from __future__ import annotations
import json, time
from uuid import uuid4
from collections.abc import Iterator
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.prompts import cargar_prompt
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services.llm import ClienteLLM, ProveedorNoDisponible, ResultadoLLM
from app.services.metrics import registrar, resumen
from app.api.admin import router as admin_router

app = FastAPI(title="Asistente Académico UNIANDES", version="2.0.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Registrar el router administrativo RAG
app.include_router(admin_router)

INJECTION_MARKERS = ("ignore previous", "ignora las instrucciones", "system prompt", "revela tu prompt", "actúa como")
DOMAIN_WORDS = ("titul", "matr", "práct", "pract", "vincul", "homolog", "certific", "académ", "uniandes", "modalidad")
DOMAIN_WORDS += ('secretar', 'normativ', 'trámit', 'tramit', 'requisito')

def obtener_llm(config: Settings = Depends(get_settings)) -> ClienteLLM:
    return ClienteLLM(config)

def respuesta_local(pregunta: str) -> RespuestaAsistente | None:
    normalizada = pregunta.lower()
    if any(marker in normalizada for marker in INJECTION_MARKERS):
        return RespuestaAsistente(
            respuesta="No puedo seguir instrucciones que alteren el rol del asistente. Puedo orientar únicamente sobre trámites académicos.",
            estado="rechazo",
            requiere_revision_humana=True,
            tiempo_segundos=0,
        )
    if not any(word in normalizada for word in DOMAIN_WORDS):
        return RespuestaAsistente(
            respuesta="Esta consulta está fuera del ámbito de orientación académica de UNIANDES. Para trámites, titulación o normativa, reformula tu pregunta.",
            estado="rechazo",
            requiere_revision_humana=True,
            tiempo_segundos=0,
        )
    return None

def responder(payload: ConsultaChat, llm: ClienteLLM) -> RespuestaAsistente:
    request_id = str(uuid4())
    inicio = time.perf_counter()
    segura = respuesta_local(payload.pregunta)
    if segura:
        registrar('consulta', request_id=request_id, estado=segura.estado, segundos=0, preferido=payload.modelo_preferido, status=200)
        return segura
    contexto = {k: v for k, v in payload.model_dump(exclude={'pregunta', 'modelo_preferido'}, exclude_none=True).items() if v.strip()}
    try:
        resultado: ResultadoLLM = llm.generar_texto(cargar_prompt(), payload.pregunta, payload.modelo_preferido, request_id=request_id, contexto=contexto)
    except ProveedorNoDisponible as error:
        registrar('consulta', request_id=request_id, estado='error', status=503, error='no_disponible', preferido=payload.modelo_preferido, segundos=round(time.perf_counter() - inicio, 3))
        raise HTTPException(status_code=503, detail=str(error)) from error
    registrar('consulta', request_id=request_id, estado='abstencion', status=200, modelo=resultado.modelo, fallback=resultado.fallback, preferido=payload.modelo_preferido, segundos=round(time.perf_counter() - inicio, 3))
    return RespuestaAsistente(
        respuesta=resultado.texto,
        estado="abstencion",
        requiere_revision_humana=True,
        fuentes=[],
        modelo_utilizado=resultado.modelo,
        fallback_activado=resultado.fallback,
        tiempo_segundos=round(time.perf_counter() - inicio, 3),
    )

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "titulacion-rag-api", "version": "2.0.0"}

@app.exception_handler(RequestValidationError)
async def error_validacion(request, exc):
    if request.url.path.startswith('/api/chat'):
        registrar('consulta', request_id=str(uuid4()), estado='validacion', status=422, error='entrada_invalida', segundos=0)
    return JSONResponse(status_code=422, content={'detail': 'Revisa la pregunta (3–2000 caracteres) y los campos de contexto.'})

@app.get('/api/metricas')
def metricas() -> dict:
    return resumen()

@app.post("/api/chat", response_model=RespuestaAsistente)
def chat(payload: ConsultaChat, llm: ClienteLLM = Depends(obtener_llm)) -> RespuestaAsistente:
    return responder(payload, llm)

@app.post("/api/chat/stream")
def chat_stream(payload: ConsultaChat, llm: ClienteLLM = Depends(obtener_llm)) -> StreamingResponse:
    respuesta = responder(payload, llm)
    def eventos() -> Iterator[str]:
        for parte in respuesta.respuesta.split(" "):
            yield f"event: token\ndata: {json.dumps({'texto': parte + ' '}, ensure_ascii=False)}\n\n"
        yield f"event: done\ndata: {respuesta.model_dump_json()}\n\n"
    return StreamingResponse(eventos(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
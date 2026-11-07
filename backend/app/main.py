from __future__ import annotations
from collections.abc import Iterator
import json
from uuid import uuid4
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from app.admin_routes import file_response
from app.admin_routes import router as admin_router
from app.config import Settings, get_settings
from app.flujo import orientar
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services import admin_store as store, rag
from app.services.llm import ClienteLLM
from app.services.metrics import registrar, resumen
from app.rate_limit import limite_chat

app = FastAPI(title="Asistente Académico UNIANDES", version="2.0.0")

app.include_router(admin_router)
from app.tool_routes import agente_router
from app.tool_routes import router as tool_router

app.include_router(tool_router)
app.include_router(agente_router)


@app.middleware("http")
async def proteger_admin(request, call_next):
  if request.method == 'POST' and request.url.path in ('/api/chat', '/api/chat/stream', '/api/agente'):
    espera = limite_chat.admitir()
    if espera is not None:
      return JSONResponse(status_code=429, content={'detail':'Se alcanzó el límite temporal de consultas. Intenta de nuevo más tarde.'},
                          headers={'Retry-After':str(espera), 'Cache-Control':'no-store'})
  if request.url.path.startswith("/api/admin"):
    try:
      if (
          int(request.headers.get("content-length", "0"))
          > rag.MAX_BYTES + 131072
      ):
        return JSONResponse(
            status_code=413, content={"detail": "La carga excede 10 MB."}
        )
    except ValueError:
      return JSONResponse(
          status_code=400, content={"detail": "Cabecera de tamaño inválida."}
      )
  response = await call_next(request)
  if request.url.path.startswith("/api/admin"):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
  return response


settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=['Retry-After'],
)


def obtener_llm(config: Settings = Depends(get_settings)) -> ClienteLLM:
  return ClienteLLM(config)


def responder(payload: ConsultaChat, llm: ClienteLLM) -> RespuestaAsistente:
  return orientar(payload, llm)


@app.get("/health")
def health(config: Settings = Depends(get_settings)) -> dict[str, str]:
  return {
      "status": "ok",
      "service": "titulacion-rag-api",
      "version": "2.0.0",
      "revision": config.app_revision,
  }


@app.get('/ready')
def ready():
  """Comprueba el índice elegible local; no consume API ni certifica el proveedor."""
  with store.db() as conn:
    config = store.get(conn, 'config', 'rag')
    count = sum(d.get('chunks', 0) for d in store.all_records(conn, 'document')
                if rag.eligible(d) and d.get('indexed_revision') == d['revision']
                and d.get('index_signature') == rag.signature(config))
  if not count:
    raise HTTPException(503, 'No hay fuentes elegibles con índice actualizado')
  return {'status':'ready', 'fragmentos_elegibles':count, 'estrategia':config['strategy'], 'proveedor_verificado':False}


@app.exception_handler(RequestValidationError)
async def error_validacion(request, exc):
  if request.url.path.startswith(("/api/chat", "/api/agente")):
    registrar(
        "consulta",
        request_id=str(uuid4()),
        estado="validacion",
        status=422,
        error="entrada_invalida",
        segundos=0,
    )
  return JSONResponse(
      status_code=422,
      content={"detail": "Revisa los campos enviados y sus límites de tamaño."},
  )


@app.get("/api/sources/{doc_id}/{revision}")
def source(doc_id: str, revision: int):
  with store.db() as conn:
    doc = store.get(conn, "document", doc_id)
  if not doc or not rag.eligible(doc) or doc["revision"] != revision:
    raise HTTPException(404, "La revisión no está activa o vigente.")
  return file_response(doc)


@app.get("/api/metricas")
def metricas(response: Response) -> dict:
  response.headers['Cache-Control'] = 'no-store'
  return resumen()


@app.post(
    "/api/agente",
    response_model=RespuestaAsistente,
    tags=["Agente educativo"],
)
@app.post("/api/chat", response_model=RespuestaAsistente)
def chat(
    payload: ConsultaChat, llm: ClienteLLM = Depends(obtener_llm)
) -> RespuestaAsistente:
  return responder(payload, llm)


@app.post("/api/chat/stream")
def chat_stream(
    payload: ConsultaChat, llm: ClienteLLM = Depends(obtener_llm)
) -> StreamingResponse:
  respuesta = responder(payload, llm)

  def eventos() -> Iterator[str]:
    for parte in respuesta.respuesta.split(" "):
      yield (
          "event: token\ndata:"
          f" {json.dumps({'texto': parte + ' '}, ensure_ascii=False)}\n\n"
      )
    yield f"event: done\ndata: {respuesta.model_dump_json()}\n\n"

  return StreamingResponse(
      eventos(),
      media_type="text/event-stream",
      headers={
          "Cache-Control": "no-cache",
          "X-Accel-Buffering": "no",
      },
  )

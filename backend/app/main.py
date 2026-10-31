from __future__ import annotations
import json
from uuid import uuid4
from collections.abc import Iterator
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services.llm import ClienteLLM
from app.services.metrics import registrar, resumen
from app.admin_routes import router as admin_router, file_response
from app.services import admin_store as store, rag
from app.services.chat_flow import generar_respuesta

app = FastAPI(title="Asistente Académico UNIANDES", version="2.0.0")
app.include_router(admin_router)

@app.middleware('http')
async def proteger_admin(request, call_next):
    if request.url.path.startswith('/api/admin'):
        try:
            if int(request.headers.get('content-length', '0')) > rag.MAX_BYTES + 131072:
                return JSONResponse(status_code=413, content={'detail': 'La carga excede 10 MB.'})
        except ValueError:
            return JSONResponse(status_code=400, content={'detail': 'Cabecera de tamaño inválida.'})
    response = await call_next(request)
    if request.url.path.startswith('/api/admin'):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

def obtener_llm(config: Settings = Depends(get_settings)) -> ClienteLLM:
    return ClienteLLM(config)

def responder(payload: ConsultaChat, llm: ClienteLLM) -> RespuestaAsistente:
    return generar_respuesta(payload, llm)[0]

@app.get

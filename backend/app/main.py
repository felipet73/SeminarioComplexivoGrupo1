"""API mínima de Semana 1 y preparación de MVP para Semana 2."""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (la clave reside solo en el backend)
load_dotenv()

app = FastAPI(title="Asistente Académico UNIANDES — API", version="0.1.0")

# Esquemas de entrada y salida para el frontend
class ChatRequest(BaseModel):
    pregunta: str

class ChatResponse(BaseModel):
    respuesta: str
    fuente: str
    tiempo_segundos: float

@app.get("/health", tags=["operación"])
def health() -> dict[str, str]:
    """Verificación de vida; no afirma conectividad con LLM o vector store."""
    return {"status": "ok", "service": "titulacion-rag-api", "version": "0.1.0"}

@app.post("/api/chat", response_model=ChatResponse, tags=["asistente"])
def chat_endpoint(payload: ChatRequest):
    """
    Endpoint del MVP: procesa la consulta con la clave cargada desde entorno.
    Cumple con el requerimiento de mantener las credenciales fuera del frontend.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Error de configuración: API Key no encontrada en variables de entorno (.env)."
        )
    
    # Respuesta estructurada para pruebas iniciales del frontend
    return ChatResponse(
        respuesta=(
            f"[Orientador Académico UNIANDES]: Su consulta '{payload.pregunta}' ha sido recibida. "
            "El sistema responderá basado exclusivamente en el reglamento oficial."
        ),
        fuente="Reglamento de Régimen Académico UNIANDES",
        tiempo_segundos=0.35
    )

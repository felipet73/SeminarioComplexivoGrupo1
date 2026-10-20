"""API mínima de Semana 1; RAG y herramientas se implementarán en fases posteriores."""
from fastapi import FastAPI

app = FastAPI(title="Asistente Académico UNIANDES — API", version="0.1.0")

@app.get("/health", tags=["operación"])
def health() -> dict[str, str]:
    """Verificación de vida; no afirma conectividad con LLM o vector store."""
    return {"status": "ok", "service": "titulacion-rag-api", "version": "0.1.0"}

"""Pruebas de endpoints para FastAPI."""
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Valida el endpoint de salud."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_endpoint_sin_api_key():
    """Valida que falle controladamente si no hay API key en el entorno."""
    # Asegurar que no haya claves en la prueba
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)
    
    response = client.post("/api/chat", json={"pregunta": "¿Cuándo son las matrículas?"})
    assert response.status_code == 500
    assert "API Key" in response.json()["detail"]

def test_chat_endpoint_con_api_key():
    """Valida la estructura de respuesta cuando la API key está presente."""
    os.environ["GEMINI_API_KEY"] = "test_key_dummy"
    
    response = client.post("/api/chat", json={"pregunta": "¿Cuándo son las matrículas?"})
    assert response.status_code == 200
    data = response.json()
    assert "respuesta" in data
    assert "fuente" in data
    assert "tiempo_segundos" in data
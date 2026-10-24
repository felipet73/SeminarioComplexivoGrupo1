from fastapi.testclient import TestClient
from app.main import app

def test_health_is_ok():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "titulacion-rag-api", "version": "2.0.0"}

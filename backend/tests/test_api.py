from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_login_fallido_admin():
  # El único acceso administrativo es el que utiliza el panel, con guardia CSRF.
  response = client.post(
      "/api/admin/login",
      json={"username": "hacker", "password": "badpassword"},
  )
  assert response.status_code == 403
  assert client.post('/admin/recargar-reglamentos').status_code == 404

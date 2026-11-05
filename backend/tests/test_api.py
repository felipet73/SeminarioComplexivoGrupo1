from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
  response = client.get("/health")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"


def test_login_fallido_admin():
  # Prueba de seguridad: Un intento de login con credenciales erróneas debe ser bloqueado (400 o 422)
  response = client.post(
      "/admin/login",
      data={"username": "hacker", "password": "badpassword"},
  )
  assert response.status_code in [400, 422]
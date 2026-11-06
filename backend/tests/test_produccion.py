"""Contrato Vercel/Cloud Run sin credenciales ni peticiones de producción."""
import pytest
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from app import admin_auth, admin_routes
from app.config import Settings
from app.main import app

FRONTEND = 'https://seminario-complexivo-grupo1.vercel.app'
BACKEND = 'https://titulacion-rag-386902880383.us-central1.run.app'


@pytest.fixture
def proxy_client(monkeypatch):
    config = Settings(_env_file=None, cors_origins=FRONTEND+'/', admin_password='solo-prueba-proxy',
                      admin_cookie_secure=True, gemini_api_key=None, openai_api_key=None)
    monkeypatch.setattr(admin_auth, 'get_settings', lambda: config)
    monkeypatch.setattr(admin_routes, 'get_settings', lambda: config)
    middleware = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    monkeypatch.setitem(middleware.kwargs, 'allow_origins', config.origins)
    monkeypatch.setattr(app, 'middleware_stack', None)
    with TestClient(app, base_url=BACKEND) as client:
        yield client


def test_login_tras_proxy_frontend_y_host_backend_diferentes(proxy_client):
    headers = {'Origin': FRONTEND, 'X-Admin-Request':'1'}
    response = proxy_client.post('/api/admin/login', headers=headers,
                                 json={'username':'admin','password':'solo-prueba-proxy'})
    assert response.status_code == 200, response.text
    cookie = response.headers['set-cookie'].lower()
    assert all(flag in cookie for flag in ('secure', 'httponly', 'samesite=strict', 'path=/api/admin'))
    assert 'domain=' not in cookie  # La respuesta proxificada pertenece al host Vercel.
    assert proxy_client.get('/api/admin/session').status_code == 200
    assert proxy_client.post('/api/admin/logout', headers=headers, json={}).status_code == 200
    assert proxy_client.get('/api/admin/session').status_code == 401


@pytest.mark.parametrize('origin', [
    'https://intruso.example', FRONTEND+'.intruso.example', FRONTEND+'@intruso.example',
    FRONTEND+'/ruta', FRONTEND+'?query=1', 'null', 'https://[malformado',
])
def test_proxy_rechaza_origen_no_exacto_y_forwarded_host_falso(proxy_client, origin):
    response = proxy_client.post('/api/admin/login', headers={'Origin':origin, 'X-Admin-Request':'1',
                                  'X-Forwarded-Host':'seminario-complexivo-grupo1.vercel.app'},
                                 json={'username':'admin','password':'solo-prueba-proxy'})
    assert response.status_code == 403
    assert not response.headers.get('set-cookie')


def test_proxy_sigue_exigiendo_cabecera_csrf(proxy_client):
    assert proxy_client.post('/api/admin/login', headers={'Origin':FRONTEND},
                             json={'username':'admin','password':'solo-prueba-proxy'}).status_code == 403


def test_cors_publico_admite_frontend_sin_habilitar_cookies_cruzadas(proxy_client):
    response = proxy_client.options('/api/chat/stream', headers={'Origin':FRONTEND,
        'Access-Control-Request-Method':'POST', 'Access-Control-Request-Headers':'content-type'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == FRONTEND
    assert 'access-control-allow-credentials' not in response.headers
    assert proxy_client.options('/api/chat/stream', headers={'Origin':'https://intruso.example',
        'Access-Control-Request-Method':'POST'}).status_code == 400


def test_cors_comodin_no_autoriza_administracion(monkeypatch):
    config = Settings(_env_file=None, cors_origins='*', admin_password='solo-prueba-proxy')
    monkeypatch.setattr(admin_auth, 'get_settings', lambda: config)
    with TestClient(app, base_url=BACKEND) as client:
        assert client.post('/api/admin/login', headers={'Origin':FRONTEND,'X-Admin-Request':'1'},
                           json={'username':'admin','password':'solo-prueba-proxy'}).status_code == 403

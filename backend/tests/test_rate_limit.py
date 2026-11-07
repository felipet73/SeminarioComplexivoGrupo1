import pytest
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware
from app import main
from app.config import Settings, get_settings
from app.rate_limit import LimiteConsultas


def test_ventana_se_recupera_sin_que_rechazos_alarguen_bloqueo():
    ahora = [0.0]
    limite = LimiteConsultas(2, 60, reloj=lambda: ahora[0])
    assert limite.admitir() is None
    ahora[0] = 10
    assert limite.admitir() is None
    ahora[0] = 59.1
    assert limite.admitir() == 1
    ahora[0] = 60
    assert limite.admitir() is None


def test_aliases_comparten_limite_antes_de_llamar_modelo_y_con_cors(monkeypatch):
    cors = next(m for m in main.app.user_middleware if m.cls is CORSMiddleware)
    monkeypatch.setitem(cors.kwargs, 'allow_origins', ['http://localhost:5173'])
    monkeypatch.setattr(main.app, 'middleware_stack', None)
    monkeypatch.setattr(main, 'limite_chat', LimiteConsultas(2, 60))
    def no_llm(*args):
        raise AssertionError('No debe llegar al proveedor')
    monkeypatch.setattr(main, 'responder', no_llm)
    with TestClient(main.app) as client:
        # La validación fallida también consume presupuesto; sin SDK ni claves.
        assert client.post('/api/chat', json={}).status_code == 422
        assert client.post('/api/chat/stream', json={}).status_code == 422
        r = client.post('/api/agente', json={}, headers={'Origin':'http://localhost:5173'})
        assert r.status_code == 429
        assert int(r.headers['retry-after']) > 0
        assert r.headers['access-control-allow-origin'] == 'http://localhost:5173'
        assert 'Retry-After' in r.headers['access-control-expose-headers']
        assert client.get('/health').status_code == 200
        assert client.options('/api/chat', headers={'Origin':'http://localhost:5173',
               'Access-Control-Request-Method':'POST'}).status_code == 200


def test_health_identifica_revision_sin_exponer_configuracion():
    config = Settings(_env_file=None, app_revision='commit-de-prueba', gemini_api_key=None)
    main.app.dependency_overrides[get_settings] = lambda: config
    try:
        response = TestClient(main.app).get('/health')
        assert response.json()['revision'] == 'commit-de-prueba'
        assert set(response.json()) == {'status','service','version','revision'}
    finally:
        main.app.dependency_overrides.pop(get_settings, None)


@pytest.mark.parametrize('cantidad,ventana', [(0,60), (True,60), (1,0)])
def test_parametros_invalidos_fallan(cantidad, ventana):
    with pytest.raises(ValueError):
        LimiteConsultas(cantidad, ventana)

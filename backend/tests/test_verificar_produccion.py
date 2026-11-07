"""El preflight correcto no basta para declarar sano un chat que devuelve 500."""
import importlib.util
import io
import json
from pathlib import Path
from urllib.parse import urlsplit
import httpx
import pytest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from app.main import app
from app.services import rag

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('verificacion_produccion', ROOT / 'scripts/verificar_produccion.py')
verificacion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verificacion)
FRONT = 'https://frontend.example'
BACK = 'https://backend.example'


class RespuestaURL(io.BytesIO):
    def __init__(self, response):
        super().__init__(response.content)
        self.status = response.status_code
        self.headers = response.headers


@pytest.fixture
def despliegue_simulado(fuente_indexada, monkeypatch):
    middleware = next(m for m in app.user_middleware if m.cls is CORSMiddleware)
    monkeypatch.setitem(middleware.kwargs, 'allow_origins', [FRONT])
    monkeypatch.setattr(app, 'middleware_stack', None)

    def sin_recuperacion(*args, **kwargs):
        raise AssertionError('El smoke debe rechazar antes de buscar o consumir un modelo')
    monkeypatch.setattr(rag, 'retrieve', sin_recuperacion)
    mode = {'chat': 'normal'}
    with TestClient(app) as client:
        def conectar(request, timeout):
            url = urlsplit(request.full_url)
            assert url.netloc in ('frontend.example', 'backend.example')
            if url.netloc == 'frontend.example' and url.path in ('/', '/admin', '/metricas'):
                response = httpx.Response(200, text='<html></html>', headers={'Content-Type':'text/html'})
            elif request.get_method() == 'POST' and url.path == '/api/chat/stream' and mode['chat'] != 'normal':
                response = (httpx.Response(500, text='Internal Server Error') if mode['chat'] == '500'
                            else httpx.Response(200, text='event: token\ndata: {"texto":"Hola"}\n\n',
                                                headers={'Content-Type':'text/event-stream'}))
            else:
                response = client.request(request.get_method(), url.path, headers=dict(request.header_items()), content=request.data)
            return RespuestaURL(response)
        monkeypatch.setattr(verificacion, 'urlopen', conectar)
        yield mode


def test_comprueba_ready_proxy_y_chat_sse_sin_modelos(despliegue_simulado):
    report = verificacion.verificar(FRONT, BACK, chat_smoke=True)
    assert report['correctos'] == report['total'] == 10


@pytest.mark.parametrize('fallo', ['500', 'truncado'])
def test_cors_correcto_con_chat_roto_no_aprueba(despliegue_simulado, fallo):
    despliegue_simulado['chat'] = fallo
    report = verificacion.verificar(FRONT, BACK, chat_smoke=True)
    rows = {row['comprobacion']: row for row in report['comprobaciones']}
    assert rows['cors_publico']['cumple'] is True
    assert rows['backend_health']['cumple'] is True
    assert rows['chat_directo']['cumple'] is False
    assert rows['chat_proxy']['cumple'] is False
    assert report['correctos'] == 8 and report['total'] == 10


def test_lee_respuesta_citada_sse_mayor_de_8k_con_citas(monkeypatch):
    final = dict(estado='respuesta', respuesta='Normativa ' * 1000, modelo_utilizado='modelo-de-prueba',
                 fuentes=[dict(titulo='Norma', seccion='Artículo 26', fragmento_id='f1')])
    body = 'event: token\ndata: {"texto":"Normativa"}\n\nevent: done\ndata: '+json.dumps(final)+'\n\n'
    monkeypatch.setattr(verificacion, 'urlopen', lambda *a, **kw: RespuestaURL(
        httpx.Response(200, text=body, headers={'Content-Type':'text/event-stream'})))
    row = verificacion.consultar(BACK+'/api/chat/stream', method='POST', payload={'pregunta':'Consulta normativa'})
    assert row['sse_valido'] is True
    assert row['json'] == final

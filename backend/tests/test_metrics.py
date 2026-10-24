import json
from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app, obtener_llm
from app.config import Settings
from app.services import metrics
from app.services.llm import ClienteLLM, SalidaProveedor, ResultadoLLM, GeminiProvider, OpenAIProvider

def test_fallback_contexto_y_tokens_reales(monkeypatch):
    def fallar(*args):
        error = RuntimeError('mensaje con una clave que no debe guardarse')
        error.status_code = 401
        raise error
    recibidos = []
    def responder(self, prompt, mensaje):
        recibidos.append(json.loads(mensaje))
        return SalidaProveedor('Respuesta', 12, 7, 19)
    monkeypatch.setattr(GeminiProvider, 'generar', fallar)
    monkeypatch.setattr(OpenAIProvider, 'generar', responder)
    llm = ClienteLLM(Settings(_env_file=None, gemini_api_key='fake', openai_api_key='fake', llm_retries=0))
    r = llm.generar_texto('rol', 'Mi titulación', contexto={'carrera':'Software'}, request_id='test')
    assert r.fallback is True
    assert recibidos[0]['contexto_declarado'] == {'carrera':'Software'}
    resumen = metrics.resumen()
    assert resumen['llamadas'] == 2
    assert resumen['errores'] == 1
    assert resumen['tokens_total'] == 19
    assert resumen['por_error'] == {'autenticacion':1}
    assert 'mensaje con una clave' not in metrics.LOG_PATH.read_text()
    assert 'Software' not in metrics.LOG_PATH.read_text()

def test_openai_primero_y_gemini_como_respaldo(monkeypatch):
    orden = []
    def fallo(*args):
        orden.append('openai')
        raise RuntimeError('fallo')
    def ok(*args):
        orden.append('gemini')
        return SalidaProveedor('Respuesta', 3, 4, 7)
    monkeypatch.setattr(OpenAIProvider, 'generar', fallo)
    monkeypatch.setattr(GeminiProvider, 'generar', ok)
    r = ClienteLLM(Settings(_env_file=None, gemini_api_key='fake', openai_api_key='fake')).generar_texto('rol', 'consulta', 'openai')
    assert orden == ['openai','gemini']
    assert r.fallback

def test_contexto_llega_desde_endpoint_y_metricas_publicas():
    recibidos = []
    def generar(*args, **kwargs):
        recibidos.append(kwargs['contexto'])
        return ResultadoLLM('Consulta Secretaría', 'doble', False, .1)
    app.dependency_overrides[obtener_llm] = lambda: SimpleNamespace(generar_texto=generar)
    try:
        client = TestClient(app)
        r = client.post('/api/chat', json={'pregunta':'Duda sobre titulación','carrera':'Software','curso':'Octavo nivel','objetivo':'Preparar preguntas'})
        assert r.status_code == 200
        assert recibidos[0]['curso'] == 'Octavo nivel'
        assert client.post('/api/chat',json={'pregunta':'x'}).status_code == 422
        metricas = client.get('/api/metricas')
        assert metricas.status_code == 200
        assert metricas.json()['consultas'] == 2
        assert metricas.json()['tipos_respuesta'] == {'abstencion':1, 'validacion':1}
        assert 'Software' not in metricas.text
    finally:
        app.dependency_overrides.clear()

def test_evento_no_guarda_campos_fuera_de_allowlist():
    metrics.registrar('consulta', pregunta='privado', api_key='privado', estado='rechazo', segundos=0)
    texto = metrics.LOG_PATH.read_text()
    assert 'privado' not in texto
    assert metrics.resumen()['consultas'] == 1

def test_reintento_contabiliza_cada_intento_sin_repetir_consultas(monkeypatch):
    intentos = []
    def generar(*args):
        intentos.append(1)
        if len(intentos) == 1:
            error = RuntimeError('límite')
            error.status_code = 429
            raise error
        return SalidaProveedor('OK', 4, 2, 6)
    monkeypatch.setattr(GeminiProvider, 'generar', generar)
    monkeypatch.setattr('app.services.llm.time.sleep', lambda _: None)
    llm = ClienteLLM(Settings(_env_file=None, gemini_api_key='fake', openai_api_key=None, llm_retries=1))
    r = llm.generar_texto('rol', 'mi titulación')
    assert r.fallback is False
    datos = metrics.resumen()
    assert datos['llamadas'] == 2
    assert datos['tokens_total'] == 6
    assert datos['por_error'] == {'cuota_o_limite': 1}

def test_503_pasa_al_respaldo_sin_reintentos_con_configuracion_actual(monkeypatch):
    orden = []
    def falla(*args):
        orden.append('gemini')
        error = RuntimeError('no disponible')
        error.status_code = 503
        raise error
    def responde(*args):
        orden.append('openai')
        return SalidaProveedor('Orientación', 3, 5, 8)
    def no_esperar(*args):
        raise AssertionError('No debe haber espera de reintento')
    monkeypatch.setattr(GeminiProvider, 'generar', falla)
    monkeypatch.setattr(OpenAIProvider, 'generar', responde)
    monkeypatch.setattr('app.services.llm.time.sleep', no_esperar)
    cliente = ClienteLLM(Settings(_env_file=None, gemini_api_key='fake', openai_api_key='fake'))
    resultado = cliente.generar_texto('rol', 'consulta de titulación')
    assert orden == ['gemini', 'openai']
    assert resultado.fallback is True
    assert metrics.resumen()['llamadas'] == 2

from app.config import Settings
from app.services.llm import ClienteLLM, ProveedorNoDisponible

def test_sin_claves_no_intenta_red():
    client = ClienteLLM(Settings(gemini_api_key=None, openai_api_key=None))
    try:
        client.generar_texto("rol", "consulta de titulación")
    except ProveedorNoDisponible as error:
        assert "GEMINI_API_KEY" in str(error)
    else:
        raise AssertionError("Se esperaba un fallo controlado")

def test_la_pregunta_larga_se_bloquea_antes_del_proveedor():
    client = ClienteLLM(Settings(gemini_api_key="fake", llm_max_input_chars=3))
    try:
        client.generar_texto("rol", "mucho texto")
    except ValueError:
        pass
    else:
        raise AssertionError("Se esperaba validación de longitud")


def test_intervalo_evaluacion_cubre_vueltas_y_reintentos(monkeypatch):
    from app.services import llm
    reloj = [0.0]
    llamadas = []
    esperas = []
    monkeypatch.setattr(llm.time, 'monotonic', lambda: reloj[0])

    def dormir(segundos):
        esperas.append(segundos)
        reloj[0] += segundos

    monkeypatch.setattr(llm.time, 'sleep', dormir)
    monkeypatch.setattr(llm.random, 'uniform', lambda *args: 0)

    class Cuota(Exception):
        status_code = 429

    class Proveedor:
        def generar(self, *args):
            llamadas.append(reloj[0])
            if len(llamadas) == 1:
                raise Cuota()
            return llm.SalidaProveedor('respuesta')

    cliente = ClienteLLM(Settings(llm_retries=1), min_interval_seconds=6)
    monkeypatch.setattr(cliente, '_proveedores', lambda preferido: [(Proveedor(), 'modelo-prueba', False)])
    cliente.generar_texto('rol', 'primera vuelta', permitir_fallback=False)
    cliente.generar_texto('rol', 'segunda vuelta', permitir_fallback=False)
    assert llamadas == [0, 6, 12]
    assert sum(esperas) == 12


def test_cliente_normal_no_introduce_esperas(monkeypatch):
    from app.services import llm
    monkeypatch.setattr(llm.time, 'sleep', lambda _: (_ for _ in ()).throw(AssertionError('Espera inesperada')))
    cliente = ClienteLLM(Settings())
    cliente._esperar_turno()
    cliente._esperar_turno()

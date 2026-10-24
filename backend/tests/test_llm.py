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

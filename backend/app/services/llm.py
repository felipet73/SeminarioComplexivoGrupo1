"""Clientes con uso real reportado por SDK, reintentos y trazas sin datos personales."""
from __future__ import annotations
import random
import json
import time
from dataclasses import dataclass
from app.config import Settings
from app.services.metrics import registrar

class ProveedorNoDisponible(Exception):
    def __init__(self,message,category='no_disponible',status=None):
        super().__init__(message)
        self.category,self.status=category,status

@dataclass(frozen=True)
class SalidaProveedor:
    texto: str
    tokens_entrada: int | None = None
    tokens_salida: int | None = None
    tokens_total: int | None = None

@dataclass(frozen=True)
class ResultadoLLM:
    texto: str
    modelo: str
    fallback: bool
    segundos: float
    tokens_entrada: int | None = None
    tokens_salida: int | None = None
    tokens_total: int | None = None

class GeminiProvider:
    def __init__(self, key: str, model: str, timeout: float = 15):
        self.key, self.model, self.timeout = key, model, timeout

    def generar(self, system_prompt: str, user_prompt: str) -> SalidaProveedor:
        from google import genai
        from google.genai import types
        with genai.Client(api_key=self.key, http_options=types.HttpOptions(timeout=int(self.timeout * 1000), retry_options=types.HttpRetryOptions(attempts=1))) as client:
            r = client.models.generate_content(model=self.model, contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_prompt, max_output_tokens=1200))
        u = r.usage_metadata
        return SalidaProveedor((r.text or '').strip(), getattr(u, 'prompt_token_count', None),
            getattr(u, 'candidates_token_count', None), getattr(u, 'total_token_count', None))

class OpenAIProvider:
    def __init__(self, key: str, model: str, timeout: float = 15):
        self.key, self.model, self.timeout = key, model, timeout

    def generar(self, system_prompt: str, user_prompt: str) -> SalidaProveedor:
        from openai import OpenAI
        with OpenAI(api_key=self.key, timeout=self.timeout, max_retries=0) as client:
            r = client.responses.create(model=self.model, instructions=system_prompt, input=user_prompt,
                                        max_output_tokens=1200, store=False)
        u = r.usage
        return SalidaProveedor(r.output_text.strip(), getattr(u, 'input_tokens', None),
                               getattr(u, 'output_tokens', None), getattr(u, 'total_tokens', None))

def clasificar_error(error: Exception) -> tuple[str, int | None]:
    status = getattr(error, 'status_code', None) or getattr(error, 'code', None)
    status = status if isinstance(status, int) else None
    if status in (401, 403): return 'autenticacion', status
    if status == 429: return 'cuota_o_limite', status
    if status == 404: return 'modelo_no_disponible', status
    if 'timeout' in type(error).__name__.lower(): return 'timeout', status
    if status and status >= 500: return 'proveedor', status
    return 'salida_o_conexion', status

class ClienteLLM:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _proveedores(self, preferido: str):
        s = self.settings
        disponibles = {}
        if s.gemini_api_key:
            disponibles['gemini'] = (GeminiProvider(s.gemini_api_key, s.ai_model, s.llm_timeout_seconds), s.ai_model)
        if s.openai_api_key:
            disponibles['openai'] = (OpenAIProvider(s.openai_api_key, s.fallback_model, s.llm_timeout_seconds), s.fallback_model)
        orden = [preferido, 'openai' if preferido == 'gemini' else 'gemini']
        return [(disponibles[n][0], disponibles[n][1], i > 0) for i, n in enumerate(orden) if n in disponibles]

    def generar_texto(self, system_prompt: str, pregunta: str, preferido: str = 'gemini', request_id: str | None = None, contexto: dict | None = None, permitir_fallback: bool = True) -> ResultadoLLM:
        if len(pregunta) > self.settings.llm_max_input_chars:
            raise ValueError('La consulta supera el límite permitido.')
        mensaje = json.dumps({'consulta': pregunta, 'contexto_declarado': contexto or {}}, ensure_ascii=False)
        inicio = time.perf_counter()
        last_category,last_status='no_disponible',None
        providers = self._proveedores(preferido)
        if not permitir_fallback:
            providers = [p for p in providers if not p[2]]
        if not providers:
            registrar('configuracion', request_id=request_id, preferido=preferido, error='sin_configuracion', segundos=0)
            raise ProveedorNoDisponible('Configura GEMINI_API_KEY u OPENAI_API_KEY en el backend.','sin_configuracion')
        for provider, model, fallback in providers:
            for intento in range(self.settings.llm_retries + 1):
                intento_inicio = time.perf_counter()
                try:
                    r = provider.generar(system_prompt, mensaje)
                    if not r.texto:
                        raise ValueError('Respuesta vacía')
                except Exception as error:
                    categoria, status = clasificar_error(error)
                    last_category,last_status=categoria,status
                    registrar('llm', request_id=request_id, modelo=model, preferido=preferido, fallback=fallback,
                              intento=intento + 1, error=categoria, status=status,
                              segundos=round(time.perf_counter() - intento_inicio, 3))
                    if categoria not in ('cuota_o_limite', 'timeout', 'proveedor') or intento == self.settings.llm_retries:
                        break
                    time.sleep(2 ** intento + random.uniform(0, .25))
                else:
                    registrar('llm', request_id=request_id, modelo=model, preferido=preferido, fallback=fallback,
                              intento=intento + 1, segundos=round(time.perf_counter() - intento_inicio, 3),
                              tokens_entrada=r.tokens_entrada, tokens_salida=r.tokens_salida, tokens_total=r.tokens_total)
                    return ResultadoLLM(r.texto, model, fallback, round(time.perf_counter() - inicio, 3), r.tokens_entrada, r.tokens_salida, r.tokens_total)
        raise ProveedorNoDisponible('El servicio de IA no está disponible. Intenta nuevamente en unos minutos.',last_category,last_status)

"""Telemetría local: eventos acotados y sin preguntas, claves ni datos académicos."""
import json
import logging
import math
from collections import Counter, deque
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from threading import Lock

LOG_PATH = Path(__file__).resolve().parents[3] / 'logs' / 'metrics.jsonl'
LOCK = Lock()

def registrar(evento: str, **datos) -> None:
    # Allowlist: nunca aceptar texto libre procedente del usuario o del SDK.
    permitidos = {'request_id', 'modelo', 'preferido', 'fallback', 'segundos', 'estado',
                 'error', 'status', 'intento', 'tokens_entrada', 'tokens_salida', 'tokens_total'}
    registro = {'fecha': datetime.now(timezone.utc).isoformat(), 'evento': evento,
                **{k: v for k, v in datos.items() if k in permitidos}}
    try:
        with LOCK:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(LOG_PATH, maxBytes=5_000_000, backupCount=3, encoding='utf-8')
            try:
                handler.emit(logging.makeLogRecord({'msg': json.dumps(registro, ensure_ascii=False)}))
            finally:
                handler.close()
    except OSError:
        logging.getLogger(__name__).warning('No se pudo escribir la telemetría local')

def resumen() -> dict:
    registros = deque(maxlen=2000)
    with LOCK:
        for archivo in [LOG_PATH.with_name(LOG_PATH.name + f'.{i}') for i in (3, 2, 1)] + [LOG_PATH]:
            if not archivo.exists():
                continue
            with archivo.open(encoding='utf-8') as stream:
                for linea in stream:
                    try:
                        registros.append(json.loads(linea))
                    except (ValueError, TypeError):
                        continue
    solicitudes = [r for r in registros if r.get('evento') == 'consulta']
    llamadas = [r for r in registros if r.get('evento') == 'llm']
    tiempos = sorted(r.get('segundos', 0) for r in solicitudes)
    return {
        'ventana': 'Últimos 2000 eventos retenidos (no representa todo el histórico)',
        'consultas': len(solicitudes), 'llamadas': len(llamadas),
        'errores': sum(r.get('error') is not None for r in llamadas),
        'fallbacks': sum(bool(r.get('fallback')) for r in solicitudes),
        'latencia_media': round(sum(tiempos) / len(tiempos), 3) if tiempos else 0,
        'latencia_p95': tiempos[max(0, math.ceil(len(tiempos) * .95) - 1)] if tiempos else 0,
        'tokens_entrada': sum(r.get('tokens_entrada') or 0 for r in llamadas),
        'tokens_salida': sum(r.get('tokens_salida') or 0 for r in llamadas),
        'tokens_total': sum(r.get('tokens_total') or 0 for r in llamadas),
        'sin_uso_reportado': sum(r.get('tokens_total') is None for r in llamadas),
        'tipos_respuesta': dict(Counter(r.get('estado', 'error') for r in solicitudes)),
        'por_modelo': dict(Counter(r.get('modelo', 'desconocido') for r in llamadas)),
        'por_error': dict(Counter(r['error'] for r in llamadas if r.get('error'))),
        'recientes': list(reversed(list(registros)[-50:])),
    }

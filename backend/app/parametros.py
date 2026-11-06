"""Parámetros compartidos por herramientas, agente y embeddings."""
import json
from pathlib import Path

PARAMETROS = json.loads(
    (Path(__file__).resolve().parents[2] / 'config/parametros.yaml').read_text(encoding='utf-8')
)
RAG_DEFAULTS = PARAMETROS['rag']


def similitud_para_modelo(modelo):
    return PARAMETROS['similitud_por_modelo'][modelo]


for campo in ('min_similarity', 'min_lexical_coverage'):
    if not 0 <= RAG_DEFAULTS[campo] <= 1:
        raise ValueError(f'Umbral inválido en config/parametros.yaml: {campo}')
for campo in ('acierto_top_k', 'silencio', 'acierto_cita', 'abstencion_o_rechazo'):
    if not 0 <= PARAMETROS['evaluacion'][campo] <= 1:
        raise ValueError(f'Criterio de evaluación fuera de rango: {campo}')
for campo in ('min_casos', 'min_negativos'):
    if type(PARAMETROS['evaluacion'][campo]) is not int or PARAMETROS['evaluacion'][campo] < 1:
        raise ValueError(f'Tamaño de muestra inválido: {campo}')
if not 1 <= PARAMETROS['max_iteraciones'] <= 10 or PARAMETROS['rrf_k'] <= 0:
    raise ValueError('El agente y RRF requieren límites positivos')

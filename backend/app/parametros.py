"""Parámetros compartidos por herramientas, agente y embeddings."""
import json
from pathlib import Path

PARAMETROS = json.loads(
    (Path(__file__).resolve().parents[2] / 'config/parametros.yaml').read_text(encoding='utf-8')
)

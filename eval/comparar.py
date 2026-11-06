"""Comparación real BM25/híbrido sobre el mismo corpus. Requiere clave para embeddings."""
import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'eval'))
from ingest import ingest
from evaluar import evaluar, cumple_umbrales, leer_casos
from app.services import admin_store as store


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--embedding-model', choices=['gemini-embedding-001', 'text-embedding-3-small'], default='gemini-embedding-001')
    parser.add_argument('--output', type=Path, default=ROOT / 'eval/results-comparacion.json')
    args = parser.parse_args()
    cases = leer_casos(ROOT / 'eval/preguntas.jsonl')
    reports = {}
    for strategy in ('lexical', 'hybrid'):
        store.DATA_DIR = ROOT / 'data' / ('eval-' + strategy)
        try:
            ingest(strategy=strategy, embedding_model=args.embedding_model)
            report = evaluar(cases)
        except Exception as error:
            # Una ingesta fallida no produce una métrica de recuperación inventada.
            report = {'modo':'no_evaluado', 'errores':1, 'error':type(error).__name__}
        reports[strategy] = report
        print(strategy, 'acierto', report.get('acierto_top_k', 'no medido'), 'silencio', report.get('silencio', 'no medido'))
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')
    sys.exit(0 if all(not r.get('errores') and cumple_umbrales(r) for r in reports.values()) else 1)

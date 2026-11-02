"""Comparación real BM25/híbrido sobre el mismo corpus. Requiere clave para embeddings."""
import json
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'eval'))
from ingest import ingest
from evaluar import evaluar
from app.services import admin_store as store


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--embedding-model', choices=['gemini-embedding-001', 'text-embedding-3-small'], default='gemini-embedding-001')
    args = parser.parse_args()
    cases = [json.loads(line) for line in (ROOT / 'eval/preguntas.jsonl').read_text(encoding='utf-8').splitlines() if line]
    reports = {}
    for strategy in ('lexical', 'hybrid'):
        store.DATA_DIR = ROOT / 'data' / ('eval-' + strategy)
        ingest(strategy=strategy, embedding_model=args.embedding_model)
        report = evaluar(cases)
        reports[strategy] = report
        print(strategy, 'acierto', report['acierto_top_k'], 'silencio', report['silencio'])
    output = ROOT / 'eval/results-comparacion.json'
    output.write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding='utf-8')
    sys.exit(0 if all(r['acierto_top_k'] >= .7 and r['silencio'] >= .9 for r in reports.values()) else 1)

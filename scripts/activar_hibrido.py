"""Activa el índice medido en el panel local reutilizando caché; falla antes de mutar si falta un vector."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.services import admin_store as store, rag
from app.parametros import PARAMETROS


def activar():
    report = json.loads((ROOT / 'eval/results-comparacion.json').read_text(encoding='utf-8'))['hybrid']
    if report.get('errores', 0) or report['acierto_top_k'] < PARAMETROS['evaluacion']['acierto_top_k'] or report['silencio'] < PARAMETROS['evaluacion']['silencio']:
        raise ValueError('La comparación no supera los umbrales de aceptación')
    config = report['config']
    with sqlite3.connect(ROOT / 'data/eval-hybrid/admin.sqlite3') as source:
        cache = {r[0]: json.loads(r[1]) for r in source.execute("SELECT id,payload FROM records WHERE kind='embedding_cache'")}
    with store.db() as conn:
        old = store.get(conn, 'config', 'rag')
        docs = [d for d in store.all_records(conn, 'document') if rag.eligible(d)]
    for doc in docs:
        for chunk in rag.split_document(doc, config):
            key = rag.embedding_cache_key(config['embedding_model'], 'RETRIEVAL_DOCUMENT', chunk['text'])
            if key not in cache or len(cache[key]) != 768:
                raise ValueError('Falta un vector medido para ' + doc['title'] + '; no se cambió la configuración')
    updated = old | {k: config[k] for k in ('strategy', 'embedding_model', 'min_similarity', 'chunk_size', 'overlap')}
    with store.db() as conn:
        for key, vector in cache.items():
            store.put(conn, 'embedding_cache', key, vector)
        if updated != old:
            updated['revision'] = old['revision'] + 1
            store.put(conn, 'config', 'rag', updated)
            store.audit(conn, 'cli', 'activar_hibrido_validado', 'rag', old, updated)
    for doc in docs:
        rag.index_document(doc['id'], 'cli')
    print(f"Índice local híbrido activo: {len(docs)} fuentes; modelo {updated['embedding_model']}. No se solicitaron embeddings nuevos.")


if __name__ == '__main__':
    activar()

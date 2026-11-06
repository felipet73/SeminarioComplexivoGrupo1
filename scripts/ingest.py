"""Ingesta reproducible con el mismo indexador del panel; ejecutar desde la raíz."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.admin_schemas import DocMeta
from app.services import admin_store as store, rag
from app.parametros import similitud_para_modelo


def cargar_fuentes(manifest=None):
    """Valida todos los originales y OCR sin modificar el índice."""
    manifest = Path(manifest or ROOT / 'data/raw/manifest.json').resolve()
    entries = json.loads(manifest.read_text(encoding='utf-8'))['documents']
    policies = json.loads((ROOT / 'config/fuentes.yaml').read_text(encoding='utf-8'))['documents']
    # Validar el manifiesto entero antes de modificar documentos.
    sources = []
    for entry in entries:
        path = (manifest.parent / entry['file']).resolve()
        if not path.is_relative_to(manifest.parent):
            raise ValueError('Archivo fuera del directorio del corpus')
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != entry['sha256']:
            raise ValueError(f'Hash incorrecto: {path.name}')
        if entry['file'] not in policies:
            raise ValueError(f'Falta política de vigencia en config/fuentes.yaml: {path.name}')
        pages = None
        if entry.get('ocr_file'):
            ocr_path = (manifest.parent / entry['ocr_file']).resolve()
            if not ocr_path.is_relative_to(manifest.parent):
                raise ValueError('OCR fuera del directorio del corpus')
            ocr_bytes = ocr_path.read_bytes()
            if hashlib.sha256(ocr_bytes).hexdigest() != entry['ocr_sha256']:
                raise ValueError('Hash OCR incorrecto')
            ocr = json.loads(ocr_bytes)
            if ocr['original_sha256'] != entry['sha256']:
                raise ValueError('OCR asociado a otro original')
            pages = rag.validar_ocr(content, ocr['pages'])
        sources.append((path, content, DocMeta(**(entry['metadata'] | policies[entry['file']])).model_dump(mode='json'), pages))
    return sources


def ingest(manifest=None, strategy=None, embedding_model=None):
    sources = cargar_fuentes(manifest)
    if strategy or embedding_model:
        with store.db() as conn:
            config = store.get(conn, 'config', 'rag')
            updated = dict(config)
            if strategy:
                updated['strategy'] = strategy
            if embedding_model:
                updated['embedding_model'] = embedding_model
                updated['min_similarity'] = similitud_para_modelo(embedding_model)
            if updated != config:
                store.put(conn, 'config', 'rag', dict(updated, revision=config['revision'] + 1))
    all_chunks = []
    for path, content, meta, pages in sources:
        with store.db() as conn:
            existing = next((d for d in store.all_records(conn, 'document')
                             if d['sha256'] == hashlib.sha256(content).hexdigest()
                             and all(d.get(k) == v for k, v in meta.items())
                             and (pages is None or d.get('pages') == pages)), None)
        doc = existing or rag.save_document(path.name, content, meta, 'ingest', ocr_pages=pages)
        if doc.get('indexed_revision') == doc['revision'] and doc.get('index_signature') == rag.signature(store.settings()):
            with store.db() as conn:
                chunks = [dict(row) for row in conn.execute('SELECT id,doc_id,revision,title,section,page,text FROM chunks WHERE doc_id=?', (doc['id'],))]
        else:
            chunks = rag.index_document(doc['id'], 'ingest')['chunks']
        all_chunks.extend(dict(c, sha256=doc['sha256']) for c in chunks)
        print(f'{path.name}: {len(chunks)} fragmentos')
    output = ROOT / 'data/processed/fragmentos.jsonl'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in all_chunks), encoding='utf-8')
    return all_chunks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strategy', choices=['lexical', 'hybrid'])
    parser.add_argument('--data-dir', type=Path, help='Estado SQLite aislado; no altera el panel local')
    parser.add_argument('--embedding-model', choices=['gemini-embedding-001', 'text-embedding-3-small'])
    args = parser.parse_args()
    if args.data_dir:
        store.DATA_DIR = args.data_dir.resolve()
    ingest(strategy=args.strategy, embedding_model=args.embedding_model)

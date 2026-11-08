"""Importación explícita SQLite→PostgreSQL vacío; DSN solo en RAG_DATABASE_URL.

Usar una copia de seguridad fuera de línea. No sobrescribe una base con datos.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'backend'))
from app.services import admin_store as store


def migrate(source_dir, report_path):
    source_dir = Path(source_dir).resolve()
    source_file = source_dir/'admin.sqlite3'
    if not source_file.is_file() or source_file.is_symlink():
        raise ValueError('Se necesita una copia SQLite regular con sus archivos files/')
    target = os.environ.get('RAG_DATABASE_URL')
    if not target:
        raise ValueError('Configura RAG_DATABASE_URL como variable privada del proceso')
    # Hash de la copia de origen, calculado antes de modificar el destino.
    source_sha256 = hashlib.sha256(source_file.read_bytes()).hexdigest()
    snapshot = sqlite3.connect(':memory:')
    snapshot.row_factory = sqlite3.Row
    source = sqlite3.connect(source_file.as_uri()+'?mode=ro', uri=True)
    try:
        source.backup(snapshot)
    finally:
        source.close()
    previous = store.DATABASE_URL
    store.DATABASE_URL = target
    try:
        records = snapshot.execute('SELECT kind,id,payload FROM records').fetchall()
        chunks = snapshot.execute('SELECT id,doc_id,revision,title,section,page,text,vector,embedding_model FROM chunks').fetchall()
        audits = snapshot.execute('SELECT id,date,actor,action,resource,before_json,after_json FROM audit').fetchall()
        files = []
        for path in (source_dir/'files').rglob('*'):
            if path.is_symlink() or not path.resolve().is_relative_to(source_dir):
                raise ValueError('No se importan enlaces ni rutas externas')
            if path.is_file():
                files.append((path.relative_to(source_dir).as_posix(),path.read_bytes()))
        blobs = dict(files)
        for row in records:
            if row['kind'] == 'document':
                doc = json.loads(row['payload'])
                if doc['path'] not in blobs or hashlib.sha256(blobs[doc['path']]).hexdigest() != doc['sha256']:
                    raise ValueError('La copia no incluye un documento íntegro; no se ha importado')
        with store.db() as conn:
            occupied = conn.execute("SELECT COUNT(*) FROM records WHERE kind NOT IN ('prompt','config')").fetchone()[0]
            occupied += conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]
            occupied += conn.execute('SELECT COUNT(*) FROM source_blobs').fetchone()[0]
            occupied += conn.execute('SELECT COUNT(*) FROM audit').fetchone()[0]
            prompts = store.all_records(conn,'prompt')
            expected = {int(p.stem.removeprefix('system_v')):p.read_text(encoding='utf-8')
                        for p in store.PROMPT_DIR.glob('system_v[0-9]*.md')}
            default_prompts = (set(expected) == {p['version'] for p in prompts}
                               and all(p['revision']==1 and p['content']==expected[p['version']] for p in prompts))
            config = store.get(conn,'config','rag')
            occupied += conn.execute("SELECT COUNT(*) FROM records WHERE kind='config' AND id<>'rag'").fetchone()[0]
            if occupied or not default_prompts or config != store.DEFAULTS:
                raise ValueError('La base de destino contiene datos o configuración editada; no se sobrescribe')
            for row in records:
                store.put(conn,row['kind'],row['id'],json.loads(row['payload']))
            for row in chunks:
                conn.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?)',tuple(row))
            conn.execute('INSERT INTO chunk_search(id,title,section,text) SELECT id,title,section,text FROM chunks')
            for row in audits:
                conn.execute('INSERT INTO audit(id,date,actor,action,resource,before_json,after_json) VALUES(?,?,?,?,?,?,?)',tuple(row))
            conn.execute("SELECT setval(pg_get_serial_sequence('audit','id'), COALESCE((SELECT MAX(id) FROM audit),1), EXISTS(SELECT 1 FROM audit))")
            for relative, content in files:
                store.write_blob(conn,relative,content)
        report = {'fecha_utc':datetime.now(timezone.utc).isoformat(), 'resultado':'aprobado',
                  'registros':len(records), 'fragmentos':len(chunks),'auditoria':len(audits),'archivos':len(files),
                  'sqlite_source_sha256':source_sha256,
                  'alcance':'Importación transaccional de copia SQLite y archivos; no cambia tráfico ni borra el origen. Sesiones en memoria no se migran.',
                  'credenciales_publicadas':False}
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False))
    finally:
        snapshot.close()
        store.DATABASE_URL = previous


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, default=ROOT/'tmp/migracion-postgres.json')
    args = parser.parse_args()
    try:
        migrate(args.source_dir,args.report)
    except ValueError as error:
        parser.exit(2,str(error)+'\n')

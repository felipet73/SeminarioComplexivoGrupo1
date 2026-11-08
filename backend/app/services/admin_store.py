"""Estado privado y auditoría: SQLite local o PostgreSQL optativo con originales."""
from __future__ import annotations
import json
import os
import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4
from app.parametros import RAG_DEFAULTS

DATABASE_URL = os.environ.get('RAG_DATABASE_URL', '')

DATA_DIR = Path(os.environ.get('RAG_DATA_DIR') or Path(__file__).resolve().parents[3] / 'data' / 'admin')
PROMPT_DIR = Path(__file__).resolve().parents[1] / 'prompts'
LOCK = RLock()
_ready: set[str] = set()
DEFAULTS = dict(RAG_DEFAULTS, revision=1)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def encode(value) -> str:
    return json.dumps(value, ensure_ascii=False)

def is_postgres():
    return bool(DATABASE_URL)


@contextmanager
def db():
    if is_postgres():
        from app.services.postgres_store import connect
        with LOCK, connect(DATABASE_URL) as conn:
            try:
                initialize(conn, postgres=True)
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        return
    with sqlite_db() as conn:
        yield conn


@contextmanager
def sqlite_db():
    with LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DATA_DIR / 'admin.sqlite3', timeout=20)
        conn.row_factory = sqlite3.Row
        try:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS records(kind TEXT, id TEXT, payload TEXT NOT NULL, PRIMARY KEY(kind,id));
                CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, date TEXT, actor TEXT, action TEXT, resource TEXT, before_json TEXT, after_json TEXT);
                CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY, doc_id TEXT, revision INTEGER, title TEXT, section TEXT, page INTEGER, text TEXT, vector TEXT, embedding_model TEXT);
                CREATE INDEX IF NOT EXISTS chunks_doc ON chunks(doc_id);
                CREATE VIRTUAL TABLE IF NOT EXISTS chunk_search USING fts5(id UNINDEXED, title, section, text, tokenize='unicode61 remove_diacritics 2');
            ''')
            initialize(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def initialize(conn, *, postgres=False):
    for path in PROMPT_DIR.glob('system_v[0-9]*.md'):
        try:
            version = int(path.stem.removeprefix('system_v'))
        except ValueError:
            continue
        descriptions={1:'Orientación básica con abstención y derivación a Secretaría.',2:'Delimita el dominio académico, solicita contexto y restringe instrucciones ajenas.',3:'Orientación contextual con criterios de evidencia y límites académicos.'}
        put(conn, 'prompt', str(version), {'version':version, 'content':path.read_text(encoding='utf-8'),
            'description':descriptions.get(version,f'Versión V{version} importada del archivo'), 'revision':1, 'updated':now()}, ignore=True)
        previous = get(conn,'prompt',version)
        content = path.read_text(encoding='utf-8')
        if not postgres and previous['content'] != content:
            updated = dict(previous,content=content,revision=previous['revision']+1,updated=now())
            put(conn,'prompt',version,updated)
            audit(conn,'filesystem','sync_prompt_file',f'prompt:{version}',previous,updated)
    put(conn, 'config', 'rag', DEFAULTS, ignore=True)
    config = get(conn, 'config', 'rag')
    if any(key not in config for key in DEFAULTS):
        put(conn, 'config', 'rag', dict(DEFAULTS, **config))
    key = hashlib.sha256(DATABASE_URL.encode()).hexdigest() if postgres else str(DATA_DIR.resolve())
    if key not in _ready:
        for job in all_records(conn, 'analysis'):
            if job['status'] in ('queued', 'running'):
                job.update(status='interrupted', error='El servidor se reinició. Ejecuta una nueva simulación.')
                put(conn, 'analysis', job['id'], job)
        _ready.add(key)

def put(conn, kind, id, value, ignore=False):
    if is_postgres():
        conflict = 'DO NOTHING' if ignore else 'DO UPDATE SET payload=EXCLUDED.payload'
        sql = 'INSERT INTO records(kind,id,payload) VALUES(?,?,?) ON CONFLICT(kind,id) '+conflict
    else:
        verb = 'INSERT OR IGNORE' if ignore else 'INSERT OR REPLACE'
        sql = f'{verb} INTO records(kind,id,payload) VALUES(?,?,?)'
    conn.execute(sql, (kind, str(id), encode(value)))

def get(conn, kind, id):
    row = conn.execute('SELECT payload FROM records WHERE kind=? AND id=?', (kind,str(id))).fetchone()
    return json.loads(row['payload']) if row else None

def all_records(conn, kind):
    return [json.loads(r['payload']) for r in conn.execute('SELECT payload FROM records WHERE kind=?', (kind,))]

def audit(conn, actor, action, resource, before, after):
    conn.execute('INSERT INTO audit(date,actor,action,resource,before_json,after_json) VALUES(?,?,?,?,?,?)',
                 (now(),actor,action,resource,encode(before),encode(after)))

def settings():
    with db() as conn:
        return get(conn,'config','rag')

def prompt(version=None):
    with db() as conn:
        version = version if version is not None else get(conn,'config','rag')['active_prompt']
        result = get(conn,'prompt',str(version))
        if not result:
            raise ValueError('Versión de prompt no encontrada')
        return result

def new_id():
    return str(uuid4())


def write_blob(conn, relative, content):
    if is_postgres():
        conn.execute('INSERT INTO source_blobs(path,content) VALUES(?,?)', (relative, content))
    else:
        target = DATA_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def read_blob(relative):
    if not is_postgres():
        raise ValueError('Solo el backend PostgreSQL almacena blobs en base de datos')
    with db() as conn:
        row = conn.execute('SELECT content FROM source_blobs WHERE path=?', (relative,)).fetchone()
    return bytes(row['content']) if row else None

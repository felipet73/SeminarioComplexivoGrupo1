"""Estado privado local y auditoría de revisiones; SQLite + originales inmutables."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4

DATA_DIR = Path(__file__).resolve().parents[3] / 'data' / 'admin'
PROMPT_DIR = Path(__file__).resolve().parents[1] / 'prompts'
LOCK = RLock()
_ready: set[str] = set()
DEFAULTS = {'active_prompt':3, 'chunk_size':1400, 'overlap':160, 'top_k':4,
            'strategy':'lexical', 'embedding_model':'gemini-embedding-001', 'min_similarity':0.65, 'revision':1}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def encode(value) -> str:
    return json.dumps(value, ensure_ascii=False)

@contextmanager
def db():
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
                if previous['content'] != content:
                    updated = dict(previous,content=content,revision=previous['revision']+1,updated=now())
                    put(conn,'prompt',version,updated)
                    audit(conn,'filesystem','sync_prompt_file',f'prompt:{version}',previous,updated)
            put(conn, 'config', 'rag', DEFAULTS, ignore=True)
            key = str(DATA_DIR.resolve())
            if key not in _ready:
                for job in all_records(conn, 'analysis'):
                    if job['status'] in ('queued', 'running'):
                        job.update(status='interrupted', error='El servidor se reinició. Ejecuta una nueva simulación.')
                        put(conn, 'analysis', job['id'], job)
                _ready.add(key)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def put(conn, kind, id, value, ignore=False):
    sql = 'INSERT OR IGNORE' if ignore else 'INSERT OR REPLACE'
    conn.execute(f'{sql} INTO records(kind,id,payload) VALUES(?,?,?)', (kind, str(id), encode(value)))

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

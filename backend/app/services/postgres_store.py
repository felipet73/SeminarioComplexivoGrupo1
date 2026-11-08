"""Adaptador PostgreSQL optativo; no cambia el backend SQLite por defecto."""
from contextlib import contextmanager

# Tipos simples para conservar los contratos JSON/SQL de la aplicación.
SCHEMA = '''
CREATE TABLE IF NOT EXISTS records(kind TEXT, id TEXT, payload TEXT NOT NULL, PRIMARY KEY(kind,id));
CREATE TABLE IF NOT EXISTS audit(id BIGSERIAL PRIMARY KEY, date TEXT, actor TEXT, action TEXT, resource TEXT, before_json TEXT, after_json TEXT);
CREATE TABLE IF NOT EXISTS chunks(rowid BIGSERIAL UNIQUE, id TEXT PRIMARY KEY, doc_id TEXT, revision INTEGER, title TEXT, section TEXT, page INTEGER, text TEXT, vector TEXT, embedding_model TEXT);
CREATE INDEX IF NOT EXISTS chunks_doc ON chunks(doc_id);
CREATE TABLE IF NOT EXISTS chunk_search(id TEXT PRIMARY KEY, title TEXT, section TEXT, text TEXT);
CREATE INDEX IF NOT EXISTS chunk_search_spanish ON chunk_search USING GIN(to_tsvector('spanish',coalesce(title,'') || ' ' || coalesce(section,'') || ' ' || coalesce(text,'')));
CREATE TABLE IF NOT EXISTS source_blobs(path TEXT PRIMARY KEY, content BYTEA NOT NULL)
'''


class StorageUnavailable(Exception):
    """Fallo operativo sin DSN ni detalle del controlador en la respuesta pública."""


class Row(dict):
    def __getitem__(self, key):
        return tuple(self.values())[key] if isinstance(key, int) else super().__getitem__(key)


class Result:
    def __init__(self, cursor):
        self.cursor = cursor

    def fetchone(self):
        value = self.cursor.fetchone()
        return Row(value) if value is not None else None

    def fetchall(self):
        return [Row(value) for value in self.cursor.fetchall()]

    def __iter__(self):
        return (Row(value) for value in self.cursor)


class Connection:
    def __init__(self, raw):
        self.raw = raw

    def execute(self, sql, params=()):
        # SQL fijo de la aplicación; datos siempre enviados como parámetros.
        if sql.startswith('INSERT INTO chunks VALUES'):
            sql = sql.replace('INSERT INTO chunks VALUES',
                              'INSERT INTO chunks(id,doc_id,revision,title,section,page,text,vector,embedding_model) VALUES', 1)
        return Result(self.raw.execute(sql.replace('?', '%s'), params))

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


@contextmanager
def connect(url):
    import psycopg
    from psycopg.rows import dict_row
    from psycopg.conninfo import conninfo_to_dict
    try:
        options = conninfo_to_dict(url)
    except (psycopg.Error, ValueError):
        raise StorageUnavailable('Configuración de almacenamiento inválida') from None
    hosts = options.get('host', '').split(',')
    local = all(h.startswith('/') or h in ('127.0.0.1', 'localhost', '::1') for h in hosts)
    addresses = options.get('hostaddr', '').split(',')
    local = local and all(a in ('', '127.0.0.1', '::1') for a in addresses)
    if not local and options.get('sslmode') != 'verify-full':
        raise ValueError('PostgreSQL remoto requiere sslmode=verify-full; Cloud SQL usa socket Unix o proxy local.')
    # No registrar DSN: puede contener contraseña. El conector de Cloud Run usa
    # socket Unix autenticado por IAM; TCP externo debe usar TLS verificado.
    tls_options = {}
    if not local and not options.get('sslrootcert'):
        # libpq no siempre usa el almacén del sistema (especialmente en Windows).
        # Mozilla CA permite verificar cadena y hostname sin un root.crt manual.
        import certifi
        tls_options['sslrootcert'] = certifi.where()
    try:
        raw = psycopg.connect(url, row_factory=dict_row, connect_timeout=10, **tls_options)
    except psycopg.Error:
        raise StorageUnavailable('Almacenamiento no disponible') from None
    try:
        raw.execute("SET LOCAL statement_timeout = '20s'")
        raw.execute("SET LOCAL lock_timeout = '10s'")
        # Serializa mutaciones entre procesos/revisiones, no solo entre hilos.
        raw.execute('SELECT pg_advisory_xact_lock(734021901)')
        for statement in SCHEMA.split(';'):
            if statement.strip():
                raw.execute(statement)
        yield Connection(raw)
    except psycopg.Error:
        raise StorageUnavailable('Almacenamiento no disponible') from None
    finally:
        raw.close()


def lexical(conn, match, doc_ids):
    placeholders = ','.join('?' for _ in doc_ids)
    document = "to_tsvector('spanish',coalesce(s.title,'') || ' ' || coalesce(s.section,'') || ' ' || coalesce(s.text,''))"
    query = f'''SELECT c.id,c.doc_id,c.revision,c.title,c.section,c.page,c.text,
        -ts_rank_cd({document},websearch_to_tsquery('spanish',?)) AS rank
        FROM chunk_search s JOIN chunks c ON c.id=s.id
        WHERE {document} @@ websearch_to_tsquery('spanish',?)
        AND c.doc_id IN ({placeholders}) ORDER BY rank,c.id LIMIT 40'''
    return [dict(row) for row in conn.execute(query, [match, match]+list(doc_ids))]

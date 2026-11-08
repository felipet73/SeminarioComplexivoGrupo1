"""Contratos del adaptador optativo; integración real en scripts/probar_postgres.py."""
from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app import admin_routes
from app.services import admin_store as store, postgres_store as pg


class Cursor:
    def __init__(self, values):
        self.values = iter(values)

    def fetchone(self):
        return next(self.values, None)

    def fetchall(self):
        return list(self.values)

    def __iter__(self):
        return self.values


class Raw:
    def __init__(self):
        self.calls = []
        self.committed = self.rolled_back = self.closed = False

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        return Cursor([{'value':1}, {'value':2}])

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


def test_adaptador_parametriza_y_conserva_acceso_por_clave_e_indice():
    raw = Raw()
    conn = pg.Connection(raw)
    payload = "Texto con ? y comillas ' que no son SQL"
    result = conn.execute('SELECT payload FROM records WHERE id=?', (payload,))
    assert raw.calls[-1] == ('SELECT payload FROM records WHERE id=%s', (payload,))
    row = result.fetchone()
    assert row['value'] == row[0] == 1
    assert result.fetchall() == [{'value':2}]
    assert result.fetchone() is None
    assert list(conn.execute('SELECT value')) == [{'value':1}, {'value':2}]
    conn.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?)', tuple(range(9)))
    assert 'chunks(id,doc_id,revision,title,section,page,text,vector,embedding_model)' in raw.calls[-1][0]
    conn.commit()
    conn.rollback()
    conn.close()
    assert raw.committed and raw.rolled_back and raw.closed


def test_conexion_tiene_lock_transaccional_y_cierra_incluso_si_falla(monkeypatch):
    import psycopg
    raw = Raw()
    monkeypatch.setattr(psycopg, 'connect', lambda *args, **kwargs: raw)
    with pytest.raises(RuntimeError):
        with pg.connect('postgresql://user@127.0.0.1/test'):
            raise RuntimeError('fallo sintético')
    assert raw.closed
    assert any('pg_advisory_xact_lock' in sql for sql, _ in raw.calls)
    assert any('statement_timeout' in sql for sql, _ in raw.calls)
    assert any('source_blobs' in sql for sql, _ in raw.calls)


def test_busqueda_postgres_no_interpela_texto_ni_documentos_en_sql():
    raw = Raw()
    conn = pg.Connection(raw)
    match = '"consulta" OR "académica"'
    ids = ["identificador'; DROP TABLE records;--"]
    rows = pg.lexical(conn, match, ids)
    sql, params = raw.calls[-1]
    assert match not in sql and ids[0] not in sql
    assert params == [match, match]+ids
    assert 'websearch_to_tsquery' in sql and 'ts_rank_cd' in sql
    assert len(rows) == 2


def test_store_postgres_confirma_y_revierte_transacciones(monkeypatch):
    raw = Raw()
    conn = pg.Connection(raw)

    @contextmanager
    def conectar(url):
        yield conn

    monkeypatch.setattr(store, 'DATABASE_URL', 'dsn-no-real')
    monkeypatch.setattr(pg, 'connect', conectar)
    monkeypatch.setattr(store, 'initialize', lambda *args, **kwargs: None)
    with store.db() as db:
        store.put(db, 'document', 'id', {'name':'prueba'})
        assert 'DO UPDATE' in raw.calls[-1][0]
        store.put(db, 'prompt', '1', {'content':'prueba'}, ignore=True)
        assert 'DO NOTHING' in raw.calls[-1][0]
        store.write_blob(db, 'files/id/1.txt', b'contenido')
    assert raw.committed
    with pytest.raises(ValueError):
        with store.db():
            raise ValueError('rollback')
    assert raw.rolled_back


def test_archivo_postgres_no_depende_de_ruta_local_y_sanitiza_nombre(monkeypatch):
    monkeypatch.setattr(store, 'DATABASE_URL', 'dsn-no-real')
    monkeypatch.setattr(store, 'read_blob', lambda path: b'fuente academica')
    response = admin_routes.file_response({'path':'files/id/1.txt', 'name':'Normativa académica.txt'})
    assert response.body == b'fuente academica'
    assert '%C3%A9' in response.headers['content-disposition']
    assert response.headers['cache-control'] == 'no-store'
    monkeypatch.setattr(store, 'read_blob', lambda path: None)
    with pytest.raises(HTTPException) as error:
        admin_routes.file_response({'path':'files/id/1.txt', 'name':'norma.txt'})
    assert error.value.status_code == 404


def test_prompt_persistido_no_se_reemplaza_por_archivo_de_imagen():
    with store.db() as conn:
        saved = store.get(conn, 'prompt', '3')
        saved.update(content='Contenido editado y persistido, diferente al archivo.', revision=2)
        store.put(conn, 'prompt', '3', saved)
        store.initialize(conn, postgres=True)
        assert store.get(conn, 'prompt', '3')['content'] == saved['content']


def test_escritura_prompt_postgres_y_lectura_blob(monkeypatch):
    monkeypatch.setattr(store, 'DATABASE_URL', 'dsn-no-real')
    original = (store.PROMPT_DIR/'system_v3.md').read_bytes()
    admin_routes.write_prompt(3, 'no debe escribir en el disco local')
    assert (store.PROMPT_DIR/'system_v3.md').read_bytes() == original

    @contextmanager
    def db():
        yield SimpleNamespace(execute=lambda *args: SimpleNamespace(fetchone=lambda: {'content':memoryview(b'contenido')}))

    monkeypatch.setattr(store, 'db', db)
    assert store.read_blob('files/id/1.txt') == b'contenido'
    monkeypatch.setattr(store, 'DATABASE_URL', '')
    with pytest.raises(ValueError):
        store.read_blob('files/id/1.txt')


@pytest.mark.parametrize('url,permitido', [
    ('postgresql://user@db.example/test', False),
    ('postgresql://user@db.example/test?sslmode=verify-full', True),
    ('postgresql://user@/test?host=/cloudsql/proyecto:region:instancia', True),
    ('dbname=test user=user service=externo', False),
])
def test_transporte_remoto_exige_verificacion_tls(monkeypatch, url, permitido):
    import psycopg
    raw = Raw()
    calls = []

    def conectar(*args, **kwargs):
        calls.append(True)
        return raw

    monkeypatch.setattr(psycopg,'connect',conectar)
    if permitido:
        with pg.connect(url):
            pass
        assert calls and raw.closed
    else:
        with pytest.raises(ValueError,match='verify-full'):
            with pg.connect(url):
                pass
        assert not calls


def test_fallo_de_conexion_no_publica_detalle_del_controlador(monkeypatch):
    import psycopg

    def falla(*args, **kwargs):
        raise psycopg.OperationalError('detalle privado de conexion de prueba')

    monkeypatch.setattr(psycopg,'connect',falla)
    with pytest.raises(pg.StorageUnavailable) as error:
        with pg.connect('postgresql://user@127.0.0.1/test'):
            pass
    assert 'detalle privado' not in str(error.value)


def test_ready_devuelve_503_seguro_si_postgres_no_esta_disponible(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app

    @contextmanager
    def falla():
        raise pg.StorageUnavailable('detalle privado de prueba')
        yield

    monkeypatch.setattr(store,'db',falla)
    response = TestClient(app).get('/ready')
    assert response.status_code == 503 and response.headers['retry-after'] == '5'
    assert 'detalle privado' not in response.text and 'almacenamiento' in response.text


def test_dsn_malformado_no_filtra_su_contenido():
    with pytest.raises(pg.StorageUnavailable) as error:
        with pg.connect('opcion_invalida=valor-privado-ficticio'):
            pass
    assert 'valor-privado' not in str(error.value)

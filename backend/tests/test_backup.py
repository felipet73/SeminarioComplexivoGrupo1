import io
import shutil
import zipfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import backup, admin_store as store


def test_respaldo_exige_autenticacion():
    assert TestClient(app).get('/api/admin/backup').status_code == 401


def test_respaldo_copia_base_y_fuentes_pero_no_entorno(fuente_indexada):
    private = store.DATA_DIR/'.env'
    private.write_text('DATO_PRIVADO=ejemplo-no-real')
    path, directory = backup.sqlite_backup()
    try:
        with zipfile.ZipFile(io.BytesIO(path.read_bytes())) as archive:
            names = archive.namelist()
            assert 'admin.sqlite3' in names
            assert any(n.startswith('files/') for n in names)
            assert '.env' not in names
        assert not (directory/'admin.sqlite3').exists()
    finally:
        shutil.rmtree(directory)


def test_respaldo_rechaza_postgres_y_exceso_de_tamano(monkeypatch, fuente_indexada):
    with pytest.raises(ValueError, match='límite'):
        backup.sqlite_backup(max_bytes=1)
    monkeypatch.setattr(store,'DATABASE_URL','dsn-no-real')
    with pytest.raises(ValueError,match='PostgreSQL'):
        backup.sqlite_backup()

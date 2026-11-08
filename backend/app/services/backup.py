"""Exportación privada SQLite para migración, sin entorno, sesiones ni credenciales."""
from pathlib import Path
import shutil
import sqlite3
import tempfile
import zipfile
from app.services import admin_store as store


def sqlite_backup(*, max_bytes=100_000_000):
    if store.is_postgres():
        raise ValueError('En PostgreSQL utiliza el respaldo administrado de la base de datos.')
    directory = Path(tempfile.mkdtemp(prefix='rag-backup-'))
    try:
        with store.LOCK:
            # Confirmar inicialización antes de abrir la conexión de backup.
            with store.db():
                pass
            snapshot = directory/'admin.sqlite3'
            source = sqlite3.connect((store.DATA_DIR/'admin.sqlite3').resolve().as_uri()+'?mode=ro', uri=True)
            target = sqlite3.connect(snapshot)
            try:
                source.backup(target)
            finally:
                source.close()
                target.close()
            files = []
            for path in (store.DATA_DIR/'files').rglob('*'):
                if path.is_symlink() or not path.resolve().is_relative_to(store.DATA_DIR.resolve()):
                    raise ValueError('El respaldo no admite enlaces ni rutas externas.')
                if path.is_file():
                    files.append(path)
            if snapshot.stat().st_size+sum(path.stat().st_size for path in files) > max_bytes:
                raise ValueError('El respaldo excede el límite de exportación web; usa una migración fuera de línea.')
            archive = directory/'respaldo-privado.zip'
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as output:
                output.write(snapshot,'admin.sqlite3')
                for path in files:
                    output.write(path,path.relative_to(store.DATA_DIR).as_posix())
        snapshot.unlink()
        return archive, directory
    except Exception:
        shutil.rmtree(directory,ignore_errors=True)
        raise

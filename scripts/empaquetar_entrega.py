"""ZIP reproducible desde archivos versionados; excluye estado privado y exige límite."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache',
                 '.ruff_cache', 'logs', 'tmp', 'test-results', 'playwright-report'}


def permitida(path):
    if EXCLUDED_DIRS.intersection(path.parts):
        return False
    if path.name.startswith('.env'):
        return path.name == '.env.example' or path.as_posix() == 'frontend/.env.production'
    return not (path.suffix.lower() in {'.key', '.pem', '.sqlite3', '.sqlite', '.db', '.zip'}
                or '.sqlite3-' in path.name or '.db-' in path.name)


def empaquetar(root, output, *, max_bytes=20_000_000, medir=False):
    root, output = Path(root).resolve(), Path(output).resolve()
    if max_bytes < 1:
        raise ValueError('El límite debe ser positivo')
    if output.exists() and not medir:
        raise ValueError('El archivo de salida ya existe; elige otro nombre')
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    selected, omitted = [], []
    for name in sorted(filter(None, names)):
        rel = Path(name)
        if not permitida(rel):
            omitted.append(name)
            continue
        source = root / rel
        if source.is_symlink() or not source.resolve().is_relative_to(root):
            raise ValueError('No se empaquetan enlaces simbólicos: '+name)
        if not source.is_file():
            raise ValueError('Falta un archivo versionado: '+name)
        selected.append((rel, source))
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as f:
        temporary = Path(f.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for rel, source in selected:
                info = zipfile.ZipInfo(root.name+'/'+rel.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, source.read_bytes(), compresslevel=9)
            entries = [dict(archivo=v.filename, bytes=v.file_size, comprimidos=v.compress_size)
                       for v in archive.infolist()]
        size = temporary.stat().st_size
        valid = size <= max_bytes
        if valid and not medir:
            temporary.replace(output)
        return {'fecha_utc':datetime.now(timezone.utc).isoformat(),
                'commit':subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'working_tree_con_cambios':bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root)),
                'bytes':size, 'MiB':round(size / 1048576, 2), 'max_bytes':max_bytes,
                'cumple_limite':valid, 'zip_creado':valid and not medir,
                'archivos':len(entries), 'excluidos':omitted,
                'mayores':sorted(entries, key=lambda v:v['comprimidos'], reverse=True)[:20],
                'alcance':'Solo archivos conocidos por Git; ejecutar detector de secretos antes de entregar. No acredita historial limpio.'}
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'tmp/Titulacion_Semana4.zip')
    parser.add_argument('--report', type=Path, default=ROOT/'tmp/paquete-informe.json')
    parser.add_argument('--medir', action='store_true', help='Mide sin crear un ZIP entregable')
    args = parser.parse_args()
    report = empaquetar(ROOT, args.output, medir=args.medir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['bytes', 'MiB', 'max_bytes', 'cumple_limite', 'zip_creado']}, ensure_ascii=False))
    return 0 if report['cumple_limite'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""ZIP reproducible desde archivos versionados; excluye estado privado y exige límite."""
import argparse
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {'.terraform', '.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache',
                 '.ruff_cache', 'logs', 'tmp', 'test-results', 'playwright-report'}


def permitida(path):
    if EXCLUDED_DIRS.intersection(path.parts):
        return False
    if path.name.startswith('.env'):
        return path.name == '.env.example' or path.as_posix() == 'frontend/.env.production'
    return not (path.suffix.lower() in {'.key', '.pem', '.sqlite3', '.sqlite', '.db', '.zip', '.tfvars', '.tfstate', '.tfplan'}
                or ('.tfvars' in path.suffixes and path.suffix != '.example') or '.tfstate' in path.suffixes or '.sqlite3-' in path.name or '.db-' in path.name)


def evidencia_publica(root, source, revision):
    """Solo incorpora el reporte explícito de 35 casos del mismo checkout limpio."""
    current = subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if revision != current:
        raise ValueError('La evidencia debe corresponder al SHA del checkout')
    for args in (['git','diff','--quiet'],['git','diff','--cached','--quiet']):
        if subprocess.run(args,cwd=root).returncode:
            raise ValueError('Se requiere checkout sin cambios versionados para incorporar evidencia')
    source = Path(source)
    if source.is_symlink() or source.stat().st_size > 1_000_000:
        raise ValueError('Reporte inválido o demasiado grande')
    content = source.read_bytes()
    data = json.loads(content)
    expected = {c['id'] for c in json.loads((root/'eval/casos_http.json').read_text())}
    cases = data.get('casos', [])
    if (data.get('revision_esperada') != revision or data.get('correctos') != 35
            or data.get('total') != 35 or len(cases) != 35 or len(expected) != 35
            or {c['id'] for c in cases} != expected or data.get('omitidos') != []
            or data.get('incluye_modelo') is not True or data.get('solo_backend') is not False
            or any(c.get('ok') is not True for c in cases)
            or not any(c.get('revision_obtenida') == revision for c in cases)):
        raise ValueError('Se requieren los 35 casos completos aprobados con SHA obtenido coincidente')
    name = Path(f'docs/evidencias/semana-4/produccion-despliegue-{revision}.json')
    metadata = {'revision':revision,'casos':35,'archivo':name.as_posix(),
                'sha256':hashlib.sha256(content).hexdigest(),
                'alcance':'Reporte del mismo despliegue incluido al empaquetar, sin crear otro commit ni atribuirlo a otra revisión.'}
    return name,content,metadata


def empaquetar(root, output, *, max_bytes=20_000_000, medir=False, production_report=None, expected_revision=None):
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
    extra = None
    evidence = None
    if production_report is not None:
        extra_name,extra_content,evidence = evidencia_publica(root,production_report,expected_revision)
        if extra_name in {rel for rel,_ in selected}:
            raise ValueError('El nombre del reporte ya está versionado; no se sobrescribe')
        extra = (extra_name,extra_content)
    output.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as f:
        temporary = Path(f.name)
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            contents = [(rel,source.read_bytes()) for rel,source in selected]
            if extra:
                contents.append(extra)
            for rel, content in sorted(contents,key=lambda entry:entry[0].as_posix()):
                info = zipfile.ZipInfo(root.name+'/'+rel.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, content, compresslevel=9)
            entries = [dict(archivo=v.filename, bytes=v.file_size, comprimidos=v.compress_size)
                       for v in archive.infolist()]
        size = temporary.stat().st_size
        archive_hash = hashlib.sha256(temporary.read_bytes()).hexdigest()
        valid = size <= max_bytes
        if valid and not medir:
            temporary.replace(output)
        return {'fecha_utc':datetime.now(timezone.utc).isoformat(),
                'commit':subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
                'working_tree_con_cambios':bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root)),
                'zip_sha256':archive_hash, 'evidencia_produccion':evidence,
                'bytes':size, 'MiB':round(size / 1048576, 2), 'max_bytes':max_bytes,
                'cumple_limite':valid, 'zip_creado':valid and not medir,
                'archivos':len(entries), 'excluidos':omitted,
                'mayores':sorted(entries, key=lambda v:v['comprimidos'], reverse=True)[:20],
                'alcance':'Archivos conocidos por Git y, si se solicita, reporte público validado del mismo SHA; ejecutar detector de secretos antes de entregar. No acredita historial limpio.'}
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'tmp/Titulacion_Semana4.zip')
    parser.add_argument('--report', type=Path, default=ROOT/'tmp/paquete-informe.json')
    parser.add_argument('--medir', action='store_true', help='Mide sin crear un ZIP entregable')
    parser.add_argument('--evidencia-produccion', type=Path, help='JSON completo del mismo despliegue; exige checkout limpio y SHA')
    parser.add_argument('--expected-revision', help='SHA del checkout y del reporte público')
    args = parser.parse_args()
    report = empaquetar(ROOT, args.output, medir=args.medir, production_report=args.evidencia_produccion, expected_revision=args.expected_revision)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['bytes', 'MiB', 'max_bytes', 'cumple_limite', 'zip_creado']}, ensure_ascii=False))
    return 0 if report['cumple_limite'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

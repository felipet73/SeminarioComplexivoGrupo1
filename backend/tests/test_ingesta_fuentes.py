"""La integridad debe funcionar también desde un checkout limpio en Linux."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path
import pytest
from app.services import admin_store

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ingesta_fuentes', ROOT / 'scripts/ingest.py')
ingesta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingesta)


def test_corpus_versionado_integro_sin_aprobar_ocr():
    sources = ingesta.cargar_fuentes()
    assert len(sources) == 6
    scanned = next(source for source in sources if source[3] is not None)
    assert len(scanned[3]) == 29
    assert scanned[2]['approved'] is False
    assert not admin_store.DATA_DIR.exists()


@pytest.fixture
def manifest_ocr(tmp_path):
    raw = ROOT / 'data/raw'
    entry = next(e for e in json.loads((raw / 'manifest.json').read_text('utf-8'))['documents'] if e.get('ocr_file'))
    for field in ('file', 'ocr_file'):
        shutil.copyfile(raw / entry[field], tmp_path / entry[field])
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'documents': [entry]}), encoding='utf-8')
    return manifest, entry


def test_ocr_alterado_aborta_antes_de_crear_indice(manifest_ocr):
    manifest, entry = manifest_ocr
    with (manifest.parent / entry['ocr_file']).open('ab') as output:
        output.write(b' ')
    with pytest.raises(ValueError, match='Hash OCR incorrecto'):
        ingesta.ingest(manifest)
    assert not admin_store.DATA_DIR.exists()


def test_ocr_de_otro_original_se_rechaza_aunque_su_hash_coincida(manifest_ocr):
    manifest, entry = manifest_ocr
    ocr = manifest.parent / entry['ocr_file']
    data = json.loads(ocr.read_text('utf-8'))
    data['original_sha256'] = '0' * 64
    ocr.write_bytes(json.dumps(data).encode('utf-8'))
    entry['ocr_sha256'] = hashlib.sha256(ocr.read_bytes()).hexdigest()
    manifest.write_text(json.dumps({'documents': [entry]}), encoding='utf-8')
    with pytest.raises(ValueError, match='OCR asociado a otro original'):
        ingesta.ingest(manifest)
    assert not admin_store.DATA_DIR.exists()

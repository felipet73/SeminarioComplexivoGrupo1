"""Regresiones del evaluador: errores y corpus vacío nunca aprueban."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('evaluador', ROOT / 'eval/evaluar.py')
evaluador = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluador)


def casos():
    return [dict(id='p', pregunta='titulación', documento='Normativa de prueba', seccion='Artículo 1'),
            dict(id='n', pregunta='bitcoin', documento=None, seccion=None)]


def test_corpus_vacio_no_aprueba():
    report = evaluador.evaluar(casos())
    assert report['acierto_top_k'] == 0 and report['silencio'] == 1
    assert not evaluador.cumple_umbrales(report)


def test_error_de_busqueda_no_cuenta_como_silencio(monkeypatch):
    def falla(*args):
        raise RuntimeError('índice roto')
    monkeypatch.setattr(evaluador.rag, 'retrieve', falla)
    report = evaluador.evaluar(casos())
    assert report['errores'] == 2 and report['silencio'] == 0
    assert not evaluador.cumple_umbrales(report)


def test_mismo_articulo_de_otro_documento_no_es_acierto(fuente_indexada, monkeypatch):
    chunk = dict(fuente_indexada, title='Otra norma', sha256='prueba')
    monkeypatch.setattr(evaluador.rag, 'retrieve', lambda q: {'chunks': [chunk] if q == 'titulación' else []})
    assert evaluador.evaluar(casos())['acierto_top_k'] == 0


def test_cli_devuelve_uno_si_no_cumple_y_escribe_resultados(tmp_path):
    output = tmp_path / 'resultado.json'
    result = subprocess.run([sys.executable, str(ROOT / 'eval/evaluar.py'), '--data-dir', str(tmp_path / 'vacio'),
                             '--output', str(output)], capture_output=True, text=True)
    assert result.returncode == 1, result.stderr
    assert json.loads(output.read_text(encoding='utf-8'))['acierto_top_k'] == 0


def test_cli_falla_si_falta_dataset_y_comparador_importa(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / 'eval/evaluar.py'), '--cases', str(tmp_path / 'falta')], capture_output=True)
    assert result.returncode == 2
    result = subprocess.run([sys.executable, str(ROOT / 'eval/comparar.py'), '--help'], capture_output=True)
    assert result.returncode == 0, result.stderr


def test_dataset_rechaza_ids_duplicados(tmp_path):
    cases = [dict(id=str(i), pregunta='titulación', documento='Norma', seccion='Artículo 1') for i in range(16)]
    cases += [dict(id='duplicado', pregunta='fuera', documento=None, seccion=None)] * 4
    path = tmp_path / 'casos.jsonl'
    path.write_text('\n'.join(json.dumps(c) for c in cases), encoding='utf-8')
    with pytest.raises(ValueError, match='duplicados'):
        evaluador.leer_casos(path)

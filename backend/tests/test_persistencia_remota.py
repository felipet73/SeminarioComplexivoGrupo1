"""El comparador no acredita persistencia con capturas vacías o diferentes."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('persistencia_remota', Path(__file__).resolve().parents[2]/'scripts/verificar_persistencia_remota.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def snapshots():
    before = {'url':'https://app.example','revision_cloud_run_declarada':'servicio-01',
              'documents':[{'id':'doc','revision':2,'archivo_sha256':'hash','fragmentos_muestra_sha256':'indice'}],
              'prompts_sha256':'prompt','config_sha256':'config'}
    after = deepcopy(before)
    after['revision_cloud_run_declarada'] = 'servicio-02'
    return before,after


def test_compara_estado_preservado_con_revisiones_diferentes():
    before,after = snapshots()
    assert module.compare(before,after)['resultado'] == 'aprobado'


@pytest.mark.parametrize('field', ['documents','prompts_sha256','config_sha256'])
def test_detecta_perdidas_o_cambios_de_estado(field):
    before,after = snapshots()
    after[field] = [] if field == 'documents' else 'modificado'
    report = module.compare(before,after)
    assert report['resultado'] == 'diferencias' and not report['comprobaciones'][field]


@pytest.mark.parametrize('case',['vacio','mismo_servicio_revision','otro_servicio'])
def test_rechaza_evidencia_insuficiente(case):
    before,after = snapshots()
    if case == 'vacio':
        before['documents'] = after['documents'] = []
    elif case == 'mismo_servicio_revision':
        after['revision_cloud_run_declarada'] = before['revision_cloud_run_declarada']
    else:
        after['url'] = 'https://otro.example'
    with pytest.raises(ValueError):
        module.compare(before,after)


def test_rechaza_fallback_de_getpass_que_mostraria_la_entrada(monkeypatch):
    import warnings

    def fallback(*args, **kwargs):
        warnings.warn('No se controla el eco', module.getpass.GetPassWarning)
        raise AssertionError('No debe llegar a leer entrada con eco')

    monkeypatch.setattr(module.getpass,'getpass',fallback)
    with pytest.raises(ValueError, match='Read-Host'):
        module.read_password()


def test_lee_y_elimina_password_temporal_sin_usar_terminal(monkeypatch):
    monkeypatch.setenv('PERSISTENCE_ADMIN_PASSWORD','valor-ficticio-de-prueba')
    monkeypatch.setattr(module.getpass,'getpass',lambda *args: pytest.fail('No usar terminal'))
    assert module.read_password(True) == 'valor-ficticio-de-prueba'
    assert 'PERSISTENCE_ADMIN_PASSWORD' not in module.os.environ
    with pytest.raises(ValueError):
        module.read_password(True)

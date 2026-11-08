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

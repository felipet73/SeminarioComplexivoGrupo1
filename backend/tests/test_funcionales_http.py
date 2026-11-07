import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('funcionales_http', ROOT / 'scripts/pruebas_funcionales.py')
funcionales = importlib.util.module_from_spec(spec)
spec.loader.exec_module(funcionales)


def test_respuesta_del_articulo_correcto_en_documento_incorrecto_no_aprueba():
    case = dict(status=200, contrato='respuesta_citada', documento='Reglamento de prueba', articulo='26')
    row = dict(status=200, json={'estado':'respuesta','fuentes':[{'titulo':'Otra norma','seccion':'Artículo 26','fragmento_id':'real'}]})
    assert not funcionales.cumple(case, row, '')
    row['json']['fuentes'][0]['titulo'] = 'Reglamento de prueba'
    assert funcionales.cumple(case, row, '')
    row['json']['estado'] = 'abstencion'
    assert not funcionales.cumple(case, row, '')


def test_health_antiguo_o_revision_distinta_no_aprueba():
    case = dict(status=200, contrato='salud')
    row = dict(status=200, json={'status':'ok'})
    assert not funcionales.cumple(case, row, '', revision='nuevo')
    row['json']['revision'] = 'viejo'
    assert not funcionales.cumple(case, row, '', revision='nuevo')
    row['json']['revision'] = 'nuevo'
    assert funcionales.cumple(case, row, '', revision='nuevo')


def test_500_y_sse_truncado_no_aprueban():
    case = dict(status=200, contrato='rechazo_sse')
    assert not funcionales.cumple(case, {'status':500}, '')
    assert not funcionales.cumple(case, {'status':200,'sse_valido':False}, '')


def test_dataset_corto_o_duplicado_falla_antes_de_la_red():
    case = dict(id='duplicado',ruta='/health',status=200)
    for cases in ([case], [case]*15):
        with pytest.raises(ValueError):
            funcionales.ejecutar('', '', casos=cases)


def test_contrato_desconocido_no_se_convierte_en_aprobado():
    with pytest.raises(ValueError):
        funcionales.cumple(dict(status=200, contrato='mal-escrito'), {'status':200}, '')

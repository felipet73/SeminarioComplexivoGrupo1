"""Regresión del Art, 24 OCR: su texto no debe heredar la etiqueta Artículo 23."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from app.services import rag, admin_store as store
from app.services.chat_flow import generar_respuesta
from app.services.llm import ResultadoLLM
from app.schemas import ConsultaChat

ROOT = Path(__file__).resolve().parents[2]


def pagina_real():
    ocr = json.loads((ROOT/'data/raw/UNIANDES-Instructivo-Titulacion-2017.ocr.json').read_text())
    return next(p for p in ocr['pages'] if p['page'] == 9)


@pytest.mark.parametrize('header', ['Art, 24.-', 'Art. 24.-', 'Artículo 24.-', 'Art 24.-'])
def test_separa_encabezado_ocr_sin_heredar_articulo_anterior(header):
    doc = {'id':'ocr-test','revision':1,'title':'Prueba', 'pages':[{'page':9,'text':
           f'Art. 23.- Defensa y evaluación del estudio de caso.\n{header} Modelo de negocios. Dos fases.\nArt. 25.- Componentes.'}]}
    chunks = rag.split_document(doc,store.settings())
    actual = next(c for c in chunks if 'Dos fases' in c['text'])
    assert actual['section'] == 'Artículo 24' and actual['page'] == 9
    assert all('Dos fases' not in c['text'] for c in chunks if c['section'] == 'Artículo 23')


def test_pagina_ocr_real_del_corpus_separa_articulos_23_y_24():
    doc = {'id':'ocr-test','revision':2,'title':'Instructivo', 'pages':[pagina_real()]}
    chunks = rag.split_document(doc,store.settings())
    actual = next(c for c in chunks if 'Art, 24.-' in c['text'])
    assert actual['section'] == 'Artículo 24' and actual['page'] == 9
    assert 'Presentación del modelo de negocio ya culminado' in actual['text']
    assert all('Art, 24.-' not in c['text'] for c in chunks if c['section'] == 'Artículo 23')


def test_indexacion_recuperacion_y_fuente_publica_conservan_articulo_24():
    # Texto real, documento temporal y permisos solo en SQLite aislado del test.
    page = pagina_real()
    doc = rag.save_document('prueba-ocr.txt',page['text'].encode(),
                            dict(title='Normativa de prueba OCR',kind='normativa',source_url='',
                                 valid_from='2020-01-01',valid_to=None,approved=True,enabled=True,notes='Ensayo aislado'), 'test')
    with store.db() as conn:
        saved = store.get(conn,'document',doc['id'])
        saved['pages'] = [page]
        store.put(conn,'document',doc['id'],saved)
    rag.index_document(doc['id'],'test')
    query = '¿Cuáles son las fases del modelo de negocios para titulación?'
    found = rag.retrieve(query)['chunks']
    actual = next(c for c in found if c['section'] == 'Artículo 24')

    def respuesta(*args, **kwargs):
        assert any(c['id'] == actual['id'] and c['section'] == 'Artículo 24'
                   for c in kwargs['contexto']['evidencia'])
        return ResultadoLLM(json.dumps({'respuesta':'El artículo 24 establece presentar el perfil para aprobación y el modelo culminado.',
                                        'estado':'respuesta','fragmentos':[actual['id']]}),'modelo-simulado',False,.01)

    result,_ = generar_respuesta(ConsultaChat(pregunta=query),SimpleNamespace(generar_texto=respuesta),evidencia=found)
    assert result.estado == 'respuesta'
    assert len(result.fuentes) == 1 and result.fuentes[0].seccion == 'Artículo 24'
    assert result.fuentes[0].pagina == 9 and result.fuentes[0].fragmento_id == actual['id']

import io
import pytest
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from app.main import app
from app.services import rag


def test_ready_distingue_proceso_sano_de_corpus_no_disponible(fuente_indexada):
    client = TestClient(app)
    assert client.get('/health').status_code == 200
    assert client.get('/ready').json()['fragmentos_elegibles'] > 0
    rag.update_document(fuente_indexada['doc_id'], {'enabled':False}, 'test', 1)
    assert client.get('/health').status_code == 200
    assert client.get('/ready').status_code == 503


def test_ocr_rechaza_paginas_desordenadas_o_incompletas():
    writer = PdfWriter()
    writer.add_blank_page(width=600, height=800)
    writer.add_blank_page(width=600, height=800)
    output = io.BytesIO()
    writer.write(output)
    pages = [{'page':1,'text':'Texto académico suficientemente largo.'}, {'page':2,'text':'Página dos.'}]
    assert rag.validar_ocr(output.getvalue(), pages) == pages
    with pytest.raises(ValueError, match='páginas'):
        rag.validar_ocr(output.getvalue(), pages[:1])
    with pytest.raises(ValueError, match='desordenadas'):
        rag.validar_ocr(output.getvalue(), list(reversed(pages)))

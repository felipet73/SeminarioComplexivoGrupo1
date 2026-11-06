"""El contrato conserva las decisiones explícitas del flujo y del agente."""
import pytest
from pydantic import ValidationError
from app.schemas import RespuestaAsistente


@pytest.mark.parametrize('texto', [
    'La carrera requiere aprobar el curso de titulación.',
    'Está prohibido presentar documentos falsos.',
    'No pude verificar la fecha; consulta el artículo citado.',
])
def test_no_infiere_estado_ni_campos_por_palabras(texto):
    respuesta = RespuestaAsistente(respuesta=texto, estado='respuesta', tiempo_segundos=0.1)
    assert respuesta.estado == 'respuesta'
    assert respuesta.campos_necesarios == []


@pytest.mark.parametrize('campo', ['estado', 'tiempo_segundos'])
def test_estado_y_tiempo_son_obligatorios(campo):
    datos = dict(respuesta='Respuesta con decisión explícita.', estado='abstencion', tiempo_segundos=0)
    del datos[campo]
    with pytest.raises(ValidationError):
        RespuestaAsistente(**datos)

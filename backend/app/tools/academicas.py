"""Contratos y herramientas educativas del agente."""
import re
from datetime import date, timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from app.parametros import PARAMETROS
from app.services import rag


class BuscarIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    pregunta: str = Field(min_length=3, max_length=2000)


class RequisitosIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    modalidad: str = Field(min_length=3, max_length=120)


class ChecklistIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    perfil_estudiante: str = Field(min_length=3, max_length=500)


class PlazoIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    fecha_inicio: date
    dias_habiles: int = Field(strict=True, ge=0, le=PARAMETROS['max_dias_habiles'])


class PlazoOut(BaseModel):
    fecha_resultado: date
    dias_habiles: int
    alcance: str


class PasajeOut(BaseModel):
    fragmento_id: str
    texto: str
    seccion: str
    pagina: int


class ConsultaOut(BaseModel):
    pasajes: list[PasajeOut]
    advertencia: str


class ChecklistItem(BaseModel):
    requisito: str
    fragmento_id: str
    documento: str
    seccion: str
    pagina: int
    estado: Literal['pendiente_de_verificar'] = 'pendiente_de_verificar'


class ChecklistOut(BaseModel):
    perfil_declarado: str
    items: list[ChecklistItem]
    completo: Literal[False] = False
    advertencia: str = 'Pasajes normativos por verificar para este perfil. No acreditan cumplimiento ni exhaustividad; confirmar aplicabilidad y normativa interna.'


def construir_checklist(perfil: str, chunks: list[dict]) -> ChecklistOut:
    """Lista extractiva: cada ítem conserva una cita textual y nunca declara cumplimiento."""
    items = []
    seen = set()
    for chunk in chunks:
        if chunk.get('kind') != 'normativa':
            continue
        for sentence in re.split(r'(?<=[.;])\s+|\n\s*\n', chunk['text']):
            sentence = sentence.strip()
            if not re.search(r'requisit|deber[áaíi]|oblig|aproba|cumpl|necesari', sentence, re.I) or len(sentence) < 25 or sentence in seen:
                continue
            seen.add(sentence)
            items.append(ChecklistItem(requisito=sentence, fragmento_id=chunk['id'], documento=chunk['title'],
                                       seccion=chunk['section'], pagina=chunk['page']))
            if len(items) == 20:
                return ChecklistOut(perfil_declarado=perfil, items=items)
    return ChecklistOut(perfil_declarado=perfil, items=items)


def calcular_plazo(datos: PlazoIn) -> PlazoOut:
    actual = datos.fecha_inicio
    pendientes = datos.dias_habiles
    while pendientes:
        actual += timedelta(days=1)
        if actual.weekday() < 5:
            pendientes -= 1
    return PlazoOut(fecha_resultado=actual, dias_habiles=datos.dias_habiles, alcance=PARAMETROS['nota_calculo'])


def consultar_pasajes(query: str):
    chunks = rag.retrieve(query)['chunks']
    salida = ConsultaOut(pasajes=[{'fragmento_id': c['id'], 'texto': c['text'],
                                  'seccion': c['section'], 'pagina': c['page']} for c in chunks],
                         advertencia='Verificar aplicabilidad al perfil; no certifica aptitud ni exhaustividad.')
    return salida, chunks


def buscar_fragmentos(datos: BuscarIn):
    return consultar_pasajes(datos.pregunta)


def consultar_requisitos(datos: RequisitosIn):
    return consultar_pasajes('requisitos ' + datos.modalidad)


def generar_checklist(datos: ChecklistIn):
    _, chunks = consultar_pasajes('requisitos ' + datos.perfil_estudiante)
    return construir_checklist(datos.perfil_estudiante, chunks), chunks


def ejecutar_calculo(datos: PlazoIn):
    return calcular_plazo(datos), []



"""Contratos y herramientas educativas del agente."""
import re
import unicodedata
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
    perfil_interpretado: dict[str, str] = Field(default_factory=dict)
    datos_por_confirmar: list[str] = Field(default_factory=list)
    items: list[ChecklistItem]
    completo: Literal[False] = False
    advertencia: str = 'Pasajes normativos por verificar para este perfil. No acreditan cumplimiento ni exhaustividad; confirmar aplicabilidad y normativa interna.'


def normalizar(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto.casefold()) if not unicodedata.combining(c))


DIMENSIONES = {
    'nivel': {'grado': r'\b(grado|pregrado|tercer nivel)\b',
              'posgrado': r'\b(posgrado|postgrado|maestria|doctorado|cuarto nivel)\b'},
    'modalidad_titulacion': {'examen complexivo': r'\bcomplexivo\b',
                            'proyecto de investigacion': r'\b(proyecto de investigacion|tesis)\b'},
}


def interpretar_perfil(perfil: str) -> dict[str, str]:
    texto = normalizar(perfil)
    return {dimension: encontrados[0] for dimension, opciones in DIMENSIONES.items()
            if len(encontrados := [nombre for nombre, patron in opciones.items() if re.search(patron, texto)]) == 1}


def consulta_checklist(perfil: str) -> str:
    texto = normalizar(perfil)
    tema = 'prácticas preprofesionales' if 'practic' in texto else 'vinculación' if 'vincul' in texto else 'titulación'
    return tema + ' ' + ' '.join(interpretar_perfil(perfil).values())


def construir_checklist(perfil: str, chunks: list[dict]) -> ChecklistOut:
    """Lista extractiva: cada ítem conserva una cita textual y nunca declara cumplimiento."""
    items = []
    seen = set()
    interpretado = interpretar_perfil(perfil)
    pendientes = [dimension for dimension in DIMENSIONES if dimension not in interpretado]
    def salida():
        return ChecklistOut(perfil_declarado=perfil, perfil_interpretado=interpretado,
                            datos_por_confirmar=pendientes, items=items)
    for chunk in chunks:
        if chunk.get('kind') != 'normativa':
            continue
        for sentence in re.split(r'(?<=[.;])\s+|\n\s*\n', chunk['text']):
            sentence = sentence.strip()
            # Solo excluimos una regla cuando explicita un perfil incompatible.
            # Una regla general o comparativa requiere revisión, nunca inferimos aptitud.
            texto = normalizar(sentence)
            # Los requisitos de cargos no son requisitos del estudiante.
            if re.search(r'\b(rector|vicerrector|decano|autoridad|profesor titular)\b', texto):
                continue
            incompatible = False
            for dimension, elegido in interpretado.items():
                mencionados = {nombre for nombre, patron in DIMENSIONES[dimension].items() if re.search(patron, texto)}
                if mencionados and elegido not in mencionados:
                    incompatible = True
            if incompatible or not re.search(r'requisit|deber[ai]|oblig|aproba|cumpl|necesari', texto) or len(sentence) < PARAMETROS['checklist']['min_caracteres'] or sentence in seen:
                continue
            seen.add(sentence)
            items.append(ChecklistItem(requisito=sentence, fragmento_id=chunk['id'], documento=chunk['title'],
                                       seccion=chunk['section'], pagina=chunk['page']))
            if len(items) == PARAMETROS['checklist']['max_items']:
                return salida()
    return salida()


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
    # Evita convertir toda la descripción libre en términos léxicos obligatorios.
    _, chunks = consultar_pasajes(consulta_checklist(datos.perfil_estudiante))
    return construir_checklist(datos.perfil_estudiante, chunks), chunks


def ejecutar_calculo(datos: PlazoIn):
    return calcular_plazo(datos), []



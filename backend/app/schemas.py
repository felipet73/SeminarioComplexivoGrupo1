"""Contrato HTTP del producto. No contiene normativa ni credenciales."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, field_validator

CampoContexto = Literal['carrera','curso','modalidad','periodo','jornada','tema','objetivo','sede','modalidad_titulacion']

class CampoNecesario(BaseModel):
    campo: CampoContexto
    etiqueta: str
    tipo: Literal['texto','select']
    opciones: list[str] = Field(default_factory=list)
    max_length: int

class ConsultaChat(BaseModel):
    pregunta: str = Field(min_length=3, max_length=2000, examples=["¿Qué requisitos debo revisar para titularme?"])
    carrera: str | None = Field(default=None, max_length=120)
    modalidad: str | None = Field(default=None, max_length=120)
    modelo_preferido: Literal["gemini", "openai"] = "gemini"
    curso: str | None = Field(default=None, max_length=80)
    periodo: str | None = Field(default=None, max_length=80)
    jornada: str | None = Field(default=None, max_length=80)
    tema: str | None = Field(default=None, max_length=80)
    objetivo: str | None = Field(default=None, max_length=120)
    sede: str | None = Field(default=None, max_length=120)
    modalidad_titulacion: str | None = Field(default=None, max_length=120)

    @field_validator('carrera','curso','modalidad','periodo','jornada','tema','objetivo','sede','modalidad_titulacion')
    @classmethod
    def validar_contexto(cls, valor):
        if valor is None:
            return None
        valor=valor.strip()
        if valor and len(valor)<2:
            raise ValueError('El dato debe tener al menos dos caracteres.')
        return valor or None

class Fuente(BaseModel):
    titulo: str
    seccion: str
    url: str
    version: str | None = None
    pagina: int | None = None
    fragmento_id: str | None = None
    sha256: str | None = None

class BorradorRAG(BaseModel):
    respuesta: str = Field(min_length=1,max_length=8000)
    estado: Literal['respuesta','abstencion','aclaracion','rechazo']
    fragmentos: list[str] = Field(default_factory=list,max_length=10)
    campos_necesarios: list[CampoContexto] = Field(default_factory=list,max_length=9)

class RespuestaAsistente(BaseModel):
    respuesta: str
    estado: Literal["respuesta", "abstencion", "aclaracion", "rechazo"]
    requiere_revision_humana: bool = False
    fuentes: list[Fuente] = Field(default_factory=list)
    campos_necesarios: list[CampoNecesario] = Field(default_factory=list)
    modelo_utilizado: str | None = None
    fallback_activado: bool = False
    tiempo_segundos: float = Field(ge=0)

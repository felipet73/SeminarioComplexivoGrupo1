"""Contrato HTTP del producto. No contiene normativa ni credenciales."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

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

class Fuente(BaseModel):
    titulo: str
    seccion: str
    url: str
    version: str | None = None

class RespuestaAsistente(BaseModel):
    respuesta: str
    estado: Literal["respuesta", "abstencion", "aclaracion", "rechazo"]
    requiere_revision_humana: bool = False
    fuentes: list[Fuente] = Field(default_factory=list)
    modelo_utilizado: str | None = None
    fallback_activado: bool = False
    tiempo_segundos: float = Field(ge=0)

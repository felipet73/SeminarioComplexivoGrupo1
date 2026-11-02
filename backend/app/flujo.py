"""Flujo de orientación y resolución humana; compartido por API y evaluación."""
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services.chat_flow import generar_respuesta
from app.services.actions import DecisionIn, DecisionOut, decidir


def orientar(consulta: ConsultaChat, llm) -> RespuestaAsistente:
    return generar_respuesta(consulta, llm)[0]


def resolver(action_id: str, decision: DecisionIn) -> DecisionOut:
    return decidir(action_id, decision)

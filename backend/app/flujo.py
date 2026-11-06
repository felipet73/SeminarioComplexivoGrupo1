"""Flujo de orientación y resolución humana; compartido por API y evaluación."""
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services.actions import DecisionIn, DecisionOut, decidir
from app.services.chat_flow import generar_respuesta


def orientar(consulta: ConsultaChat, llm) -> RespuestaAsistente:
  # El flujo compartido ya valida citas, vigencia y estados sin evidencia.
  # Aclaraciones, rechazos y propuestas de confirmación no necesitan citas.
  return generar_respuesta(consulta, llm)[0]


def resolver(action_id: str, decision: DecisionIn) -> DecisionOut:
  return decidir(action_id, decision)

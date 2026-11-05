"""Flujo de orientación y resolución humana; compartido por API y evaluación."""
from app.schemas import ConsultaChat, RespuestaAsistente
from app.services.actions import DecisionIn, DecisionOut, decidir
from app.services.chat_flow import generar_respuesta


def orientar(consulta: ConsultaChat, llm) -> RespuestaAsistente:
  # Obtenemos la respuesta del generador de chat
  resultado = generar_respuesta(consulta, llm)

  # Manejo por si genera una tupla (respuesta, contexto) o directamente la respuesta
  respuesta = resultado[0] if isinstance(resultado, tuple) else resultado

  # --- VALIDACIÓN ANTI-ALUCINACIONES (RAG SEGURO) ---
  # Verificamos si la respuesta no tiene fuentes asociadas o el texto está vacío
  if hasattr(respuesta, "fuentes") and not respuesta.fuentes:
    return RespuestaAsistente(
        respuesta=(
            "Lo siento, esa consulta no se encuentra registrada en los"
            " reglamentos oficiales vigentes de UNIANDES."
        ),
        fuentes=[],
    )

  return respuesta


def resolver(action_id: str, decision: DecisionIn) -> DecisionOut:
  return decidir(action_id, decision)
# Revisión técnica de Semana 1

**Fecha:** 20-10-2026  
**Alcance:** revisión del repositorio y contraste con la consigna del Caso 01, Grupo 1. No sustituye la revisión docente ni la verificación institucional de fuentes.

## Evidencia encontrada

| Criterio de Semana 1 | Evidencia | Estado |
|---|---|---|
| Propuesta de solución | `docs/01-propuesta.md` | Disponible y ajustada al backend actual |
| Historias, criterios y requisitos no funcionales | `docs/02-requisitos.md` | Disponible |
| Arquitectura con frontend, backend, modelo, vectorial y agente | `docs/03-arquitectura.md` | Disponible como arquitectura objetivo; solo FastAPI está implementado |
| Inventario de fuentes | `docs/04-fuentes.md` y `data/raw/manifest.json` | Disponible; vigencia y descargas continúan pendientes |
| Al menos 15 preguntas frecuentes reales | `docs/05-levantamiento-15-preguntas.md` | No cumplido todavía: existen 15 preguntas propuestas, no evidencia de campo |
| Backend | `backend/app/main.py` y `backend/tests/test_health.py` | Implementado para el corte de Semana 1 |

## Mejoras prioritarias antes de cerrar la semana

1. Levantar y anonimizar al menos 15 preguntas reales mediante encuesta breve o entrevista con Secretaría; registrar fecha, método, cantidad de participantes y evidencia.
2. Completar la minuta de revisión docente en `docs/evidencias/semana-1/revision-1.md` con acuerdos, responsables y fechas reales.
3. Confirmar para cada fuente el enlace directo, versión, vigencia, aplicabilidad y responsable de la verificación antes de indexarla.
4. Mantener el alcance honesto: no afirmar que el chat, RAG, agente, frontend o base vectorial están implementados mientras no existan en el repositorio.
5. En Semana 2, definir contratos `POST /api/v1/chat` con modelos Pydantic, validación de entradas, pruebas de abstención y secretos exclusivamente en el backend.

## Verificación ejecutada

El 20-10-2026 se ejecutó `pytest -q` dentro de `backend/`: 1 prueba aprobada. El resultado verifica el contrato actual de `GET /health`; no es evidencia de RAG, citas, seguridad adversarial ni disponibilidad desplegada.

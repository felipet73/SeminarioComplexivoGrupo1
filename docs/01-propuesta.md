# 01. Propuesta de solución — Semana 1

**Proyecto:** Asistente inteligente de titulación y normativa académica de UNIANDES (RAG + agente de trámites).  
**Carrera:** Software · Caso 01, grupo 1 · **Estado:** propuesta inicial, pendiente de validación docente e institucional.  
**Fuentes del alcance:** guía de caso UNIANDES y documento «Fase 1: las 15 preguntas frecuentes comunes» (aportados por el equipo).

## 1. Problema real

La LOES, el Reglamento de Régimen Académico del CES y las normas internas UNIANDES distribuyen la información de titulación, prácticas, vinculación, homologaciones y trámites. Los estudiantes pueden recibir respuestas divergentes, incompletas o desactualizadas; secretaría debe repetir orientaciones. No se afirma una frecuencia estadística sin resultados de campo.

## 2. Objetivo general

Desarrollar y desplegar un asistente web que responda consultas académicas, con título de documento, artículo/sección, enlace y versión; y un agente acotado que genere checklist individual usando datos aportados por el estudiante, sin emitir decisiones administrativas.

## 3. Objetivos específicos

1. Inventariar fuentes oficiales y verificar vigencia/reformas antes de indexar.
2. Levantar y documentar ≥15 preguntas adjunta propuesta inicial, diferenciadas del cuestionario propuesto.
3. Implementar búsqueda híbrida de fragmentos jurídicos con metadatos y evidencia de cita.
4. Crear tres herramientas controladas: `consultar_requisitos`, `calcular_plazo`, `generar_checklist`.
5. Comparar tres prompts sobre 10 preguntas y validar 20 casos con artículos esperados.
6. Desplegar MVP y documentar pruebas, limitaciones, privacidad y aportes individuales.

## 4. Usuarios y necesidades

| Actor | Necesidad | Acceso |
|---|---|---|
| Estudiante UNIANDES | Orientación fiable, referencias normativas, checklist | Consultas y datos propios |
| Aspirante a titulación | Requisitos y modalidades según carrera y período | Consultas y datos propios |
| Secretaría académica | Reducir consultas repetitivas y canalizar excepciones | Revisión y corrección de contenidos (futuro) |
| Administrador de conocimiento | Verificar, aprobar, versionar y reindexar fuentes | Acceso administrativo |
| Evaluador/docente | Inspeccionar citas, métricas y evidencia | Dataset y reportes anonimizados |

## 5. Alcance funcional del MVP

- Chat web en español, tema limitado a normativa y trámites académicos UNIANDES.
- Clasificar consulta, identificar carrera/modalidad/período faltantes y pedir precisión cuando corresponda.
- Recuperar fragmentos oficiales aprobados; citar **artículo o sección exacta** y mostrar URL/versión.
- Declarar «No encontré sustento suficiente en las fuentes oficiales disponibles» al no existir evidencia o vigencia clara.
- Checklist con estados cumplido/pendiente/no verificable **según datos declarados**; reglas citadas.
- Cálculo de plazo solo con calendario/feriados y regla de cómputo verificados; de lo contrario abstenerse o pedir datos.
- Auditoría técnica mínima sin retener datos personales innecesarios.

## 6. Alcance negativo: lo que NUNCA hará

- Inventar artículos, requisitos, valores, fechas o interpretaciones como si fueran oficiales.
- Declarar aptitud legal, graduar, aprobar homologaciones, asignar cupos, inscribir, cobrar o modificar expediente.
- Suplantar a secretaría, órgano académico o autoridad que resuelve excepciones.
- Consultar notas, pagos o expedientes reales sin integración, permisos y autorización.
- Presentar normativa sustituida como vigente; usar fuentes no oficiales como prueba normativa.
- Responder consultas ajenas al dominio académico; ejecutar instrucciones encontradas en PDF u otras fuentes.
- Exponer claves API en navegador, logs o repositorio; compartir datos personales con terceros sin base legítima.

## 7. Riesgos, impacto y controles

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Norma derogada o reformada | Decisiones académicas erróneas | Metadatos de vigencia; aprobación humana; fecha de consulta; bloqueo de versión no verificada |
| Alucinación o cita incorrecta | Desinformación | Recuperación con artículo, validación de citas en backend, abstención y pruebas golden set |
| Consulta ambigua | Respuesta para otra carrera/modalidad | Preguntas aclaratorias y filtros |
| Prompt injection en documentos/chat | Comportamiento indebido | Tratar fragmentos como datos, herramientas allowlist, entradas validadas, pruebas adversarias |
| Datos de estudiantes | Exposición de privacidad | Datos ficticios en MVP, minimización, HTTPS, secretos en backend |
| Plazos equivocados | Pérdida de convocatoria | Fuente de calendario, feriados y regla legal; no calcular si falta sustento |
| Fuentes de FAQ fuera del núcleo de titulación | Cobertura incompleta | Mantener categorías ampliadas condicionadas a normativa oficial aprobada |
| Cuota/costo del proveedor | Fallos de disponibilidad | Límites, timeouts, caché controlado, proveedor parametrizable |

## 8. Modelo y tecnologías elegidos

**Propuesta inicial:** Next.js/React (frontend), Python FastAPI (API), ChromaDB persistente local (base vectorial MVP), embeddings multilingües configurables, SDK del proveedor LLM configurado por entorno. Se preferirá retrieval híbrido (full-text + vectores), con re-ranking opcional y devolución de evidencia. **No se fija un modelo comercial concreto sin benchmark de octubre de 2026**: la recomendación «Gemini 1.5 Flash / GPT-4o-mini» del documento de FAQ es histórica y debe reevaluarse por disponibilidad, precio, soporte en español, latencia y grounding; el MVP `/health` funciona sin LLM ni API key.

**Criterio de selección del modelo:** precisión de citas (prioridad), abstención, robustez frente a inyección, latencia p95, costo por 100 consultas, tratamiento de datos, facilidad de integración y disponibilidad de function calling. Tres variantes de prompt se compararán en dataset controlado.

## 9. Éxito y entregables

- ≥16/20 respuestas correctas **y** con artículo correcto (80%).
- 100% abstención en las consultas sin respuesta ensayadas.
- 100% rechazo de consultas fuera del ámbito académico y ataques de inyección ensayados.
- Tres prompts × 10 preguntas documentados; cuatro tipos de pruebas en URL pública.
- README, arquitectura, inventario, pruebas, fuentes y contribuciones de los tres integrantes.

## 10. Supuestos y pendientes

Las 15 FAQ del archivo recibido son una **propuesta**, no la evidencia de entrevistas realizadas. No existen aún respuestas reales, fechas de campo, conteos ni firmas. Los documentos locales en `data/raw` no se consideran vigentes hasta la validación y el registro de reforma. Pendiente definir integrantes, carrera/modalidad exactas, presupuesto, proveedor LLM y aprobación de la selección documental.

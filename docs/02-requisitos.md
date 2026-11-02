# 02. Requisitos de software — Semana 1

## Historias de usuario y criterios de aceptación (Gherkin)

### HU-01 — Consultar una norma
**Como** estudiante, **quiero** formular una pregunta sobre titulación, **para** recibir orientación con fuente verificable.
- **Dado** que existe un fragmento oficial vigente y pertinente, **cuando** pregunto un requisito de titulación, **entonces** la respuesta incluye contenido respaldado, título, artículo/sección y URL.

### HU-02 — Abstención por falta de fundamento
**Como** estudiante, **quiero** no recibir información inventada, **para** saber cuándo acudir a secretaría.
- **Dado** que no existe evidencia suficiente, **cuando** consulto una condición no documentada, **entonces** el sistema se abstiene explícitamente, no inventa norma y señala el canal institucional.

### HU-03 — Desambiguar carrera y modalidad
**Como** estudiante, **quiero** precisar contexto antes de una respuesta, **para** evitar reglas inaplicables.
- **Dado** que la consulta depende de carrera o modalidad no indicadas, **cuando** formulo una pregunta ambigua, **entonces** el asistente pide aclaración sin dar una conclusión definitiva.

### HU-04 — Consultar requisitos por modalidad
**Como** aspirante, **quiero** consultar requisitos concretos, **para** preparar documentos.
- **Dado** que la modalidad existe y está soportada por normativa aprobada, **cuando** solicito sus requisitos, **entonces** la herramienta devuelve una lista estructurada con referencias verificables.

### HU-05 — Generar checklist
**Como** estudiante, **quiero** indicar requisitos que ya cumplí, **para** identificar pendientes.
- **Dado** que hay reglas aprobadas y datos autodeclarados, **cuando** solicito mi checklist, **entonces** cada ítem se marca cumplido, pendiente o no verificable y contiene respaldo.

### HU-06 — Calcular un plazo
**Como** estudiante, **quiero** conocer fechas de entrega, **para** planificar trámites.
- **Dado** que se dispone de la fecha base, feriados y regla de días hábiles aplicable, **cuando** solicito una fecha límite, **entonces** el sistema calcula e indica regla/fuente, o se abstiene si faltan datos.

### HU-07 — Control de vigencia
**Como** administrador, **quiero** registrar versiones de normas, **para** evitar referencias obsoletas.
- **Dado** que una fuente tiene vigencia pendiente o fue sustituida, **cuando** intento activarla para respuestas, **entonces** el sistema impide tratarla como vigente hasta verificarla.

### HU-08 — Bloquear prompt injection
**Como** evaluador, **quiero** probar resistencia a órdenes maliciosas, **para** proteger integridad.
- **Dado** que una entrada contiene instrucciones para ignorar políticas, **cuando** envío la consulta, **entonces** el asistente no sigue dichas instrucciones y mantiene el límite académico.

### HU-09 — Registrar evidencia de prueba
**Como** evaluador, **quiero** comparar resultados con respuestas esperadas, **para** medir calidad.
- **Dado** que dispongo de casos con artículo esperado, **cuando** ejecuto la evaluación, **entonces** se registra acierto, cita, abstención, latencia y motivo de fallo sin datos personales.

### HU-10 — Consultar respaldo documental
**Como** estudiante, **quiero** abrir el documento origen, **para** comprobar la respuesta.
- **Dado** que se ha generado una respuesta con evidencia, **cuando** selecciono una cita, **entonces** veo URL oficial, identificador de artículo, versión y página si existe.

## Requisitos funcionales

| ID | Requisito | Prioridad |
|---|---|---|
| RF-01 | Chat que recibe preguntas y metadatos de contexto | Alta |
| RF-02 | Ingesta versionada y aprobada de documentos oficiales | Alta |
| RF-03 | Segmentación por artículo/inciso con metadatos | Alta |
| RF-04 | Búsqueda semántica y lexical con filtro de vigencia | Alta |
| RF-05 | Respuesta y validación backend de citas | Alta |
| RF-06 | Abstención / aclaración / rechazo de fuera de alcance | Alta |
| RF-07 | Tres herramientas: requisitos, plazo, checklist | Alta |
| RF-08 | Dataset de evaluación y exportación de métricas | Alta |
| RF-09 | Panel de aprobación documental | Media (MVP manual) |

## Requisitos no funcionales medibles (objetivos de aceptación propuestos)

| ID | Métrica verificable | Objetivo | Método |
|---|---|---|---|
| RNF-01 | Respuesta p95 a consultas RAG (sin ingestion) | ≤ 8 s bajo 5 usuarios concurrentes en entorno de prueba | 100 consultas instrumentadas |
| RNF-02 | Disponibilidad del endpoint `/health` | ≥ 99% durante 24 h de prueba de despliegue | Sondeo cada 60 s |
| RNF-03 | Cita exacta | ≥ 16/20 respuestas correctas y con artículo esperado | Golden set validado |
| RNF-04 | Abstención de preguntas sin evidencia | 100% del conjunto negativo | Suite negativa |
| RNF-05 | Rechazo fuera de dominio/inyección | 100% de los casos ensayados | Suite adversaria definida antes de probar |
| RNF-06 | Secretos en frontend y Git | 0 credenciales expuestas | Gitleaks / revisión de bundle y repo |
| RNF-07 | Trazabilidad | 100% de respuestas afirmativas incluyen documento + artículo/sección + versión/URL | Test automático |
| RNF-08 | Privacidad del dataset | 0 datos personales reales en casos de prueba | Revisión manual y automatizada |
| RNF-09 | Accesibilidad básica del chat | Navegable íntegramente con teclado; contraste WCAG AA en componentes esenciales | Playwright + axe |
| RNF-10 | Mantenibilidad | ≥80% cobertura del código de negocio crítico (sin contar infraestructura) | pytest-cov |
| RNF-11 | Reproducibilidad | Backend levanta con README y `uvicorn`; health responde 200 | Instalación limpia |
| RNF-12 | Calidad documental | 100% fragmentos activados con ID, artículo/sección y URL fuente | Validador de ingestión |

## Restricciones y reglas de negocio

- El LLM no es fuente de autoridad; solo los documentos oficiales aprobados pueden fundamentar requisitos.
- Un fragmento con `verification_status != approved` **no** participa como norma vigente.
- Cuando cambie el calendario institucional, invalidar respuestas de plazos antes de publicar la nueva versión.
- Un checklist del MVP es orientativo, no certifica estado académico oficial.
- El proveedor LLM nunca es invocado directamente desde navegador.
- Las consultas ajenas al ámbito se rechazan; no se ejecutan transacciones académicas.

## Evidencias de aceptación pendientes

Registrar test, fecha, ejecutor, build, ambiente, esperado, obtenido y captura/registro. Las metas anteriores **no se consideran aprobadas aún**.

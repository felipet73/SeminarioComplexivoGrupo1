# Auditoría de la guía HTML — Grupo 1

**Documento histórico del 1 de noviembre.** La revisión actual, que incorpora las regresiones y nuevas observaciones del docente, está en [análisis del 5–6 de noviembre](evidencias/semana-3/2026-11-05/analisis-observaciones-docente.md). Consultar allí el estado vigente y sus pendientes; las cifras siguientes se conservan como antecedente.

Corte: 1 de noviembre de 2026. Referencia: `Guia_practica_Entrega3_por_proyecto (3).html`, grupo Titulación y normativa académica; sección «3 · El camino, paso a paso» y pestaña «Lo que piden a todos». Se revisaron niveles mínimo, recomendado y avanzado, incluidos los pasos comunes que no aparecen en la ruta priorizada del grupo.

## Todos los pasos, nivel por nivel

| Paso | Mínimo | Recomendado | Avanzado y comprobación |
|---|---|---|---|
| Propio g1a: normativa real | Cinco originales en `data/raw`; `scripts/ingest.py` usa las mismas funciones que el panel | Manifiesto corregido con SHA-256, fecha de incorporación y origen; estrategia nueva por defecto hybrid | Vigencia por fuente en `config/fuentes.yaml`; el script valida hashes y políticas antes de mutar. El estado local se activó como híbrido con el modelo medido mediante `scripts/activar_hibrido.py` |
| Común corpus: ingesta | PDF reales y exportación de fragmentos | División por artículo/sección, documento, revisión y página | Manifiesto con fechas de incorporación reales. `downloaded_at=null` en cargas del panel: no se inventa una descarga. `data/raw/download-attempts.json` conserva los fallos históricos |
| Común RAG: citas y silencio | FTS5/BM25 real, umbral de cobertura léxica y abstención sin LLM | Vectores multilingües, coseno y umbral semántico | Persistencia vectorial SQLite + BM25 + RRF. Alternativa justificada a Chroma, sin afirmar ANN. Modelo y firma impiden mezclar vectores. Comparación real con 20 preguntas; 961 fragmentos en cinco fuentes |
| Común herramienta con contrato | Calendario determinista y límites Pydantic; caso calculado a mano y validación de error | Herramientas de consulta y checklist; registro demo de tutor con confirmación y pruebas de cancelación/expiración | `model_json_schema()` en `/api/herramientas`; entradas y salidas tipadas en `/docs`. Parámetros en `config/parametros.yaml`. Fechas e enteros, sin Decimal porque no hay montos; no se copia el plazo ficticio ni el artículo TODO del ejemplo |
| Común agente | Solicitudes JSON del modelo, PERMITIDAS, MAX_ITER y bloqueo de funciones ajenas | REQUIEREN_OK y endpoint `/api/herramientas/agente/confirmar/{id}`; React muestra argumentos exactos y Confirmar/Cancelar | Capacidad secreta con TTL; ID por acción como clave idempotente; transacción y auditoría del actor de demostración. No duplica registro al repetir; una decisión contradictoria falla con 409. Pruebas A, B, C y D en `test_agente.py`/`test_actions.py` |
| Propio g1b: evaluación honesta | 20 preguntas con documento/artículo y respuestas esperados; script llama al flujo real con `--chat` | `eval/comparar.py` mide lexical/hybrid sobre el mismo corpus y preguntas | Evaluación sin modelos en cada CI; ejecución manual de evaluación real con secretos. Se eliminó el script que inventaba alucinaciones según el nombre del prompt. Las cifras reales y los modelos dobles se distinguen explícitamente |
| Común evaluación | 20 preguntas, incluidas cuatro sin respuesta en el corpus | Casos del agente A–D, citas y respuestas reales; negativos también educativos | Umbrales que hacen fallar CI: recuperación ≥70%, silencio ≥90%, contratos 20/20; con chat real citas ≥80% y negativos 100%. El acierto de artículo no sustituye la revisión semántica humana |
| Común calidad | Pytest, validación HTTP y README de estado real | Cobertura mínima de 85% y evaluación en CI | Ruff de errores críticos, comprobador de patrones de secretos y auditorías Python/npm. Workflow preparado para push/PR y ejecución manual real. **Publicar y observar Actions verde sigue pendiente: no se confunde el archivo de CI con una corrida remota** |
| Común talleres | `docs/09-decisiones.md`, `docs/10-automatizacion.md`, `docs/11-plan-de-calidad.md`, `config/parametros.yaml` | `backend/app/flujo.py` y `eval/casos_flujo.jsonl` con 20 casos | `eval/evaluar_flujo.py` ejecuta esos casos desde CI y exige 20/20. Son implementaciones para esta entrega, no supuestas descargas originales del taller. Su publicación en GitHub forma parte del pendiente de entrega |

La propia guía permite una solución arquitectónica distinta si satisface la definición de hecho. Se documentan estas equivalencias: SQLite con vectores persistentes en lugar de Chroma; fechas e enteros en lugar de Decimal; fecha de incorporación verificable en lugar de una descarga desconocida; registro de borrador demo en lugar de un envío institucional real. No se amplía el alcance a expedientes, mensajería ni despliegue público.

## Los cinco requisitos comunes de «hecho»

| Requisito | Evidencia local | Límite o pendiente |
|---|---|---|
| Conocimiento especializado | Cinco originales, manifiesto y YAML; ingesta de 961 fragmentos trazables | Las fechas/aprobación preservan la revisión del equipo; validar actualidad normativa y URL oficial cuando se aporte información verificable |
| RAG | Comparación BM25/híbrido real, citas y silencio medidos; chat real con Gemini | El 100% sobre esta muestra no implica cobertura de futuras preguntas; ampliar evaluación con cada nueva fuente |
| Agente controlado | Herramientas tipadas, límite, confirmación, caducidad, idempotencia y auditoría; pruebas A–D | Borrador solo local; capacidad de demostración, no identidad universitaria autenticada |
| Calidad | Pruebas backend/frontend/navegador, cobertura, lint y auditorías; `.env` ignorado | Hace falta publicar cambios y observar la ejecución remota de Actions |
| Evaluación básica | 20 preguntas con fuente y respuesta esperadas; 20 casos del flujo; informes reales exportados | Las respuestas deben revisarse contra la fuente; no se presenta un juez automático como exactitud semántica |

## Mediciones obtenidas

| Medición | Resultado | Evidencia |
|---|---|---|
| Recuperación léxica | 14/16 (87,5%) | `docs/evidencias/semana-3/comparacion-real.json` |
| Recuperación híbrida | 16/16 (100%) | Mismo informe, mismo corpus y preguntas; embeddings text-embedding-3-small |
| Silencio de recuperación | 4/4 en ambos modos | Mismo informe; incluye preguntas educativas sin respaldo |
| Chat real con híbrido | Cita esperada en 16/16; abstención/rechazo en 4/4 negativas | `docs/evidencias/semana-3/chat-real-hibrido.json`; Gemini con respaldo OpenAI, sin sustituirlos por un modelo doble |
| Contratos del flujo | 20/20 | `docs/evidencias/semana-3/flujo-contratos.json`; corpus real y modelo doble declarado |
| Backend | 50 pruebas; cobertura de sentencias 88,08%, umbral 85% | Pytest y `cobertura.xml`; la advertencia de deprecación httpx/TestClient no es un fallo |
| Frontend | 15 pruebas; tipos y compilación | Vitest, TypeScript y Vite |
| Navegador | 9/9 escenarios aprobados, incluido confirmar borrador contra API aislada y vista móvil | Playwright; tras un primer cierre bloqueado por Windows se repitió fuera del entorno restringido y terminó con `9 passed` |
| Dependencias | 52 paquetes de ejecución/pruebas sin avisos conocidos; npm 0 vulnerabilidades | Informes finales; ver limitación separada del tooling Python 3.10 |
| Ingesta limpia | 961 fragmentos; BM25 14/16 y silencio 4/4 | `ingesta-limpia.json`, reconstrucción sin usar el estado del panel |
| Lint y secretos | Sin errores críticos ni patrones de clave encontrados | Ruff E9/F63/F7/F82 y `scripts/check_secrets.py`; no se afirma detección exhaustiva de todo secreto posible |

Los informes crudos conservan respuestas y denominadores. Se excluyen `.env`, bases SQLite y capacidades de confirmación de las evidencias publicables.

## Dependencias y entorno

La primera auditoría local detectó 51 avisos en cinco paquetes. Se actualizaron pip, setuptools, pyasn1 y pypdf; el runtime y las dependencias de pruebas se auditan por su inventario instalado en `backend/requirements.lock.txt`. Es un snapshot de auditoría de Python 3.10/Windows, no un lock universal de todos los sistemas. El frontend recibió una corrección de minimatch y se comprueba también el generador OpenAPI, además de tests y build.

La herramienta de auditoría local trae filelock 4.1 en el Python 3.10 heredado. Su corrección exige Python ≥3.11; `requirements-dev.txt` la exige para el Python 3.12 recomendado y usado en CI. Este aviso de herramientas no se oculta ni se confunde con las dependencias del runtime. Revisar los informes finales `auditoria-runtime-final.json` y `auditoria-frontend-final.json`.

## Limpieza de los hallazgos

Se sustituyó la arquitectura de solo `/health` por la arquitectura implementada React/Vite/FastAPI. Se quitaron variables Chroma sin uso. Las 20 diapositivas de clase que estaban en `tmp/pdfs` se trasladaron a `tmp/respaldo-diapos`, respaldo local ignorado; no se borraron los originales del usuario. Se preservaron los cambios locales previos de `main.py` al integrar las rutas adicionales.

## Cierre humano y publicación

Antes de declarar entregado: revisar los cambios y respuestas, publicar el commit, comprobar Actions en verde y configurar los secretos para el job manual real. Confirmar la vigencia y procedencia de nuevas fuentes, y completar el levantamiento real de FAQ. Los integrantes deben poder explicar las decisiones y los casos calculados a mano. Ninguno de estos hechos se infiere de que un test local haya pasado.

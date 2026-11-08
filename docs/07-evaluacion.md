# Evaluación reproducible y resultados

> **Estado de entrega al 7 de noviembre de 2026:** Consultar el [checklist vigente s4a–s4k](14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

Revisión del 5–6 de noviembre de 2026. Las cifras anteriores del 1–2 de noviembre son históricas; los informes de esta revisión están en `docs/evidencias/semana-3/2026-11-05/`, fecha de inicio de la sesión. Sus marcas de tiempo usan UTC.

La ampliación posterior de CORS y proxy Vercel elevó la suite a 75 pruebas backend, cobertura 88,43 %, y 18 frontend; los 10 escenarios de navegador también pasaron. Ese seguimiento y la comprobación HTTP pública (3/6 antes de publicar las correcciones) se documentan en [configuración de producción del 6 de noviembre](evidencias/semana-3/configuracion-produccion-2026-11-06.md). Las tablas siguientes conservan los resultados de su revisión original.

## Corrección de la regresión

Se recuperó del historial el evaluador que usa `rag.retrieve`; se eliminaron la llamada inexistente a `rag.buscar` y el resultado siempre verdadero. `eval/comparar.py` vuelve a importar la función pública `evaluar`. No se presentan puntuaciones escritas a mano ni se usa una excepción como silencio correcto.

El conjunto contiene 20 preguntas: 16 con documento y artículo esperados y cuatro sin respuesta, incluyendo una educativa ajena al corpus. Las respuestas de referencia están en `eval/respuestas_esperadas.json`. La carga exige al menos 20 casos, cuatro negativos, IDs únicos y documento/sección coherentes.

Un acierto de recuperación exige **documento y sección** esperados, no solo un número de artículo. El silencio exige ausencia de evidencia sin error de búsqueda. Con `--chat` se ejecuta el flujo real y se comprueba que la respuesta cite la fuente/artículo esperados, o se abstenga/rechace sin fuentes en los negativos. Los fallos de recuperación o proveedor quedan registrados y hacen fallar la evaluación.

Los umbrales se leen de `config/parametros.yaml`: recuperación ≥0,70; silencio ≥0,90; citas positivas ≥0,80; negativas con abstención/rechazo sin fuentes =1,00. El CLI sale con 0 si cumple, 1 si no cumple y 2 si no se pudo preparar la evaluación. Un corpus vacío produce 0 de acierto y **exit 1**. Estas regresiones tienen pruebas de ejecución del CLI y del import del comparador.

## Resultados de esta revisión

| Medición | Resultado | Evidencia |
|---|---|---|
| BM25, sin generación | 14/16 artículos; silencio 4/4; 0 errores | `comparacion-real.json`, `recuperacion-lexical.json` |
| Híbrido, embeddings OpenAI text-embedding-3-small | 16/16 artículos; silencio 4/4; 0 errores | `comparacion-real.json` |
| Chat real Gemini con híbrido | Cita esperada 16/16; negativas 4/4; 0 errores | `chat-real-hibrido.json` |
| Agente real, primera medición | 2/6 checklists con cita | `agente-real-antes.json` |
| Agente real, última medición | Seleccionó y ejecutó generar_checklist en 6/6; checklist final con cita en 5/6 | `agente-real.json` |
| Contratos del flujo con modelo doble | 20/20 | `flujo-contratos.json` |
| Backend local Python 3.10 | 64 pruebas; 88,29 % de cobertura, mínimo 85 % | `tests-backend.xml`, `cobertura-backend.json` |
| Backend Linux/Python 3.12.16 | 64 pruebas; 88,29 % de cobertura | `tests-linux.txt`; imagen sin `.env` ni `.venv` local |
| Frontend | 16 pruebas y build TypeScript/Vite correcto | `tests-frontend.json` |
| Navegador | 10/10 escenarios con API aislada y modelo doble | Checklist, confirmación, administración y vistas adaptables; en Windows el cierre de servidores requirió limpieza manual |
| Auditorías | 0 avisos conocidos en 50 dependencias de la imagen; npm 0 vulnerabilidades; gitleaks 0 hallazgos/28 commits | `auditoria-python.json`, `auditoria-frontend.json`, `gitleaks-historial.json` |
| Contenedor | Build y smoke HTTP aprobados; 961 fragmentos elegibles; PORT personalizado | `contenedor.json`; semilla léxica, sin llamadas a modelos |

El primer problema de checklist fue recuperar requisitos de cargos por buscar solamente «requisitos posgrado». Se centró la búsqueda en el trámite y perfil, se excluyeron cargos y se probaron perfiles incompatibles y niveles inventados por el modelo. Hubo una corrida intermedia con seis listas; **no sustituye el resultado de la última versión**. El caso complexivo final se abstuvo tras usar checklist y buscar evidencia adicional: los pasajes aprobados eran específicos de artes/salud y no sustentaban la lista general pedida. El instructivo institucional descargado permanece pendiente de revisión del OCR y aprobación. No se fuerza una lista para alcanzar 100 %.

`eval/evaluar_agente_real.py` exige seis listas finales con citas para su criterio estricto y devuelve exit 1 con 5/6. Es una limitación conocida del corpus, visible también en el job manual de CI; no se rebajó el umbral ni se excluyó la pregunta. Las trazas muestran turnos, proveedor, nombre y argumentos de herramientas, fragmentos y resultado de checklist. No contienen claves ni capacidades de confirmación. El proveedor se usa sin fallback en estas seis consultas; el modelo decide las herramientas, no un guion.

## Ejecución

```bash
python scripts/ingest.py --data-dir data/eval-state --strategy lexical
python eval/evaluar.py
python eval/evaluar_flujo.py
python -u eval/comparar.py --embedding-model text-embedding-3-small
python eval/evaluar.py --data-dir data/eval-hybrid --chat --prompt system_v3
python eval/evaluar_agente_real.py --modelo gemini
```

Las últimas tres órdenes necesitan credenciales/cuota; las demás no llaman a modelos. Pruebas A–D del agente, lista cerrada, tope, confirmación, expiración, cancelación e idempotencia se ejecutan con dobles declarados en pytest. El escenario de navegador de checklist usa la API y herramienta reales con modelo doble; no constituye evidencia del proveedor.

CI en push/PR ejecuta backend/cobertura, lint, búsqueda/flujo sin modelos, frontend, navegador, auditorías y build/smoke de contenedor. La ejecución manual agrega comparación, chat y agente reales. Una definición YAML no prueba que Actions haya corrido en GitHub; la corrida remota debe observarse después de publicar.

## Qué no miden estas cifras

Acierto de artículo y validación de ID no certifican que cada afirmación esté implicada por el pasaje. La revisión semántica y de vigencia sigue siendo humana. La muestra no es un conjunto reservado independiente: se ha usado durante el desarrollo y no demuestra generalización. Ampliar casos al aprobar nuevas fuentes, incluyendo requisitos internos, perfiles contradictorios y preguntas sin respuesta. Los metadatos de aprobación no sustituyen una resolución institucional.

## Corte final local del 7 de noviembre

Recuperación léxica repetida sobre estado aislado: **14/16 positivos, 4/4 negativos, 0 errores**, igual al baseline histórico. Contratos de flujo con modelo doble: **20/20**. [Resultado fechado](evidencias/semana-4/recuperacion-lexica-final-2026-11-07.json). Los 35 casos públicos de Actions 42378740379 intento 2 no sustituyen el golden set de 20 con chat, la comparación híbrida ni seis checklists reales; s4e permanece parcial. Para la corrida manual activar `evaluar_modelo_real=true`; en main puede desplegar además de evaluar.

## Runner separado para cierre de s4e

El workflow manual `.github/workflows/evaluacion-final.yml` permite repetir comparación, golden set generativo y seis checklists sin desplegar. Necesita `GEMINI_API_KEY` y `OPENAI_API_KEY` en Secrets de Actions; no hereda Secret Manager. Los resultados se guardan como artefacto y un fallo mantiene la corrida roja. Esta automatización preparada no acredita una corrida real nueva ni cambia el 5/6 histórico.

## Evaluación final aportada el 8 de noviembre de 2026 UTC

Se conservan los [tres JSON completos aportados por el equipo](evidencias/semana-4/2026-11-08-evaluacion-final/). Sus fechas internas van de 03:12 a 03:14 UTC. El identificador de ejecución de Actions y el SHA del runner no están incluidos en esos JSON ni se infieren del SHA publicado en Cloud Run. Falta añadir esa vinculación para completar trazabilidad.

| Medición | Resultado |
| --- | --- |
| Recuperación léxica, 16 positivos | 14/16 (87,5 %) |
| Recuperación híbrida OpenAI `text-embedding-3-small`, 16 positivos | 16/16 (100 %) |
| Silencio fuera de dominio, ambos recuperadores | 4/4 (100 %) |
| Chat real: artículo esperado citado | 16/16 (100 %) |
| Chat real: abstención/rechazo en negativos | 4/4 (100 %) |
| Agente estricto Gemini sin fallback | 0/6; seis errores genéricos de indisponibilidad |

Los 16 positivos del chat usaron `gemini-3.5-flash-lite` sin fallback. Los cuatro negativos fueron dos rechazos y dos abstenciones sin uso de modelo. La indisponibilidad posterior del agente no prueba una clave permanentemente inválida ni una mala elección de herramientas. Los reportes anteriores no conservan el estado HTTP/categoría del error: no permiten atribuirlo a cuota, autenticación o conectividad. El nuevo diagnóstico conserva únicamente categorías conocidas y estado HTTP, y el workflow adjunta la telemetría local sanitizada para una siguiente ejecución. No se rebajan los seis criterios estrictos ni se convierte este 0/6 en un aprobado.

En relación con los cortes de semana 3 documentados arriba, se repiten 20 preguntas (16 positivas y cuatro negativas) y seis casos del agente; recuperación y citas siguen siendo controles de artículo, no una garantía semántica de cada frase. Este corte usa embeddings OpenAI; no atribuir diferencias solo al código sin controlar corpus, modelos y configuración. El 5/6 histórico del agente conserva su fecha y no sustituye el 0/6 final observado. La revisión humana del OCR sigue pendiente.

### Segundo intento final: límite por minuto identificado

Los [reportes del segundo intento](evidencias/semana-4/2026-11-08-evaluacion-final-intento2/) tienen fechas internas del 8 de noviembre de 2026, 03:25–03:26 UTC. La captura de Actions aportada identifica el commit abreviado `f93076f`; no se dispone aquí del identificador de ejecución. Se conservan los JSON y la telemetría originales del runner.

Recuperación: léxico 14/16, híbrido 16/16 y silencio 4/4. Chat: citas 16/16, negativos 4/4, sin errores finales; 12 respuestas con Gemini y cuatro con OpenAI como respaldo. Agente: 0/6, todos con `categoria_proveedor=cuota_o_limite` y `status_proveedor=429`. La telemetría contiene diez intentos Gemini con 429 y llamadas Gemini exitosas: la credencial no estuvo permanentemente rechazada por autenticación.

La captura posterior de AI Studio muestra para Gemini 3.5 Flash Lite **17/15 RPM**, **59,58K/250K TPM** y **99/500 RPD**. Confirma saturación por solicitudes/minuto en el momento de la captura, sin agotamiento diario visible. No se atribuye cada respuesta histórica a una ventana exacta no registrada.

Corrección preparada: `EVAL_LLM_MIN_INTERVAL_SECONDS=6` en el workflow, aplicado por el cliente a **cada intento** y a las vueltas del agente; `LLM_RETRIES=2` solo en ese runner. El cliente compartido conserva el ritmo entre casos, con aproximadamente diez inicios/minuto por proceso. El intervalo por defecto del cliente de producción continúa en cero; no se modifica su política de reintentos. Las cuotas son compartidas por proyecto: otras llamadas simultáneas pueden seguir causando 429; el ritmo no garantiza aprobación ni sustituye aumentar cuota si es necesario. El embedding continúa con OpenAI, no Gemini.

Pendiente: fusionar la corrección e iniciar una ejecución nueva sobre main, con el proyecto sin otras pruebas intensivas simultáneas. Los seis casos estrictos del agente y su prohibición de fallback siguen intactos. El segundo intento se conserva como fallo real y no se reemplaza por un aprobado supuesto.

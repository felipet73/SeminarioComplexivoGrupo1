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

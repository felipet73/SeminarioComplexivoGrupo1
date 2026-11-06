# Sincronización de main y corrección de CI — Grupo 1

Fecha: 6 de noviembre de 2026. Esta revisión complementa el [análisis de las observaciones del docente](../2026-11-05/analisis-observaciones-docente.md). No sustituye las limitaciones registradas allí.

## Conservación y comparación

Los 82 archivos con cambios locales se guardaron mediante un commit antes de actualizar main:

| Referencia local | Commit | Propósito |
|---|---|---|
| `respaldo/cambios-locales-2026-11-06` | `80623860c164addf3370200afd090fb77fbd6bea` | Conserva íntegramente el trabajo local anterior |
| `main` y `origin/main` | `f8e0a1b67e57ec388c408238b582c320d1507277` | Última versión remota, actualizada con fast-forward |
| `fix/ci-main-sin-servicios-externos` | Correcciones desde `08ef882` | Cambios revisables separados de main |

La comparación entre el respaldo y main mostró diferencias solamente en siete archivos: `backend/app/agente.py`, `schemas.py`, `seguridad.py`, `backend/tests/conftest.py`, `test_admin.py`, `test_agente.py` y `test_endpoints.py`. El resto de las mejoras locales ya estaba incluido: frontend, URLs públicas de producción, CORS/proxy, documentos, corpus, evaluador y herramientas. Esto acredita la presencia de esos cambios; no significa que todas las observaciones del docente estén cerradas.

No se usaron reset, force push ni sobrescrituras del historial remoto. Las ramas y los commits nuevos permanecen locales; main conserva exactamente el commit remoto. El `.env` privado no se incorporó al respaldo.

## Fallos observados en GitHub Actions

Ejecución examinada: [Pruebas Grupo 1, main f8e0a1b](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42300191418).

| Job | Evidencia y causa | Corrección |
|---|---|---|
| [backend](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42300191418/job/128175656995) | 6 fallos, 53 aprobadas y 16 errores. La indexación solicitaba `GEMINI_API_KEY`; cobertura 73,03 %, inferior al 85 %. Se había eliminado el aislamiento léxico de las pruebas y agregado carga del `.env` con `override=True` | Se restituye SQLite temporal y estrategia léxica en fixtures. Se deshabilita la lectura del `.env` durante cada prueba, se vacían credenciales incluso para subprocesos y se bloquean proveedores reales hasta que un test los sustituya por un doble. La configuración híbrida de producción permanece disponible |
| [contenedor](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42300191418/job/128175656695) | `ValueError: Hash OCR incorrecto` durante la ingesta del build. El hash del manifiesto correspondía al archivo con CRLF de Windows; Git había guardado LF | OCR con LF, actualización del hash y sus notas en manifiesto/política; `.gitattributes` declara `data/raw/** -text`. Se mantiene la verificación SHA-256 de originales y OCR, además del vínculo OCR-original |
| frontend y navegador | Ambos aprobados en esta ejecución | Sin cambios de producto en este parche |

Los cuatro checks rojos de la captura son backend y contenedor repetidos por eventos push/pull_request. No equivalen a cuatro causas independientes ni a que todas las pruebas estén fallando. La evaluación real aparece omitida porque requiere ejecución manual y secretos.

Hash OCR anterior en Windows: `9505654613bb00077bfdf97dd5bf16dfaf692c8fa0af483d8144e5d7b5ca926e`. Hash de los bytes LF ya guardados en Git y del manifiesto corregido: `556a1f22b919a8158adcd0eb227885539d5a79d3a0c2a6ec3be6b714377f82bf`. El PDF original no se modificó. La validación local anterior no había comprobado esta diferencia en un checkout limpio.

## Regresiones corregidas y relación con las observaciones

| Requisito del docente | Implementación y evidencia |
|---|---|
| Ingesta reproducible y fuentes trazables | `cargar_fuentes` valida el manifiesto completo antes de modificar el índice. Nuevas pruebas usan el corpus real, rechazan OCR alterado y rechazan un OCR cuyo hash es correcto pero pertenece a otro PDF. Se verifica que el índice no se cree tras esos errores |
| Citas y abstención verificables | Se recuperan las aserciones estrictas del respaldo: no se acepta indistintamente respuesta/aclaración o rechazo/abstención. Se mantienen fuente, fragmento, controles de contexto y evidencia de ejecución |
| Agente con lista cerrada y límite | Se restituyen las comprobaciones de herramienta no permitida, recorrido exacto hasta MAX_ITER y entrega de resultados al siguiente turno. Las pruebas híbridas usan embeddings simulados explícitamente |
| Contrato backend/frontend | Se elimina la inferencia de estado y campos a partir de palabras en el texto. Una respuesta válida sobre una «carrera» o «curso» no debe inventar una aclaración; mencionar una prohibición normativa no implica rechazo. Estado y tiempo son obligatorios. Cinco casos nuevos cubren estas regresiones |
| Pruebas, CI y secretos | Se conserva el umbral de cobertura del 85 % y los umbrales del evaluador. El job backend declara claves vacías, reserva credenciales para evaluación real y cachea ambos archivos de dependencias. Se retira `seguridad.py`, módulo sin consumidores con credenciales fijas; la autenticación activa sigue en `admin_auth.py` |
| Contenedor verificable | Construcción desde un worktree limpio de Git, sin `.env` ni venv local. Se prueba arranque HTTP, readiness, catálogo, cálculo de plazo y ausencia de la ruta administrativa retirada. Se corrige además el reintento cuando Docker acepta la conexión antes de que Uvicorn pueda responder (`RemoteDisconnected`, subclase de `ConnectionError`) |
| Auditoría del entorno | La comprobación adicional de la imagen base local detectó avisos sobre `pip 25.0.1`. El backend de Actions ya ejecutaba su actualización; el Dockerfile ahora también la hace antes de instalar dependencias. La reconstrucción instaló `pip 26.3`. No se ocultan paquetes ni se excluye pip del auditor |

## Validación ejecutada

| Comprobación | Resultado |
|---|---|
| Pytest local Windows, Python 3.10.6 | **83/83**, cobertura **88,43 %** |
| Pytest sobre checkout limpio montado en Linux, Python 3.12.16 | **83/83**, cobertura **88,43 %**, sin claves ni `.env`; confirmado también en la imagen final con instalación de `requirements-dev.txt` |
| Ruff y detector local de patrones de secretos | Aprobados |
| `pip-audit --local`, entorno Linux final con dependencias de desarrollo | **Sin vulnerabilidades conocidas** según la consulta ejecutada; incluye `pip 26.3` |
| Ingesta léxica del corpus en Linux | 6 documentos, **1.047 fragmentos** totales; **961 elegibles**, 86 del instructivo pendientes de aprobación |
| Evaluación de recuperación, corpus real y sin LLM | **14/16** documentos/artículos esperados, **4/4** negativos, **0 errores**; supera los umbrales configurados |
| Evaluación del flujo con modelo doble y corpus real | **20/20**; no representa una medición del modelo real |
| Build desde `tmp/ci-main-clean`, commit `659f682` | Aprobado: `titulacion-rag:ci-main`, con `pip 26.3` |
| Smoke HTTP de la imagen, puerto local 18087 | Aprobado: `/health`, `/ready` con 961 fragmentos, herramientas, fecha calculada y ruta retirada 404. Contenedor detenido al finalizar |

Anexos: [recuperación](evaluacion-recuperacion.json) y [flujo](evaluacion-flujo.json). Comandos principales:

```powershell
backend/.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short --cov=app --cov-fail-under=85
git worktree add --detach tmp/ci-main-clean 659f682
# Desde el worktree limpio:
docker build -f backend/Dockerfile -t titulacion-rag:ci-main .
```

En Linux también se ejecutaron `scripts/ingest.py --data-dir data/eval-state --strategy lexical`, `eval/evaluar.py` y `eval/evaluar_flujo.py`, sin credenciales. Pytest conserva una advertencia de deprecación de Starlette/httpx; no produjo fallos.

## Límites pendientes

Estos resultados son verificaciones locales, incluidas ejecuciones en contenedores Linux. GitHub no ha ejecutado aún el parche porque no se ha publicado esta rama. No se modificaron Vercel ni Cloud Run.

El instructivo escaneado mantiene `approved=false`: necesita revisión humana del OCR y aplicabilidad. La evaluación generativa histórica del agente conserva el resultado estricto de **5/6** checklists finales con cita; no se repitió ni se rebajó ese criterio. Estas tareas siguen abiertas conforme al análisis del docente, independientemente de la corrección del CI.

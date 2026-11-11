# Pruebas funcionales y criterio de aceptación - Grupo 1

> **Conteo vigente, 8 de noviembre de 2026 UTC:** 147 pruebas backend aprobadas y 89,11 % de cobertura de `app` en ejecución local. Ver [XML, resumen y explicación de cortes anteriores](21-conteos-de-pruebas.md). El smoke público de 35 casos y la evaluación real del agente 6/6 son conjuntos separados; ver [checklist](14-checklist-entrega-final.md).

Las URLs evaluadas son el [backend de Cloud Run](https://titulacion-rag-386902880383.us-central1.run.app) y el [frontend de Vercel](https://seminario-complexivo-grupo1.vercel.app/). El contrato y los datos de prueba están en `eval/casos_http.json`; el runner es `scripts/pruebas_funcionales.py`. No se usan frases de ejemplo ni se acepta una abstención como respuesta normativa correcta.

## Ejecución

Desde la raíz, con Python 3.12; el runner solo necesita biblioteca estándar:

```powershell
python scripts/pruebas_funcionales.py --output eval/results-funcionales.json
# Añade tres consultas generativas (dos directas y una SSE por Vercel):
python scripts/pruebas_funcionales.py --incluir-modelo --output eval/results-funcionales-modelo.json
# Exige que la URL sirva exactamente el commit desplegado:
python scripts/pruebas_funcionales.py --expected-revision COMMIT_SHA --output eval/results-funcionales.json
```

La entrada `python backend/tests/smoke.py URL_BACKEND` se conserva por compatibilidad. `--solo-backend` omite explícitamente las comprobaciones de Vercel (cuatro contratos y, si se activa generación, un caso SSE). Los resultados informan todos los IDs omitidos; no se cuentan como aprobados. Sin `--incluir-modelo` se ejecutan 32 casos, incluidos consulta de requisitos y checklist contra el corpus real, pero no generación de texto por el LLM. Si la búsqueda usa embeddings, esas herramientas pueden consumir el proveedor de embeddings. Con el flag se ejecutan 35 casos. Las tres respuestas generativas exigen texto no vacío, modelo identificado, estado `respuesta`, documento y artículo esperados y un fragmento citado; el caso por Vercel exige además un evento SSE `done` válido.

## Casos y expectativas

| Grupo | Casos y resultado exigido |
|---|---|
| Frontend (4) | `/`, `/admin`, `/metricas`: 200 HTML; proxy `/api/admin/session`: 401 JSON |
| Proceso y corpus (2) | `/health`: 200, revisión presente y coincidente si se proporciona SHA; `/ready`: 200 y fragmentos elegibles > 0 |
| Seguridad antigua (2) | POST `/admin/login` y `/admin/recargar-reglamentos`: **404**, incluso con cuerpo vacío. Un 401, 405 o 422 no acredita retirada |
| Administración actual (4) | Sesión, bootstrap e historial sin autenticar: 401; login con cuerpo válido pero sin cabecera CSRF: 403 |
| Agente (1) | Cinco herramientas exactas, tope entre 1 y 10 y única escritura demo sujeta a confirmación |
| Validación del chat (3) | Cuerpo vacío, pregunta demasiado corta y modelo inventado: 422 |
| Inyección (3) | Chat y agente: 200 con estado `rechazo`, texto y fuentes vacías; stream: evento final de rechazo válido. No se acepta HTTP 500 ni SSE truncado |
| CORS (2) | Origen de Vercel permitido sin cookies cruzadas; origen ajeno rechazado y sin allow-origin |
| Calendario (6) | Fin de semana, año bisiesto y cero: fechas exactas; días negativos/booleanos y fecha imposible: 422 |
| Herramientas (4) | Entradas vacías: 422; requisitos con pasajes trazables; checklist con citas y `completo=false` |
| Fuente (1) | Revisión/documento inexistente: 404 |
| Generación (3; obligatoria tras desplegar) | RRA artículo 26: quién determina requisitos/opciones; RRA artículo 31: investigación formativa. Dos consultas directas y repetición del artículo 26 por el proxy SSE de Vercel; respuesta, modelo y cita del artículo/documento correcto |

El runner devuelve exit 1 si falla cualquier caso seleccionado o si se seleccionan menos de 15. Guarda estado esperado/obtenido, contrato, artículo/documento esperado, duración por caso y p95. No guarda contraseñas, tokens, cookies, capacidades ni texto libre completo. Una respuesta 200 por sí sola no aprueba las comprobaciones de contrato.

## Resultado contra producción

La corrida histórica publicada antes de añadir el caso SSE generativo obtuvo **23/34**, con cero omitidos. Véase [reporte completo](evidencias/semana-4/pruebas-url-inicial.json). En esa corrida el chat fallaba y las rutas legacy seguían disponibles. Es evidencia histórica: la ejecución posterior 42378740379, intento 2, aprobó el SHA `0dab82d` y los 35 casos actuales. Ver el [análisis técnico actualizado](analisis-tecnico-preliminar.md) y la [evidencia resumida](evidencias/semana-4/analisis-preliminar-2026-11-07.json). Esto no acredita revocación completa de credenciales históricas ni la evaluación estricta 6/6 del agente. El [informe de seguridad](evidencias/semana-4/analisis-observaciones-docente.md) detalla la credencial histórica aceptada, sin publicar sus valores o token.

## Pruebas locales y CI

Pytest mantiene el modelo simulado, estado temporal y lectura del `.env` deshabilitada. Las claves se vacían y los proveedores se bloquean salvo dobles explícitos. Se recuperaron las aserciones estrictas del agente, fuentes, contexto y SSE; no se rebajó el 85 % de cobertura ni los umbrales del evaluador.

Las regresiones añadidas cubren credenciales de baja entropía, alias del chat compartiendo límite, `Retry-After` con CORS, identidad de revisión y falsos aprobados por documento/artículo incorrectos, revisión vieja, 500 y SSE incompleto. El smoke de la imagen exige retirada de ambas rutas antiguas y un rechazo SSE antes de publicar la imagen.

## Evaluación repetida y límites

Repetir las corridas contra las dos URLs después de desplegar la nueva revisión y conservar los JSON en `docs/evidencias/semana-4/`. Se requiere 32/32 para los contratos sin generación y 35/35 para declarar también superadas las tres consultas generativas. El job de despliegue incluye `--incluir-modelo`: no puede aprobar omitiendo estos casos. Consume la cuota del proveedor configurado en Cloud Run; no necesita copiar claves LLM al runner. El pipeline verifica el SHA; resultados locales no reemplazan esta comprobación remota.

La evaluación del RAG y del agente sigue en `docs/07-evaluacion.md`: el resultado histórico estricto del agente es 5/6 listas finales citadas. Los casos HTTP no prueban exhaustividad normativa, persistencia entre revisiones, identidad institucional ni calidad semántica de cada afirmación. El OCR pendiente no se aprueba por ejecutar estas pruebas.

## Producción posterior a limpieza y Neon: JSON completo incorporado

[Actions 42494812366](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42494812366), SHA `ab21d853186ba34acfe8359553a8d38a39de1f80`: **35/35 casos completos y únicos, cero omitidos**, `incluye_modelo=true`, `solo_backend=false`. Fecha del reporte: **2026-11-08 15:29:04 UTC**; p95 de esta corrida **4,327 s**, sin equivalencia a prueba de carga. La revisión obtenida coincide con la esperada. [JSON completo](evidencias/semana-4/produccion-ab21d85-run-42494812366.json).

El propietario descargó el artefacto y adjuntó el archivo; se validó su estructura y resultado antes de versionarlo. [Metadatos y hashes](evidencias/semana-4/cierre-main-ab21d85/actions-metadata.json). No se reutiliza el JSON de `279580e` para acreditar este SHA y no se atribuye este resultado a despliegues posteriores.

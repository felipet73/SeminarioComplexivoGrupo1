# Revisión de observaciones del docente - Entrega 4, Grupo 1

Fecha local: 6 de noviembre de 2026 (algunos informes registran 7 de noviembre en UTC). Referencias: capturas de revisión entregadas por el equipo, guía HTML de Entrega 3 y ejemplo de workflow de la captura de Entrega 4. La ficha del docente revisó main `f8e0a1b`; esta auditoría parte del merge posterior `15a6044` y de los refuerzos preparados localmente. No se reescribe el estado histórico de las evidencias de semana 3.

## Falla crítica: confirmada en el servicio desplegado

`seguridad.py` ya no existe en main desde `08ef882`, y las rutas antiguas no se registran en el código actual. Sin embargo, Cloud Run aún publica esas rutas. Una única prueba de autenticación con la credencial histórica devolvió **200 y presencia de token**. El token se descartó, no se guardaron sus valores y no se ejecutó ninguna operación administrativa. [Evidencia sin secretos](credencial-antigua.json).

El servicio activo necesita reconstrucción y actualización. La incidencia **sigue abierta en producción** hasta comprobar retirada de rutas, commit, revocación y casos funcionales. El nuevo detector AST identifica las credenciales de baja entropía que los patrones anteriores no detectaban. El [informe de historial](historial-credenciales.json) conserva cuatro posiciones en dos versiones del módulo; ese análisis devuelve exit 1. No se borró historial remoto ni se publicó un force push.

El token legacy emitido no demuestra acceso al panel actual `/api/admin`, que utiliza otra autenticación. No se intentó usarlo allí ni se afirma acceso a documentos o modificación de datos.

## Matriz de cumplimiento y límites

| Observación | Estado verificado / implementación | Qué falta para cerrarla |
|---|---|---|
| Credenciales en HEAD | Corregido en main: módulo eliminado, autenticación real con configuración privada; nuevo detector bloquea constantes débiles | Actualizar el servicio; no confundir eliminación en Git con revocación remota |
| Credencial en historial | Auditoría explícita con posiciones y sin valores; no se oculta en ignore | Revocar usos, coordinar limpieza de referencias y clones si se exige historial sin esa ruta |
| Tests debilitados en 0bdb519 | Recuperados antes de esta auditoría: estados exactos, citas, controles de contexto, token **y** done, trazas y límite exacto; sin carga de `.env` con override | Mantenerlos en el flujo de PR; las nuevas pruebas no los sustituyen |
| Solo 3/6 comprobaciones públicas | Frontend/proxy ya corregidos; verificador actual obtiene 6/10 porque exige también readiness, retirada y chat real | Desplegar backend vigente y repetir hasta 10/10 |
| Chat público 500 | Reproducido directo y por proxy; preflight CORS sí correcto. Corrección previa de flujo ya en main; backend actual local responde | Desplegar; consultar traceback de Cloud Logging si persiste. No se afirma una excepción exacta sin logs |
| Despliegue sin pipeline/needs | Job `desplegar`, condicionado a main, con cinco jobs necesarios. Promueve la imagen probada y exige SHA y casos HTTP posteriores | Configurar proyecto, Artifact Registry y WIF o secreto JSON; ejecutar y conservar Actions remoto |
| Docker y ejecución | Usuario no root, PORT, semilla sin claves, exclusión de credenciales, revisión de build; comandos en README/docs | Aplicar la imagen al servicio existente; no se hizo un cambio remoto |
| `docs/08-pruebas.md` | Creado con 34 casos, denominadores, criterios exactos, comandos y límites | Evidencia posterior al despliegue, sin cambiar expectativas para maquillar fallos |
| 15+ casos reales contra URL, incluida inyección | Ejecutados **34**: **23 aprobados**, 11 fallidos, sin omitidos. [Reporte](pruebas-url-inicial.json) | 32/32 contratos y, con el caso SSE generativo añadido, 35/35 incluyendo generación; p95 actual solo describe una corrida con fallos |
| Presentación PDF | Resumen de sustentación en `docs/presentacion-entrega4.pdf`, con resultados reales y pendientes | Revisión y preparación oral del equipo |
| Evidencias semana 4 | Directorio creado con informes de producción, seguridad, historial y validaciones | Añadir la corrida remota posterior a la nueva revisión |
| Límite de consultas inexistente | Presupuesto global de 30 POST por 60 s y proceso, compartido por chat/stream/agente; 429 y Retry-After expuesto por CORS; pruebas de ventana, alias y proveedor no ejecutado | No es una cuota distribuida ni por usuario. Reiniciar o escalar reinicia/amplía presupuesto; requiere control de plataforma si crece |
| Decisiones sin actualizar | ADR actualizado con límite, identidad de commit, despliegue e historial; alcance y limitaciones explícitos | Validación del equipo |
| Uso de IA por integrante | README distingue cuentas Git observadas y solicita declaración individual; no se inventa autoría humana ni uso de herramientas | Cada integrante debe completar/confirmar su declaración real |
| Corpus institucional sin aprobar | PDF/OCR preservados, `approved=false`, 86 fragmentos no elegibles | Revisión humana integral del OCR y aplicabilidad; no se aprueba automáticamente |
| Resultado agente real 5/6 | Se conserva el criterio estricto, trazas históricas y abstención de complexivo | Fuente institucional aprobada y repetición real de seis casos. La evaluación pública no reemplaza ese ensayo |
| SQLite local sin volumen | Semilla reproducible y límite documentado; no se afirma persistencia por tener RAG_DATA_DIR o max-instances 1 | Infraestructura duradera para cargas/decisiones; no se monta SQLite en FUSE como arreglo ficticio |

## Evidencia de GitHub y alcance de esta intervención

La [ejecución 42310236801](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42310236801) de la corrección anterior aprobó backend, frontend, navegador y contenedor. La evaluación real fue omitida por el evento push; no se informa como aprobada. El merge está en main `15a6044`.

Los cambios locales del equipo en workflow/smoke se conservaron en `respaldo/propuesta-ci-semana4-2026-11-06`, commit `03f0a4c`, antes de completarlos en `fix/entrega4-seguridad-y-despliegue`. No se desplegó, modificó IAM ni se publicó esa rama durante esta revisión. Se requiere configuración de Google Cloud para cerrar la incidencia del servicio real.

## Validación del código preparado

| Verificación | Resultado |
|---|---|
| Pytest Windows/Python 3.10.6 | 99/99, 88,73 % |
| Pytest Linux/Python 3.12.16 en imagen sin .env | 99/99, 88,73 % |
| Frontend Vitest y build TypeScript/Vite | 18/18 y build aprobado |
| Playwright con API real aislada y modelo doble | 10/10 |
| Ruff y actionlint | Aprobados |
| Detector de credenciales del código activo | Exit 0 |
| Gitleaks con `--all`, patrones predeterminados y redacción | Exit 0; [informe](gitleaks-historial.json) vacío. No detecta la credencial débil legacy, por eso se añade AST |
| Auditoría explícita del historial legacy | Exit 1, riesgo histórico pendiente |
| Imagen local, smoke con SHA | Aprobado; `/health` identifica `4e7a8c9cfe952ed61beb66871454f8bb732b504a`, rutas antiguas 404 y rechazo SSE correcto |
| Casos HTTP contra imagen local | 28/28 de backend sin generación; se excluyen explícitamente cuatro rutas Vercel y dos casos LLM |
| Casos HTTP contra producción | 23/34, sin omitidos; incidencia abierta |

[Resumen verificable](validacion-local.json), [pytest local](pytest-local.xml), [pytest Linux](pytest-linux.xml), [cobertura Linux](cobertura-linux.json) y [contratos de imagen](pruebas-contenedor.json). La comprobación del SHA también rechazó un identificador distinto antes de repetirla con el SHA completo correcto. Los dos contenedores de aplicación de las pruebas terminaron y no se modificó el servicio remoto.

La primera versión del conjunto HTTP tenía dos expectativas mal preparadas: GET a una ruta que solo acepta POST y un login inválido antes del guard CSRF. Se corrigieron ruta/cuerpo a operaciones válidas y se repitió la corrida completa; el informe publicado usa las expectativas corregidas. No se aceptaron estados alternativos ni se cambiaron los resultados esperados para ocultar fallos del backend.

Para regenerar el PDF en un entorno de documentación: instalar `docs/requirements.txt` y ejecutar `python scripts/generar_resumen_entrega4.py`. Sus seis páginas se renderizaron e inspeccionaron; los PNG intermedios quedan en `tmp/pdfs/entrega4/` y no forman parte del artefacto de entrega.


## Complemento de las capturas del docente — 7 de noviembre de 2026

Se contrastaron las tres capturas aportadas con la rama `fix/entrega4-seguridad-y-despliegue`, base `7476e3f`. Los porcentajes de las capturas describen la revisión histórica; no se sustituyen por un porcentaje de cumplimiento estimado.

- **Falla crítica / secretos:** el módulo y las rutas legacy ya están retirados del código. El detector activo y su prueba cubren constantes débiles; la auditoría histórica sigue fallando de forma explícita. Sigue pendiente revocación y verificación remota de todas las revisiones accesibles. No se reescribió el historial ni se reutilizó la credencial para probar autenticación.
- **Pruebas debilitadas:** se conservan estados exactos, citas, campos/opciones de contexto, eventos token y done, trazas y bloqueo de proveedores reales en pytest. Los cambios de este complemento añaden regresiones del verificador, sin relajar aserciones ni umbrales existentes.
- **Pipeline / chat 500 / URL pública:** el despliegue exige ahora los 35 casos, con dos consultas generativas directas y una por Vercel SSE. El verificador requiere texto, modelo identificado y cita correcta; readiness y rechazo de inyección no sustituyen generación. La lectura SSE admite respuestas citadas mayores de 8 KiB con un límite de 1 MiB. Un fallo posterior al deploy exige intervención y no restaura automáticamente una revisión antigua vulnerable.
- **Docker, documentación, PDF y evidencias:** ya existen Dockerfile sin privilegios, exclusión de credenciales, semilla léxica, documentación de build/start, `docs/08-pruebas.md`, presentación PDF y evidencia histórica en semana 4. Se conserva la distinción entre pruebas locales y servicio publicado; el PDF previo no acredita ejecución de este complemento.
- **Límite de tasa y decisiones:** presupuesto global por proceso de 30 consultas/minuto ya probado y documentado; no equivale a control distribuido, cuota por usuario ni persistencia duradera.
- **Corpus / agente real / autoría:** aprobación del OCR, incorporación de normativa aplicable, repetición de las seis consultas reales y declaración individual del uso de IA siguen requiriendo al equipo. Se conserva el resultado histórico 5/6 y no se rebaja el criterio para obtener 6/6.

### Condiciones externas de cierre

Configurar/revisar WIF y variables de GitHub, protección del entorno `production`, secretos de ejecución de Cloud Run, rotación de valores expuestos y tráfico a la revisión corregida. Después ejecutar el pipeline y conservar SHA y reporte de 35/35 contra ambas URLs. En este chat GitHub API y Cloud Run devolvieron 403 por la política de acceso: no hay una comprobación remota nueva ni un despliegue acreditado. No se modificó ni publicó la configuración del entorno cloud.

### Evidencia local del complemento

[Reporte reproducible con hashes de los archivos verificados](complemento-revision-2026-11-07.json): 104 pruebas backend aprobadas, cobertura 88,73 %, Ruff y detector activo aprobados. Tras ajustar el límite de lectura SSE se repitieron las 13 pruebas del verificador: 13/13. Las pruebas de generación real contra las URLs públicas no se ejecutaron; 35 es el conjunto exigido por el pipeline, no un resultado remoto aprobado. El frontend y la imagen no cambian en este complemento.

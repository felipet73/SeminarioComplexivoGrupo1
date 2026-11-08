# Verificación del diagnóstico de cierre de la credencial legacy

> Corte histórico: para el estado posterior a la publicación de ramas y los pendientes de PR/cachés, consultar [la constancia vigente](24-cierre-historial-publicado.md). Los resultados anteriores no se reetiquetan.

Revisión sobre `main` **`e3e8b22545724af521b7b35bf4d60590cfaa13fe`**. Este documento contrasta evidencia existente; no prueba contraseñas antiguas, no muestra valores secretos y no realiza cambios de IAM ni reescritura de historial.

## Resultado: diagnóstico mayormente correcto, con actualizaciones

| Afirmación | Verificación actual | Estado |
|---|---|---|
| La credencial legacy funcionó | `credencial-antigua.json` registra HTTP 200 el 7/11 a las 03:44:36 UTC (6/11 a las 22:44:36 de Ecuador). Se conserva esa evidencia anterior; no se repitió el login. El código histórico usa literales para JWT y contraseña. | Confirmado como hallazgo histórico documentado. |
| Módulo eliminado en `08ef882` | El historial muestra retirada del archivo; no existe ni se registra en el código actual. | Corregido en HEAD. |
| Solo hay comprobación posterior del SHA `0dab82d` | Además de aquella, Actions **42422021200** aprobó el despliegue de **`e3e8b22`**, incluido smoke de SHA/rutas antiguas y los casos públicos con generación. | Hay evidencia remota más reciente. |
| No hay JSON completo versionado posterior al cierre | Los JSON por caso versionados siguen siendo el inicial 23/34 y el contenedor 28/28. Hay resúmenes posteriores y el nuevo PDF de evidencias, pero no sustituyen el JSON completo exitoso. | Pendiente de adjuntar el reporte completo. |
| Clave y contraseña recuperables del historial | Se conservan las referencias `1348b06:backend/app/seguridad.py:10,20` y `3e38895:9,19`. Las seis exclusiones de Gitleaks corresponden a un advisory y su reporte, no a esos valores. | Pendiente de remediación coordinada del historial. |
| No hay rotación/no reutilización acreditadas | No se encontró constancia específica para contraseña/clave JWT legacy. Configurar nuevas claves Gemini/OpenAI no demuestra rotación de aquellos valores. | No acreditado; requiere actuación del equipo. |
| No hay secretos nuevos reconocibles en `f8e0a1b..e3e8b22` | Se revisaron líneas añadidas de 23 commits con formatos reconocibles, sin coincidencias; detector activo aprobado. Los dos PDF de `e3e8b22` contienen infografías y capturas revisadas visualmente, sin valores de credenciales identificados. | Sin hallazgos dentro de ese alcance; no prueba ausencia universal de secretos o datos personales. |
| Hay que ampliar aportes por integrante | README ya incluye responsabilidades, herramientas de IA y declaración común de ejecución local, PR y pruebas locales/remotas confirmadas por el equipo. | Ampliación realizada; aún pueden añadirse ejemplos concretos de revisión de IA y PR por integrante si se necesitan. |
| Faltan observaciones de sustentación | `observaciones-sustentacion.md` conserva el registro vacío, sin observaciones reales aportadas. | Pendiente; no deben inventarse. |
| Falta evaluación final real comparable | No aparecen ejecuciones del workflow independiente `evaluacion-final.yml`; en el último CI `evaluacion-real` quedó omitido. El baseline léxico final ya se repitió; la evaluación híbrida/chat/agente final no está acreditada. | Parcial. |
| Hay que reducir ZIP a 20 MB | Medición de main `e3e8b22`: **28.722.097 bytes, 27,39 MiB**, mayor que el límite de 20.000.000 bytes; exit 1 y sin ZIP entregable. Los dos PDF incorporados aumentaron el tamaño respecto al corte anterior de 24,82 MiB. | Pendiente. |

## Qué prueba Actions y qué documento falta

La API de GitHub confirma success en [Actions 42422021200](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42422021200), commit completo `e3e8b22545724af521b7b35bf4d60590cfaa13fe`. Los pasos **Verificar revisión, corpus, rutas retiradas y chat** y **Casos funcionales contra las URLs públicas** aprobaron. El smoke exige revisión exacta y 404 en ambas rutas legacy; el runner exige todos los casos seleccionados, incluidos tres generativos. Esta evidencia acredita los controles de esa URL/revisión, no revocación en otras copias.

El artefacto vigente se llama `evidencias-despliegue-e3e8b22545724af521b7b35bf4d60590cfaa13fe`. La descarga desde el chat fue rechazada por la política de red hacia `productionresultssa1.blob.core.windows.net`. Las conexiones directas a Cloud Run y Vercel también están bloqueadas aquí. Se documentan las restricciones en lugar de fabricar un JSON completo o afirmar una nueva ejecución directa.

**Forma más rápida de completar la evidencia:** descargar el artefacto desde Summary → Artifacts y versionar su `results-produccion-funcional.json` con nombre fechado dentro de `docs/evidencias/semana-4/`. Comprobar fecha, revisión esperada, 35 casos, cero omitidos y que cada caso sea correcto. Conservar los reportes fallidos anteriores.

También se puede repetir desde un computador con acceso. En PowerShell, desde la raíz de `main`, con cambios locales preservados y después de esperar el despliegue de esa revisión:

```powershell
git switch main
git pull --ff-only
$revision = git rev-parse HEAD
python scripts/pruebas_funcionales.py --incluir-modelo --expected-revision $revision --output docs/evidencias/semana-4/produccion-verificada.json
$LASTEXITCODE
```

Se espera exit 0, 35/35, cero omitidos y SHA coincidente. El comando consume el proveedor del backend. Si main tiene un commit aún no desplegado, no cambiar el SHA esperado para ocultar el fallo: esperar o comprobar la revisión y el resultado de Actions. Al versionar la evidencia, esta sigue acreditando el SHA que contiene el reporte, aunque el commit documental posterior tenga otro identificador.

## Constancia de no reutilización o rotación

El equipo debe revisar **sus entornos reales** sin publicar valores. Registrar: fecha/hora de Ecuador, responsable, servicio/proyecto y entorno revisados, nombre del secreto o configuración, acción tomada (no reutilización comprobada o rotación), revisión desplegada y validación de retirada de rutas. Una captura de nombres/referencias/versión, sin el contenido del secreto, puede acompañar el registro. No copiar hashes de contraseñas débiles ni valores al informe.

La revisión actual no consume la clave JWT antigua y no registra sus rutas, por lo que aquellos valores no sirven para ese mecanismo en la URL comprobada. Quedan por revisar reutilizaciones y revisiones/URLs antiguas accesibles. La confirmación declarativa del responsable y una evidencia de cambio de configuración deben distinguirse de una prueba criptográfica o una auditoría de todos los servicios.

Para cumplir literalmente “historial limpio”, acordar con el docente y el equipo el alcance de la limpieza: respaldo seguro, inventario de ramas/tags y referencias de PR/cachés, reescritura coordinada y actualización de clones. No se realiza force push en esta revisión. Añadir la credencial a `.gitleaksignore` no cierra este requisito.

## Orden recomendado antes de la entrega

1. Adjuntar JSON exitoso completo del SHA publicado y registrar la actuación sobre los valores legacy; ninguno exige divulgar secretos.
2. Configurar las claves requeridas en Secrets de Actions y ejecutar **Evaluación final sin despliegue**. Conservar errores y comparar mismas métricas/golden set frente a semana 3. No rebajar el criterio estricto del agente ni aprobar OCR para hacer pasar pruebas.
3. Resolver el corpus/paquete con el docente y medir con `scripts/empaquetar_entrega.py` hasta exit 0. Imágenes de documentación no bastan; preservar firmas, hashes, orden de páginas y la capacidad de ingesta.
4. Registrar observaciones reales del tribunal y correcciones con commit; complementar aportes con ejemplos de PR/revisión si los integrantes los proporcionan.

La entrega oficial es el **lunes 9 de noviembre de 2026 a las 23:59 de Ecuador**, con prórroga indicada por el docente hasta el miércoles 11 a las 23:59. Una ejecución de CI verde no convierte los pendientes anteriores en cumplidos.

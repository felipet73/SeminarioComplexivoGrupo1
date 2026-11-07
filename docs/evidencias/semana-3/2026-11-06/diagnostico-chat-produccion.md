# Chat de producción: HTTP 500 mostrado como error CORS

> **Registro histórico:** conserva criterios, cifras y pendientes de su fecha; no es el estado actual. Consultar el [checklist vigente s4a–s4k](../../../14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

Verificación: 6 de noviembre de 2026, hora de Ecuador. El informe [produccion-chat-500.json](produccion-chat-500.json) registra la fecha UTC y las respuestas del despliegue real.

## Lo comprobado

| Comprobación remota | Resultado |
|---|---|
| Frontend, `/admin` y `/metricas` en Vercel | 200 HTML |
| Proxy de Vercel `/api/admin/session`, sin sesión | 401 JSON esperado |
| Cloud Run `/health` | 200 |
| Preflight de `/api/chat/stream` con origen Vercel | 200 y `Access-Control-Allow-Origin` con el dominio exacto |
| Consulta válida pero rechazada localmente, directo a Cloud Run | **500**, sin cabecera CORS |
| Misma consulta a través del proxy Vercel | **500** |
| Cloud Run `/ready` | **404**, ruta presente en main |
| Antigua ruta administrativa | GET devuelve **405**; el OpenAPI desplegado todavía declara el POST retirado |

La consola del navegador muestra CORS porque la respuesta 500 no lleva esa cabecera. El preflight sí permite el dominio; cambiar el origen permitido no corrige la excepción del backend. La comprobación mediante el proxy obtiene el mismo 500 sin depender de CORS en el navegador.

La URL del backend incorporada al JavaScript público coincide con la proporcionada por el equipo. Las rutas y el proxy de Vercel ya funcionan. Cloud Run presenta un contrato anterior al código actual: `/ready` falta y aún aparecen `/admin/login` y `/admin/recargar-reglamentos` en su OpenAPI.

## Estado del repositorio y diagnóstico

El merge de correcciones ya está en `origin/main`, commit `15a6044`. La [ejecución de Actions de la rama corregida](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42310236801) terminó con backend, frontend, navegador y contenedor aprobados; evaluación real omitida conforme al evento push.

El historial anterior contiene una regresión en `backend/app/flujo.py`: reconstruía una respuesta sin los campos obligatorios `estado` y `tiempo_segundos` cuando no tenía fuentes. El flujo actual devuelve el contrato completo y permite abstenciones, aclaraciones y rechazos sin citas. Esa regresión es compatible con el 500 observado incluso al pedir un rechazo local. **La excepción exacta de la revisión desplegada requiere su traceback en Cloud Logging**; no se ha accedido a esos logs ni se afirma que esa sea la única causa posible.

La corrección operativa pendiente es reconstruir y desplegar el backend desde el main actualizado, comprobando el commit de la revisión y el origen de la imagen. Para el contenedor preparado en este repositorio, el contexto de build es la raíz y el Dockerfile es `backend/Dockerfile`. El método concreto depende de si se usa un repositorio conectado, Cloud Build o una imagen de Artifact Registry. No se modificaron Cloud Run ni sus variables de entorno.

## Mejora de la verificación

El verificador anterior podía dar 6/6 con el chat roto porque solo comprobaba rutas, salud y preflight. Ahora también exige readiness y ausencia de la ruta retirada. Su opción `--chat-smoke` comprueba el SSE de una petición que debe rechazarse antes de buscar documentos o llamar a proveedores, tanto directamente como por el proxy. No guarda el texto generado ni capacidades de confirmación; registra estado, presencia de evento final y ausencia de fuentes. Puede generar métricas de consultas de prueba.

```powershell
backend/.venv/Scripts/python.exe scripts/verificar_produccion.py --chat-smoke --output eval/results-produccion.json
```

Resultado remoto observado: **6/10**, exit 1. Las cuatro comprobaciones que fallan son readiness, retirada de ruta antigua, chat directo y chat por proxy. El resultado no se presenta como despliegue aprobado.

`scripts/smoke_container.py`, ejecutado por CI, también exige ahora un evento SSE final de rechazo válido. Tres regresiones nuevas comprueban el recorrido completo contra la API local, un servidor con CORS correcto y chat 500, y un flujo truncado sin evento final. Bloquean recuperación y proveedores para acreditar que este smoke no depende del modelo.

La imagen local `titulacion-rag:ci-main`, con el código corregido y 961 fragmentos habilitados, aprobó health, readiness, herramientas, cálculo y **chat SSE** con la comprobación reforzada. El contenedor temporal fue detenido. Esto acredita la imagen probada; la revisión remota continúa pendiente de actualización.

Validación del refuerzo: suite completa Windows **86/86**, cobertura **88,50 %**; los diez casos del verificador y endpoints también aprobaron en Linux/Python 3.12. Ruff y el detector de patrones de secretos aprobaron. Los cambios del smoke y las evidencias se conservaron en la rama local `fix/verificacion-chat-produccion`; el arreglo del flujo de aplicación ya está en main.

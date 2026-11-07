# Configuración del backend de producción — 6 de noviembre de 2026

> **Registro histórico:** conserva criterios, cifras y pendientes de su fecha; no es el estado actual. Consultar el [checklist vigente s4a–s4k](../../14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

Actualización posterior: el frontend y su proxy ya responden correctamente, pero Cloud Run devuelve 500 en el chat y conserva rutas de una versión antigua. Véase el [diagnóstico del chat desplegado](2026-11-06/diagnostico-chat-produccion.md). El comando de verificación agrega ahora readiness y retirada de ruta; `--chat-smoke` permite comprobar también el SSE sin usar un proveedor. Los resultados 3/6 de esta página corresponden a la comprobación histórica anterior.

El equipo indicó como URL del backend `https://titulacion-rag-386902880383.us-central1.run.app/`.

Se añadió `frontend/.env.production` con `VITE_API_URL=https://titulacion-rag-386902880383.us-central1.run.app`. Vite la incorpora durante el build; el desarrollo conserva su backend local. Las variables del proceso de build pueden sobrescribir el archivo. El cliente normaliza espacios y barras finales para evitar rutas dobles. Chat, métricas, confirmación y enlaces a fuentes comparten esta configuración. También se retiraron direcciones localhost fijas del componente administrativo antiguo, que no forma parte del enrutador activo.

Se añadió `frontend/.env.example` con valores locales y se ajustó `vite.config.ts` para leer las variables del proxy de desarrollo mediante `loadEnv`. Las excepciones de Git/Docker se limitan al archivo público `.env.production`; no se incorporaron claves ni archivos `.env.local`.

Validaciones realizadas:

- Vitest: 18 pruebas aprobadas, incluidas solicitudes al host configurado con y sin barra final.
- TypeScript y build Vite: aprobados.
- Playwright: dos escenarios administrativos aprobados, incluyendo login, fuentes, indexación, análisis y vista móvil; API local aislada, sin consumir producción.
- Inspección del JavaScript compilado: contiene la URL indicada y no contiene `http://localhost:8000` ni `http://127.0.0.1:8000` como backend.
- Consulta HTTPS a `/health`: HTTP 200, servicio `titulacion-rag-api`, versión `2.0.0`. No se hicieron consultas a modelos ni escrituras en producción.

## Comprobación con la URL del frontend confirmada

El equipo confirmó `https://seminario-complexivo-grupo1.vercel.app/`. La inspección pública dio **3/6 comprobaciones correctas**:

| Comprobación remota | Resultado |
|---|---|
| Página principal de Vercel | 200 HTML |
| Backend `/health` | 200 JSON |
| Preflight del chat desde el origen Vercel | 200, origen exacto permitido, sin credenciales cruzadas |
| Apertura directa de `/admin` | 404 |
| Apertura directa de `/metricas` | 404 |
| `/api/admin/session` en Vercel, sin sesión | 404; debería ser 401 JSON del backend |

El informe crudo está en `produccion-http-2026-11-06.json`. No se atribuyen estos fallos a CORS: el problema observado son las rutas y el proxy de Vercel. No se hicieron intentos de login con credenciales reales.

Se añadió `frontend/vercel.json` (Root Directory de Vercel: `frontend`). Primero reescribe `/api/:path*` a Cloud Run conservando el prefijo `/api`, después aplica el fallback SPA a `index.html`. Sigue el mecanismo oficial de [rewrites externos](https://vercel.com/docs/routing/rewrites) y [rutas SPA Vite](https://vercel.com/docs/frameworks/frontend/vite). El chat conserva la URL pública configurada; la administración usa el origen Vercel y su cookie de sesión.

Se ajustó `mutation_guard`: cuando el proxy cambia `Host`, el `Origin` del navegador debe coincidir exactamente con un origen configurado. Se mantienen `X-Admin-Request`, validación de credenciales, expiración, HttpOnly y SameSite=Strict. Un comodín, dominios parecidos y `X-Forwarded-Host` falsificado no autorizan operaciones. La lista de orígenes normaliza la barra final. La API pública mantiene CORS sin credenciales.

El proxy local ahora cambia `Host` hacia el backend; la configuración del servidor E2E declara explícitamente su frontend local. Esto permite comprobar con navegador el flujo real de cookie y CSRF a través de dos hosts/puertos diferentes, usando únicamente datos y modelos de prueba.

Las variables correspondientes del backend de Cloud Run son:

```dotenv
APP_ENV=production
CORS_ORIGINS=https://seminario-complexivo-grupo1.vercel.app
ADMIN_COOKIE_SECURE=true
```

El origen CORS ya fue observado como permitido en el despliegue existente. Las demás variables no se infieren de una respuesta de salud ni se modificaron remotamente. Debe publicarse el frontend con `vercel.json` y el backend con el guard actualizado; las correcciones están en el repositorio local, no se presentan como un despliegue realizado.

Para repetir la comprobación sin credenciales ni llamadas a modelos:

```bash
python scripts/verificar_produccion.py --output eval/results-produccion.json
```

El script usa solo GET/OPTIONS y devuelve exit 1 mientras falte alguna ruta/contrato esperado. Actualmente conserva el resultado 3/6, sin convertir los 404 en éxito. No valida login real, persistencia ni proveedores de IA.

Tras los cambios de origen y proxy, pytest aprobó **75 pruebas con 88,43 % de cobertura** en Windows/Python 3.10. El nuevo conjunto prueba sesión completa por proxy HTTPS, flags de cookie, origen falso o malformado, cabecera CSRF ausente, comodín y preflight. Resultados en `tests-cors-produccion-2026-11-06.xml` y `cobertura-cors-produccion-2026-11-06.json`.

Se repitió la suite en Linux/Python 3.12 dentro de la imagen de verificación, montando únicamente código y casos de prueba, sin `.env` ni credenciales: **75/75 y 88,43 %**. Informe en `tests-cors-linux-2026-11-06.txt`.

La verificación final del frontend aprobó **18 pruebas Vitest, build TypeScript/Vite y los 10 escenarios Playwright**. En esta corrida el proxy local ya cambia `Host` hacia el backend: login, subida de documentos, indexación, análisis, logout y vistas móviles se ejercitan con `Origin` del frontend distinto de `Host` del backend. Las credenciales y el modelo son dobles de prueba; no se atribuye esta corrida al login de producción.

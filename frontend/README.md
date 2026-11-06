# Frontend

El formulario de fuentes incluye «Cancelar»: al editar/reemplazar sale de esa acción y vuelve al alta limpia; al agregar limpia campos, archivo, casillas y errores. No guarda ni elimina documentos, y permanece deshabilitado durante el guardado.

RAG y Análisis muestran diagramas de nodos sincronizados con pasos y datos devueltos por backend. Los botones «?» ofrecen ayuda ampliada para configurar e interpretar cada proceso. Las simulaciones generan respuestas y mediciones, **sin evaluación adicional con IA**. Ver [ayudas y trazas](../docs/10-ayudas-y-trazas-rag.md).

Las tarjetas de Configuración, RAG y Análisis se contraen/expanden con animación y controles accesibles; el contenido sigue montado para conservar los borradores. «Nueva fuente» reinicia el formulario incluso si ya está en modo nuevo: borra campos, archivo y errores, restablece las casillas, expande el editor y enfoca el título. Guardar una fuente nueva también deja el formulario limpio. No se permite reiniciarlo durante su guardado.

Las preguntas sugeridas públicas no incluyen pruebas adversarias. Estas se encuentran en `/admin`, pestaña Análisis, cuya simulación muestra burbujas por caso y versión con métricas. Cada aclaración del chat conserva un botón para reabrir sus campos pendientes; las simulaciones permiten repetir el caso con contexto para todas las versiones.

Cuando la IA solicita datos faltantes, el chat muestra su respuesta también en un popup con campos validados. Permite volver a consultar con la pregunta/modelo/contexto originales o salir sin consultar. Los valores se conservan ante errores. Ver [campos necesarios](../docs/09-aclaraciones-y-campos-necesarios.md); cubierto por `npm run test` y `npm run test:admin`.

`/admin` abre el login administrativo y las pestañas Configuración / RAG / Análisis. Usa `/api/admin` a través del proxy Vite al backend 8000 (reinicia Vite tras actualizar esta configuración). Usuario por defecto `admin`, contraseña definida únicamente en `.env` del repositorio. No hay claves ni tokens de sesión en localStorage.

Pruebas completas del administrador: `npm run test:admin` levanta servidores aislados 9019/4180, fuentes temporales y LLM doble. Consulta [manual de administración](../docs/08-admin-rag-y-analisis.md). En producción configura reverse proxy `/api/admin` en el mismo origen, HTTPS y `ADMIN_COOKIE_SECURE=true`.

El selector muestra Gemini 3.5 Flash-Lite como primera opción y OpenAI GPT-4.1 mini como alternativa. El backend usa 15 segundos por llamada, sin reintentos adicionales antes del respaldo.

La ruta `/` muestra la orientación con contexto académico opcional y selector de modelo. `/metricas` muestra el dashboard público (sin login ni enlace de menú), alimentado por `GET /api/metricas`. Abre `http://localhost:5173/metricas` con el backend activo. Los campos elegidos se envían con cada nueva consulta y se mantienen solo en memoria durante la página actual.

Verificación de navegador: `npm run test:e2e` (instalar Chromium una vez con `npx playwright install chromium`). El servidor de producción debe redirigir las rutas del frontend a `index.html` para abrir `/metricas` directamente.

Cliente Vite + React 19 + TypeScript. Lee el stream SSE de `POST /api/chat/stream`; no conoce claves ni llama a proveedores de IA.

```powershell
npm install
npm run dev
npm run test
npm run build
```

El backend debe estar en `http://127.0.0.1:8000`. Para otro host, cree `frontend/.env.local` con `VITE_API_URL=http://host:puerto`. `npm run tipos` genera tipos desde `/openapi.json` con el backend activo.

## Variables de producción

`frontend/.env.production` contiene la URL pública del backend:

```dotenv
VITE_API_URL=https://titulacion-rag-386902880383.us-central1.run.app
```

`npm run build` carga esa configuración; `npm run dev` conserva el backend local. Vite incorpora la URL al compilar: cambiar variables en el servidor después del build requiere reconstruir el frontend. Una variable `VITE_API_URL` definida por el entorno de build tiene prioridad sobre el archivo. El cliente elimina espacios y barras finales para formar las rutas correctamente.

El frontend de producción es `https://seminario-complexivo-grupo1.vercel.app`. Chat, métricas, confirmación de borradores y enlaces a fuentes usan la URL de backend indicada. El administrador activo conserva `/api/admin` en el origen de Vercel y su cookie de sesión.

`frontend/vercel.json` configura el proyecto Vite con **Root Directory `frontend`**, build `npm run build` y salida `dist`. Sus reglas envían primero `/api/:path*` a Cloud Run, conservando `/api`; después resuelven rutas SPA como `/admin` y `/metricas` con `index.html`. No hay una función intermedia ni se guarda un token en el navegador. Ver [rewrites externos](https://vercel.com/docs/routing/rewrites) y [rutas SPA de Vite](https://vercel.com/docs/frameworks/frontend/vite).

En las variables del servicio **backend de Cloud Run** usar:

```dotenv
APP_ENV=production
CORS_ORIGINS=https://seminario-complexivo-grupo1.vercel.app
ADMIN_COOKIE_SECURE=true
```

La lista CORS se usa también para validar el `Origin` administrativo cuando el proxy presenta un `Host` distinto. Se exige `X-Admin-Request: 1`; los dominios ajenos, subdominios parecidos y un comodín no autorizan acceso administrativo. La cookie continúa `HttpOnly`, `SameSite=Strict` y sin `Domain`, para que el navegador la asocie al origen Vercel de la respuesta proxificada. La API pública mantiene las solicitudes CORS sin credenciales.

`VITE_ADMIN_API_TARGET` configura únicamente el proxy local de Vite. Las reglas de Vercel se aplican cuando se publica el frontend; la validación nueva de origen se aplica al publicar el backend. Antes de esos cambios, la comprobación remota encontró CORS público permitido y `/api/admin/session` devolviendo 404 en Vercel. Se necesita publicar ambas revisiones para verificar el flujo completo del administrador.

Las variables `VITE_*` son públicas en el navegador. Las credenciales de Gemini, OpenAI y administrador se configuran exclusivamente en el backend.

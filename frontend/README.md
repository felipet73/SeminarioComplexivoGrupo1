# Frontend

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

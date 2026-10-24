# Frontend

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

# Implementación de Semana 2

> **Registro histórico:** conserva criterios, cifras y pendientes de su fecha; no es el estado actual. Consultar el [checklist vigente s4a–s4k](14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

- Backend FastAPI con contrato OpenAPI, JSON y streaming SSE.
- Gemini principal y OpenAI de respaldo, reintentos, límite de entrada y log sin texto personal.
- Salvaguardas de dominio e inyección antes del modelo.
- Tres prompts y diez entradas de evaluación.
- Frontend Vite, React 19 y TypeScript con `useActionState`, `useOptimistic`, `useEffectEvent` y `Activity`.
- Pytest con dobles, Vitest para SSE y errores HTTP, y Playwright para el flujo visible.

No hay RAG ni fuentes aprobadas: el backend responde `fuentes=[]`, no afirma requisitos o plazos oficiales y requiere revisión humana. Eso se activa solo después de validar e indexar normativa en Semana 3.

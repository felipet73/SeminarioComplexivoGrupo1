# Contexto académico, observabilidad y revisión de cumplimiento

Este documento registra el corte anterior a la administración. La actualización de prompts, RAG persistente y laboratorio se detalla en [08-admin-rag-y-analisis.md](08-admin-rag-y-analisis.md); sus brechas reemplazan las entradas históricas que ahora están implementadas.

Fecha: 24 de octubre de 2026. Revisión del código frente a `docs/01-propuesta.md`, `02-requisitos.md`, `03-arquitectura.md`, `04-fuentes.md`, `05-prompts.md` y las condiciones de Semana 2 registradas en `06-semana-2-implementacion.md`. Esto es una revisión técnica, no una aprobación docente o institucional.

Actualización de disponibilidad: Gemini 3.8 Flash presentó 503/504. Se sustituyó por `gemini-3.5-flash-lite` tras dos pruebas con el system prompt real y contexto ficticio de Software: 6,94 s / 564 tokens y 5,57 s / 610 tokens, ambas con texto. Esto verifica disponibilidad puntual, no calidad normativa ni disponibilidad garantizada. Se redujo el timeout por llamada a 15 s y los reintentos a cero, conservando OpenAI como respaldo. Referencia de modelo: https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite

## Cambios implementados

- Contexto opcional: carrera (texto con sugerencias), nivel/curso, sede, modalidad de estudios, modalidad de titulación, período, jornada, tema y objetivo de ayuda. Las listas son orientativas; solo se sugiere Software por ser la carrera del caso y se admite escritura libre. No se atribuye un catálogo oficial a UNIANDES.
- El frontend envía esos campos en JSON a `POST /api/chat` o `/api/chat/stream`; Pydantic limita su tamaño. El servicio envía `consulta` y `contexto_declarado` al modelo; el system prompt los trata como datos autodeclarados. Se distingue modalidad de estudios de modalidad de titulación.
- Ayudas posibles: explicar términos, organizar preguntas para Secretaría, identificar información faltante y proponer próximos pasos orientativos. No certifica estados ni emite decisiones administrativas.
- Selector Gemini/OpenAI con respaldo en ambos sentidos. Timeout por llamada y reintentos solo en límites, timeout o errores de proveedor; SDK sin reintentos automáticos adicionales.
- Dashboard público `/metricas`, sin enlace en la navegación principal y sin autenticación por petición del equipo. Cualquier visitante que conozca la ruta puede leer los metadatos. `GET /api/metricas` también es público.
- Persistencia JSONL en `logs/metrics.jsonl` con rotación a 5 MB y tres respaldos. Vista acotada a últimos 2000 eventos; actividad reciente de 50. Los logs están ignorados por Git. Pensado para el servidor local de un proceso; centralizar almacenamiento antes de usar varios workers/instancias.
- Eventos `llm` por intento y `consulta` por resultado final, relacionados por UUID. Incluyen fecha UTC, modelo, preferido, respaldo, tiempo, tipo de respuesta y error clasificado. Validaciones 422 y rechazos locales también cuentan como consultas.
- Tokens de entrada/salida/total provienen del SDK; `null` significa no reportado. Los errores normalmente no reportan tokens. El total puede incluir razonamiento interno del proveedor; no se deduce costo ni uso no reportado. El consumo de OpenAI usa los campos `usage` de Responses API: https://developers.openai.com/api/reference/python/resources/responses/methods/create
- No se guardan preguntas, respuestas, contexto académico, claves, IP o mensajes crudos de excepciones. El sistema antiguo `logs/llm.jsonl` no se importa al dashboard porque carece de fecha, tipo y tokens.
- Errores visibles del chat incluso después de terminar la acción, distribución de resultados y modelos, latencia media/p95 y filtro de actividad en dashboard.

## Revisión de cumplimiento: pendientes reales

| Prioridad | Falta | Evidencia / requisito |
|---|---|---|
| Alta | Validar vigencia, descargar y versionar LOES/RRA/normas UNIANDES; aprobar fuentes antes de indexar | RF-02, HU-07; inventario aún pendiente y descargas fallidas |
| Alta | Fragmentar por artículo/inciso, recuperar por texto y vectores, filtrar aplicabilidad, validar citas y enlazar evidencia | RF-03/04/05, HU-01/10; actualmente `fuentes=[]` |
| Alta | Implementar `consultar_requisitos`, `calcular_plazo`, `generar_checklist` con reglas verificadas | RF-07, HU-04/05/06; hoy son diseño |
| Alta | Abstención y salida estructurada validadas en código (JSON del LLM); aclaración condicional fiable | RF-06; hoy todas las respuestas generadas se etiquetan `abstencion` sin validar semánticamente el texto |
| Alta | Streaming real desde SDK, cancelación, límites de concurrencia/cuotas por sesión, memoria de conversación en servidor y errores RFC 9457 | Clases/guía Semana 2; hoy SSE divide una respuesta ya generada, no reduce tiempo a primera palabra |
| Alta | Ejecutar 3 prompts × 10 entradas; registrar calificación y ganador; levantar 15 FAQ reales y golden set de 20 preguntas con artículos | HU-09, RF-08; prompts y entradas existen pero no hay resultados reales |
| Media | Generar y consumir tipos OpenAPI; validar respuestas en runtime; completar MSW/componentes, SSE fragmentado, 429/Retry-After con cuenta regresiva, 503, cancelación y recuperación | Guía frontend; tipos del cliente aún manuales y pruebas no cubren todos los estados |
| Media | Medir exactitud ≥16/20 con artículo correcto, abstención/inyección 100% en conjuntos definidos, p95 ≤8 s, disponibilidad 24 h, cobertura ≥80%, accesibilidad axe | RNF-01 a RNF-10; métricas operativas no equivalen a esos resultados |
| Media | Despliegue aprobado HTTPS, persistencia y pruebas URL pública; actualizar arquitectura/ADR y aportes reales/PR revisado | Entrega por fases; documento de arquitectura aún describe Next.js objetivo y Semana 1 |

No se declaran metas cumplidas sin evidencia. Los bloqueos por palabras clave y el prompt actual son salvaguardas parciales: no garantizan rechazo de todas las inyecciones ni ausencia de afirmaciones inventadas.

## Ejecución y pruebas

Desde `backend`: `.\.venv\Scripts\python.exe -m pytest -q`. Pruebas de métricas usan almacenamiento temporal; pruebas LLM usan dobles y nunca claves reales. Desde `frontend`: `npm run build`, `npm run test`, `npm run test:e2e`. El dashboard inicia vacío y se alimenta de consultas posteriores a esta implementación; no se rellenan datos ficticios en producción.

Evidencia local del 24-10-2026: backend 12 pruebas, frontend 8 pruebas y Playwright 3 flujos. Los flujos de navegador comprueban envío de contexto/modelo, respuesta sin duplicación y `/metricas` móvil sin desbordamiento horizontal. Capturas reproducibles en `frontend/test-results/chat-contexto.png` y `metricas-movil.png` (datos simulados solo en tests, archivos ignorados por Git). Chromium se instaló en la caché local de Playwright para ejecutar estos flujos.

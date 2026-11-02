# Registro de decisiones iniciales

| ID | Fecha | Decisi贸n propuesta | Motivo | Estado |
|---|---|---|---|---|
| ADR-001 | 2026-10-19 | Backend FastAPI | Coincide con la recomendaci贸n del material FAQ, facilita ecosistema Python RAG | Propuesta; validar en revisi贸n |
| ADR-002 | 2026-10-19 | Next.js/React | UI modular para chat y documentos | Propuesta |
| ADR-003 | 2026-10-19 | ChromaDB para MVP | 脥ndice vectorial sencillo; evitar infraestructura adicional al inicio | Propuesta |
| ADR-004 | 2026-10-19 | No fijar Gemini 1.5 Flash ni GPT-4o-mini | Modelos mencionados en el documento fuente son recomendaciones hist贸ricas | Pendiente de benchmark |
| ADR-005 | 2026-10-19 | Respuestas 煤nicamente con fuente aprobada y cita verificable | Requisito expreso del caso y control de alucinaciones | Pol铆tica propuesta |
| ADR-006 | 2026-10-19 | 15 FAQ del DOCX son cuestionario, no resultados de campo | Evitar afirmar levantamiento que a煤n no ocurri贸 | Confirmado por contenido recibido |


## Decisi髇 T閏nica: Selecci髇 Multimodelo (Gemini principal con Fallback a OpenAI)
- **Modelo Principal:** Google Gemini 1.5 Flash (alta ventana de contexto y baja latencia).
- **Modelo de Respaldo:** OpenAI GPT-4o-mini (tolerancia a fallos por cuota o latencia).
- **Configuraci髇:** Selecci髇 manual expuesta en el payload y fallback autom醫ico en backend.

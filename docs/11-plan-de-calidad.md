# Plan de calidad de la Entrega 3

> **Corte actual de pruebas:** 147 casos backend aprobados, cobertura de app 89,11 %, según la [ejecución local y conciliación histórica](21-conteos-de-pruebas.md). La evaluación real posterior aprobó 6/6 del agente. El plan de Entrega 3 se conserva; consultar el [checklist vigente](14-checklist-entrega-final.md) para pendientes de Entrega 4.

Se aplican los pasos comunes y específicos del grupo 1 de la guía HTML aportada. La matriz completa está en `docs/12-auditoria-entrega3-grupo1.md`.

| Control | Ejecución | Criterio |
|---|---|---|
| Backend, herramientas y agente A–D | `cd backend; python -m pytest -q --cov=app --cov-fail-under=85` | Todas las pruebas pasan y cobertura de sentencias ≥85% |
| Lint de errores críticos | `python -m ruff check backend scripts eval` | Sin errores E9/F63/F7/F82; no se afirma cobertura de todo PEP8 |
| Frontend | `cd frontend; npm test; npm run build` | Pruebas, tipos y compilación correctos |
| Navegador administrativo y confirmación | `cd frontend; npm run test:admin` | Flujos con servidor aislado y modelo doble; no consume proveedores |
| Recuperación | `python eval/evaluar.py` | Acierto top-k ≥70%, silencio ≥90%, con denominadores explícitos |
| Respuestas del modelo real | `python eval/evaluar.py --chat --prompt system_v3` | Citas esperadas ≥80%, abstención/rechazo negativo 100%; revisión semántica humana adicional |
| Flujo de 20 casos | `python eval/evaluar_flujo.py` | 20/20 contratos correctos; sin confundir el modelo doble con evaluación real |
| Dependencias Python | `python -m pip_audit --local` | Revisar avisos y actualizar dependencias vulnerables; guardar informe |
| Dependencias frontend | `cd frontend; npm audit --audit-level=high` | Sin avisos altos o críticos |
| Secretos | `python scripts/check_secrets.py` | Sin claves reconocibles ni PEM privados en archivos versionables |

`.github/workflows/ci.yml` ejecuta pruebas, cobertura, lint, recuperación, flujo y auditorías. La ejecución manual workflow_dispatch agrega comparación híbrida y chat real con secretos del repositorio. Si falta una clave o cuota, falla y deja un informe; no se sustituye por resultados inventados. La aprobación local no equivale a una ejecución remota verde de Actions.

Los casos y sus respuestas esperadas están en `eval/preguntas.jsonl` y `eval/respuestas_esperadas.json`. Deben ampliarse cuando se incorporen nuevas fuentes o cambien artículos. Revisar manualmente la respuesta frente al pasaje, la jerarquía normativa, el nivel de estudios y la distinción entre norma nacional y reglamento interno.

Actualización del 5–6 de noviembre: 64 pruebas backend con 88,29 % de cobertura y 16 pruebas frontend. La comparación medida vuelve a dar 14/16 artículos con BM25 y 16/16 con híbrido; el chat real cita los 16 artículos esperados y controla las cuatro negativas. La prueba estricta de checklist real queda en 5/6, aunque el modelo eligió y ejecutó la herramienta en seis consultas; no se oculta la abstención de complexivo. Resultados y límites actuales en `docs/07-evaluacion.md` y en `docs/evidencias/semana-3/2026-11-05/analisis-observaciones-docente.md`. Las cifras de la matriz histórica corresponden al 1 de noviembre, no a esta revisión.

CI audita con `pip-audit --local` el entorno realmente instalado en Python 3.12, incluye la construcción y smoke HTTP del contenedor, y agrega las seis consultas reales de agente en ejecución manual. La aprobación íntegra del instructivo OCR y la repetición satisfactoria del criterio estricto de checklist siguen pendientes. No se cambia ese criterio para hacer pasar la corrida.

Riesgos concretos: fechas de vigencia y aprobación provienen del equipo; documentos sin texto requieren OCR externo; el cálculo no contempla feriados; los datos académicos son autodeclarados; las acciones solo tienen alcance demo local; la búsqueda exhaustiva de vectores está limitada a 5000 fragmentos. No se afirma certificación jurídica ni conexión con expedientes reales.

## Resultado actual y separación del historial

Backend: **104 aprobadas, cobertura 88,73 %**; frontend 18 y navegador 10 según evidencia conservada y jobs remotos aprobados. Actions 42378740379 intento 2 aprobó despliegue y 35 casos públicos. `evaluacion-real` omitido. La recuperación repetida conserva 14/16 positivos y 4/4 negativas; flujo con doble 20/20. El detector AST del historial legacy sigue fallando y las exclusiones de Gitleaks son falsos positivos distintos; ver `docs/15-auditoria-credenciales-historicas.md`.

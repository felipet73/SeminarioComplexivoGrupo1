# Plan de calidad de la Entrega 3

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

Resultados del cierre: 50 pruebas backend, 88,08% de cobertura, 15 pruebas frontend y nueve escenarios de navegador. El inventario de 52 dependencias de ejecución/pruebas y npm no reportaron avisos conocidos en las auditorías finales. La limitación de filelock del tooling del Python 3.10 heredado se declara por separado en la matriz; el entorno recomendado y CI usan Python 3.12.

Riesgos concretos: fechas de vigencia y aprobación provienen del equipo; documentos sin texto requieren OCR externo; el cálculo no contempla feriados; los datos académicos son autodeclarados; las acciones solo tienen alcance demo local; la búsqueda exhaustiva de vectores está limitada a 5000 fragmentos. No se afirma certificación jurídica ni conexión con expedientes reales.

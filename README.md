# Asistente de Titulación y Normativa Académica — UNIANDES

Caso 01, Grupo 1 · Ingeniería de Software con IA Generativa.

Integrantes: Aguilar Rogel Olmes Patricio; Cevallos Mazon Widman Yadiro; Torres Lopez Christian Felipe.

Proyecto educativo con FastAPI, React/Vite, Gemini con respaldo OpenAI, RAG con citas verificadas y agente de herramientas de alcance controlado. Orienta a partir de las fuentes aportadas; no emite resoluciones ni modifica expedientes.

## Estado real de la Entrega 3

| Punto | Implementación y evidencia |
|---|---|
| Conocimiento especializado | Cinco fuentes aprobadas (961 fragmentos) y el instructivo oficial de titulación de 2017 con OCR (86 fragmentos), pendiente de revisión/aprobación; manifiesto con hashes y fechas, vigencia por fuente en YAML e ingesta repetible |
| RAG | BM25 + embeddings, persistencia SQLite, filtros de vigencia/aprobación, umbrales, RRF, citas y abstención sin modelo cuando no hay evidencia |
| Agente controlado | Lista cerrada, Pydantic de entrada/salida, MAX_ITER, herramientas de consulta/checklist/calendario y borrador demo con confirmación, caducidad, idempotencia y auditoría |
| Evaluación | Evaluador restaurado y probado contra falsos aprobados: BM25 14/16, híbrido 16/16, chat real con cita 16/16 y negativas 4/4. Gemini eligió/ejecutó checklist en 6/6 consultas; produjo cinco listas con cita y una abstención (criterio estricto: 5/6) |
| Calidad | 75 pruebas backend, cobertura 88,43 %, 18 frontend y 10 navegador; pruebas de proxy y CSRF, Ruff, auditorías y gitleaks sin hallazgos, build/smoke de contenedor y CI. Actions remoto se verifica tras publicar |

La matriz actual de **todos los pasos mínimos, recomendados y avanzados**, incluyendo las nuevas observaciones, está en [análisis y evidencias del 5–6 de noviembre](docs/evidencias/semana-3/2026-11-05/analisis-observaciones-docente.md). La [auditoría del 1 de noviembre](docs/12-auditoria-entrega3-grupo1.md) conserva antecedentes. El equipo confirmó que ya está desplegado en Google Cloud Run; esta revisión no modifica el servicio ni afirma haber observado su configuración o una corrida remota de Actions.

## Inicio rápido

Usar Python 3.12 y Node 22 o superior. Desde la raíz:

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
pip install -r backend/requirements-dev.txt
```

En Linux/macOS activar con `source backend/.venv/bin/activate`. Copiar `.env.example` a `.env` en una instalación nueva y completar claves y contraseña administrativa. No sobrescribir un `.env` existente. Las claves solo se leen en backend.

```bash
# Corpus híbrido con Gemini; requiere clave y cuota de embeddings.
python scripts/ingest.py --strategy hybrid

# Alternativa explícita de embeddings con OPENAI_API_KEY.
python scripts/ingest.py --strategy hybrid --embedding-model text-embedding-3-small

# Línea base reproducible sin red ni proveedor.
python scripts/ingest.py --strategy lexical

cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

En otra terminal:

```bash
cd frontend
npm ci
npm run dev
```

Chat: http://localhost:5173 · Administrador: http://localhost:5173/admin · Métricas: http://localhost:5173/metricas · Contratos: http://127.0.0.1:8000/docs. `/health` comprueba el proceso, no disponibilidad de fuentes ni proveedores. El usuario administrativo por defecto es `admin`; configurar `ADMIN_PASSWORD`.

Para producción, el frontend es `https://seminario-complexivo-grupo1.vercel.app` y `frontend/.env.production` configura `VITE_API_URL=https://titulacion-rag-386902880383.us-central1.run.app`. `npm run build` incorpora esa URL; desarrollo mantiene el backend local. `frontend/vercel.json` configura el proxy `/api` a Cloud Run y las rutas SPA. Ver [variables de producción, CORS y proxy administrativo](frontend/README.md#variables-de-producción).

La ingesta reutiliza documentos idénticos y vectores en caché; no duplica revisiones sin cambios. Valida SHA-256 antes de modificar documentos. Las fechas y aprobación del YAML son decisiones del equipo, no una verificación jurídica automática. Los artículos se dividen conservando documento, revisión, sección y página; la exportación está en `data/processed/fragmentos.jsonl`.

## Verificación reproducible

Con el entorno backend activado, desde la raíz:

```bash
python -m pytest -q -c backend/pyproject.toml backend/tests --cov=app --cov-fail-under=85
# Alternativa habitual: cd backend; python -m pytest -q --cov=app --cov-fail-under=85
python -m ruff check backend scripts eval
python scripts/check_secrets.py
python scripts/ingest.py --data-dir data/eval-state --strategy lexical
python eval/evaluar.py
python eval/evaluar_flujo.py
```

La configuración `-c backend/pyproject.toml` permite ejecutar desde la raíz; también se puede ejecutar pytest desde `backend`. La suite no consume proveedores. En frontend: `npm test`, `npm run build` y `npm run test:admin` (requiere instalar Chromium con `npx playwright install chromium`). El servidor de navegador usa estado temporal y modelo doble.

Evaluación con proveedores reales, desde la raíz:

```bash
python -u eval/comparar.py --embedding-model text-embedding-3-small
python eval/evaluar.py --data-dir data/eval-hybrid --chat --prompt system_v3 --output eval/results-chat-hybrid.json
python eval/evaluar_agente_real.py --modelo gemini
```

Consume API y requiere las claves correspondientes. Gemini también puede seleccionarse para embeddings. Los informes incluyen denominadores, fuentes/artículos esperados, respuestas esperadas y obtenidas. El runner del agente usa Gemini sin fallback y conserva trazas; su criterio estricto exige seis listas finales con citas y actualmente falla con 5/6. La consulta de complexivo se abstuvo por falta de normativa institucional aprobada. No se inventan puntuaciones por el nombre del prompt. La validación de citas no certifica que cada afirmación esté respaldada: se necesita revisión humana de contenido.

El workflow ejecuta pruebas y evaluación sin red de modelos en cada push/PR. Su ejecución manual agrega la comparación y el chat reales usando los secretos `GEMINI_API_KEY` y `OPENAI_API_KEY` del repositorio. La última corrida remota debe comprobarse en Actions tras publicar los cambios.

## Alcance y límites

El asistente explica preguntas educativas relacionadas con las fuentes disponibles, distingue normas nacionales de requisitos internos y pide contexto solo cuando cambia la respuesta. Una fuente ausente produce abstención, no un requisito inventado. Solo las fuentes aprobadas, habilitadas, vigentes e indexadas pueden citarse.

El agente y su bucle están en [backend/app/agente.py](backend/app/agente.py), función `ejecutar_agente`. Allí se encuentran `PERMITIDAS`, `MAX_ITER` y `REQUIEREN_OK`, siguiendo la organización propuesta en la guía. Las herramientas se definen en [app/tools/academicas.py](backend/app/tools/academicas.py). La API ofrece `/api/agente` y `/api/agente/confirmar/{id}`; el chat utiliza ese mismo orquestador.

El calendario simula días hábiles explícitos, excluye fines de semana y la fecha inicial y **no incluye feriados ni determina plazos institucionales**. Los borradores de tutor requieren confirmación y se registran únicamente como demostración local; no se envían a la universidad, no asignan tutores ni certifican cumplimiento. El actor auditado identifica una capacidad de demostración, no una cuenta universitaria autenticada. Usar datos ficticios.

La persistencia vectorial usa SQLite y coseno exhaustivo hasta 5000 fragmentos, como alternativa arquitectónica a Chroma. No se declara un índice ANN. No hay integraciones con expedientes. La imagen incluye semilla léxica sin credenciales; activar híbrido exige claves de ejecución y reindexación. `/ready` comprueba corpus elegible y `/health` el proceso. En Cloud Run el estado local no es duradero: `RAG_DATA_DIR` selecciona ubicación, pero no aporta persistencia compartida. Ver [operación y límites](docs/06-rag.md).

Documentación técnica: [arquitectura](docs/03-arquitectura.md), [fuentes](docs/04-fuentes.md), [RAG](docs/06-rag.md), [evaluación](docs/07-evaluacion.md), [decisiones](docs/09-decisiones.md), [automatización](docs/10-automatizacion.md), [calidad](docs/11-plan-de-calidad.md). Los archivos de talleres se implementaron para esta entrega; no se presentan como descargas originales no aportadas. La revisión y ampliación de FAQ reales del equipo sigue siendo trabajo humano.

Se utilizó asistencia de Codex para análisis, implementación y ejecución de verificaciones. Los integrantes deben revisar las reglas, los casos y las fuentes y poder explicar la solución; no se atribuyen contribuciones ni commits que no consten en el historial.

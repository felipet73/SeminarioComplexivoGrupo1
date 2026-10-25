# Asistente de Titulación y Normativa Académica — UNIANDES

**Caso 01, Grupo 1 · Ingeniería de Software con IA Generativa**  
Proyecto académico con backend FastAPI, frontend React y administración de prompts, fuentes RAG y evaluación.

Integrantes:  
- Aguilar Rogel Olmes Patricio
- Cevallos Mazon Widman Yadiro  
- Torres Lopez Christian Felipe  


## Estado de avance

> **Implementado:** chat React/FastAPI, Gemini con respaldo OpenAI, contexto académico, métricas y `/admin` protegido con versiones de prompt, fuentes versionadas, indexación RAG y laboratorio comparativo.
>
> **Pendiente:** cargar y validar normativa real, evaluar exactitud con artículos esperados, herramientas deterministas del agente, FAQ reales y despliegue. Solo fuentes aprobadas, vigentes e indexadas pueden fundamentar citas.

## Inicio rápido (Python 3.11+)

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir http://127.0.0.1:8000/health (esperado: `{"status":"ok","service":"titulacion-rag-api","version":"2.0.0"}`) y http://127.0.0.1:8000/docs. El endpoint de salud solo confirma que la API está en ejecución; no comprueba conectividad con LLM, fuentes ni índice vectorial.

Pruebas: `cd backend && pytest -q`.

## Semana 2: ejecución

Administración: `http://localhost:5173/admin`, usuario por defecto `admin`; contraseña solo en `.env` (`ADMIN_PASSWORD`). `.env.example` la deja vacía. Pestañas Configuración, RAG y Análisis, con pruebas aisladas `cd frontend; npm run test:admin`. Instrucciones, límites y estado actual en [administración y RAG](docs/08-admin-rag-y-analisis.md).

Actualización del 24-10-2026: formulario de contexto académico y dashboard público en `http://localhost:5173/metricas` (API: `GET /api/metricas`). Incluye intentos, errores, tokens reportados y latencias. Las métricas requieren el backend activo y registran solo metadatos de las nuevas consultas. Revisión de requisitos y pendientes en [contexto, métricas y brechas](docs/07-contexto-metricas-y-brechas.md).

El backend expone `POST /api/chat` y `POST /api/chat/stream` (SSE). Gemini es el proveedor principal y OpenAI el respaldo; sus claves viven solo en `.env`.

```powershell
# terminal 1
cd backend
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# terminal 2
cd frontend
npm install
npm run dev
```

Pruebas: en backend `.\.venv\Scripts\python.exe -m pytest -q`; en frontend `npm run build`, `npm run test` y `npm run test:admin` tras `npx playwright install chromium`. Las pruebas unitarias y `test:admin` usan dobles sin consumir proveedores. La suite histórica `npm run test:e2e` requiere servidores propios y puede consultar el modelo real. Sin normativa aprobada e indexada, el sistema no entrega citas ni requisitos como oficiales.

## Estructura

```text
.
├── README.md
├── .gitignore
├── .env.example
├── docs/
│   ├── 01-propuesta.md
│   ├── 02-requisitos.md
│   ├── 03-arquitectura.md
│   ├── 04-fuentes.md
│   ├── 05-levantamiento-15-preguntas.md
│   ├── 05-preguntas-frecuentes.csv
│   └── evidencias/semana-1/
├── data/
│   ├── raw/                     # PDF normativos + manifiesto
│   └── referencias/             # documentos docentes aportados
├── backend/
│   ├── app/main.py
│   ├── tests/test_health.py
│   ├── requirements.txt
│   └── pyproject.toml
└── scripts/descargar_fuentes.py
```

## Variables de entorno

El chat principal admite aclaraciones con un popup de campos faltantes y reconsulta con contexto. Ver [contrato e interacción](docs/09-aclaraciones-y-campos-necesarios.md).

Copiar `.env.example` a `.env` en instalaciones nuevas y completar las claves de los proveedores y `ADMIN_PASSWORD`. **Nunca subir `.env` o claves reales a Git.** `AI_PROVIDER` y `AI_MODEL` son configurables y no se usan en `/health`.

## Alcance técnico por fase

| Semana | Entregable principal | Estado en este repositorio |
|---|---|---|
| 1 | Propuesta, requisitos, arquitectura, inventario de fuentes y backend base | Documentado; API `/health` y su prueba implementadas |
| 2 | Chat, prompts comparados y cliente web | Implementados; laboratorio `/admin` disponible; validar comparativas con casos reales |
| 3 | RAG con citas, agente controlado y evaluación | RAG e historial implementados; pendientes herramientas deterministas y evaluación de exactitud |
| 4 | Despliegue, pruebas en URL pública y documentación final | Pendiente |

## Fases pendientes

1. Semana 1: validar vigencia de fuentes, obtener evidencia real de ≥15 FAQ y registrar la revisión docente.
2. Semana 2: ejecutar y revisar 3 prompts × 10 preguntas con el laboratorio implementado; los ejemplos propuestos no sustituyen FAQ reales.
3. Semana 3: cargar normativa vigente, aprobar e indexar; implementar tools y evaluar con 20 preguntas/artículos esperados. Ver [administración y RAG](docs/08-admin-rag-y-analisis.md).
4. Semana 4: despliegue, pruebas de negativas/ambigüedad/inyección, README final y sustentación.

## Métricas de aceptación (todavía no medidas)

≥80% (≥16 de 20) exactitud con artículo, 100% abstención en negativos y 100% rechazo en casos adversarios ensayados. Todos los resultados futuros deben reportar denominadores y evidencia.

## Seguridad, ética y límites

Sistema orientativo; no emite actos administrativos ni certifica estados de estudiante. En el MVP solo datos ficticios. Las fuentes no validadas no pueden dar respuestas oficiales. Registrar aportes y herramientas de IA usadas en el README final.

## Fuentes y autores

Caso y documento FAQ aportados por el equipo (copias en `data/referencias/`). Enlaces oficiales y estado de verificación en `docs/04-fuentes.md`. **Integrantes / contribuciones:** por completar; no atribuir commits inexistentes.

# Asistente de Titulación y Normativa Académica — UNIANDES

**Caso 01, Grupo 1 · Ingeniería de Software con IA Generativa**  
Proyecto de Semana 1: definición de la solución, inventario inicial de normativa, FAQ propuestas y backend mínimo en Python + FastAPI.

Integrantes:  
- Aguilar Rogel Olmes Patricio
- Cevallos Mazon Widman Yadiro  
- Torres Lopez Christian Felipe  


## Estado de avance

> **Implementado:** API FastAPI con `GET /health`, documentación OpenAPI y prueba automatizada.
>
> **Pendiente:** frontend, chat, RAG, base vectorial, herramientas del agente, levantamiento real de FAQ y validación oficial de vigencia. Las fuentes pendientes no se usan para emitir respuestas oficiales.

## Inicio rápido (Python 3.11+)

```bash
cd backend
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir http://127.0.0.1:8000/health (esperado: `{"status":"ok","service":"titulacion-rag-api","version":"0.1.0"}`) y http://127.0.0.1:8000/docs. El endpoint de salud solo confirma que la API está en ejecución; no comprueba conectividad con LLM, fuentes ni índice vectorial.

Pruebas: `cd backend && pytest -q`.

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

Copiar `.env.example` a `.env` si se configura un LLM en futuras fases. **Nunca subir `.env` o claves reales a Git.** `AI_PROVIDER` y `AI_MODEL` son configurables y no se usan en `/health`.

## Alcance técnico por fase

| Semana | Entregable principal | Estado en este repositorio |
|---|---|---|
| 1 | Propuesta, requisitos, arquitectura, inventario de fuentes y backend base | Documentado; API `/health` y su prueba implementadas |
| 2 | Chat, prompts comparados y cliente web | Pendiente |
| 3 | RAG con citas, agente controlado y evaluación | Pendiente |
| 4 | Despliegue, pruebas en URL pública y documentación final | Pendiente |

## Fases pendientes

1. Semana 1: validar vigencia de fuentes, obtener evidencia real de ≥15 FAQ y registrar la revisión docente.
2. Semana 2: chat backend/frontend; probar 3 prompts × 10 preguntas; secretos solo backend.
3. Semana 3: fragmentación por artículo, RAG con citas, tools y evaluación con 20 preguntas/ artículos esperados.
4. Semana 4: despliegue, pruebas de negativas/ambigüedad/inyección, README final y sustentación.

## Métricas de aceptación (todavía no medidas)

≥80% (≥16 de 20) exactitud con artículo, 100% abstención en negativos y 100% rechazo en casos adversarios ensayados. Todos los resultados futuros deben reportar denominadores y evidencia.

## Seguridad, ética y límites

Sistema orientativo; no emite actos administrativos ni certifica estados de estudiante. En el MVP solo datos ficticios. Las fuentes no validadas no pueden dar respuestas oficiales. Registrar aportes y herramientas de IA usadas en el README final.

## Fuentes y autores

Caso y documento FAQ aportados por el equipo (copias en `data/referencias/`). Enlaces oficiales y estado de verificación en `docs/04-fuentes.md`. **Integrantes / contribuciones:** por completar; no atribuir commits inexistentes.

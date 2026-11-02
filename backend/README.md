# Backend

Administración protegida en `/api/admin/*`: sesión HttpOnly, prompts .md con revisiones, originales y metadatos de fuentes en `data/admin`, índices FTS5/vectores y simulaciones con evaluación IA. Define `ADMIN_PASSWORD` en `.env` y reinstala dependencias (`python-multipart`, `pypdf`, `defusedxml`). Para acceder desde navegador usa `/admin` en el frontend (proxy de mismo origen). Ver [operación y seguridad](../docs/08-admin-rag-y-analisis.md).

El chat recupera evidencia de fuentes aprobadas/vigentes, valida JSON y IDs de citas y se abstiene ante salida inválida. SQLite debe residir en volumen persistente; ejecutar un solo worker mientras sesiones/cola sean locales. Las pruebas usan datos, archivos y prompts temporales.

Indexación y recuperación administrativas devuelven `trace` con pasos, estados y conteos observados. Análisis persiste la traza y ejecuta solo respuestas, sin juez de IA (`evaluation_mode=measurements_only`). Los históricos se conservan. Ver [contrato y almacenamiento vectorial](../docs/10-ayudas-y-trazas-rag.md).

Las respuestas de chat y el evento SSE `done` incluyen `campos_necesarios`: controles canónicos de contexto para aclaraciones. El modelo solo propone IDs permitidos y no puede solicitar campos arbitrarios; se omiten duplicados y datos ya aportados. Ver [contrato de aclaraciones](../docs/09-aclaraciones-y-campos-necesarios.md). `services/chat_flow.py` comparte ese flujo con las simulaciones; cada caso admite `contexto`, y cada resultado incluye respuesta validada más salida original para auditoría. Las comparaciones no hacen fallback.

Modelo principal actual: `gemini-3.5-flash-lite`; respaldo: `gpt-4.1-mini`. Tiempo de espera por llamada: 15 segundos y `LLM_RETRIES=0` (un intento por proveedor). Los reintentos internos del SDK también están desactivados. Si el principal falla, se intenta el respaldo directamente. Reiniciar la API para recargar `.env`.

`GET /api/metricas` expone resúmenes y eventos técnicos públicos sin autenticación. `logs/metrics.jsonl` guarda consultas e intentos de proveedores sin datos personales ni texto de entrada/salida. Rota a 5 MB con tres respaldos; el resumen cubre hasta 2000 eventos. Los tokens desconocidos se mantienen como `null`. Los tests usan un archivo temporal para no contaminar el dashboard.

Los endpoints chat aceptan carrera, curso, modalidad de estudios, período, jornada, tema, objetivo y `modelo_preferido`. El contexto acompaña a la consulta como datos autodeclarados; no es evidencia normativa. Reinicie Uvicorn tras modificar `.env`.

API FastAPI del asistente. La clave vive únicamente en el archivo `.env` de la raíz del repositorio, nunca en el navegador ni en Git.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```

Contratos: `GET /health`, `POST /api/chat` y `POST /api/chat/stream` (SSE). Gemini es principal y OpenAI se intenta ante errores transitorios. Sin fuentes aprobadas no hay citas y se exige revisión humana. Las pruebas usan un doble LLM, sin claves ni consumo.

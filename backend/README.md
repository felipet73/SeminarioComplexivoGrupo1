# Backend

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

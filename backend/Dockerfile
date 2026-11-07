FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home app && mkdir -p /app/data /app/logs \
    && chown app:app /app/data /app/logs

COPY --chown=app:app backend/ .
COPY --chown=app:app config/ /app/config/
COPY --chown=app:app scripts/ingest.py /app/scripts/ingest.py
COPY --chown=app:app data/raw/ /app/data/raw/

USER app

# Semilla reproducible sin claves ni llamadas a proveedores durante el build.
# La activación híbrida se realiza después, con secretos de ejecución y reindexación.
RUN python /app/scripts/ingest.py --data-dir /app/data/admin --strategy lexical

ARG APP_REVISION=unknown
ENV APP_REVISION=${APP_REVISION}

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

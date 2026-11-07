# RAG: fuentes, recuperación y límites

> **Estado de entrega al 7 de noviembre de 2026:** Consultar el [checklist vigente s4a–s4k](14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

Revisión del 5–6 de noviembre de 2026, Grupo 1. Implementación: `backend/app/services/rag.py`; parámetros: `config/parametros.yaml`; criterios de elegibilidad: `config/fuentes.yaml`.

## Ingesta y procedencia

`python scripts/ingest.py` reutiliza el indexador del panel. Antes de modificar documentos valida el manifiesto completo: ruta dentro del corpus, SHA-256 y política de cada fuente. Conserva el PDF original, revisión, título, artículo/sección y página. Una fuente sin cambios reutiliza su índice compatible y la caché de embeddings.

Hay seis originales: cinco fuentes aprobadas con 961 fragmentos y el instructivo oficial de titulación de UNIANDES de 2017, con 86 fragmentos OCR pendientes de aprobación. Este último **no participa en las respuestas ni en las métricas de acierto**. El PDF oficial es escaneado; se conserva una transcripción por página en `.ocr.json`, asociada al hash del original y con hash propio en el manifiesto. La ingesta verifica ambos hashes y el número y orden de las páginas. No confunde descarga oficial con revisión jurídica o aprobación del OCR.

Para repetir el OCR se usa `scripts/ocr_normativa.sh` con Poppler y Tesseract en español a 200 dpi. La transcripción ya está incluida: un clon nuevo no necesita estas herramientas para ingerirla. Hay errores en membretes y tablas; revisar íntegramente el original y la transcripción, corregirla, actualizar hashes y confirmar aplicabilidad antes de cambiar `approved` en el YAML. Una revisión parcial de páginas no equivale a aprobación integral.

La fecha de descarga se registra solo cuando existe. Las fuentes aportadas desde el panel conservan su fecha de incorporación y `downloaded_at=null`.

## Recuperación

1. Se filtran documentos habilitados, aprobados, dentro de las fechas declaradas y con revisión/firma de índice actuales.
2. SQLite FTS5 produce un ranking BM25. Se exige cobertura léxica mínima, configurable independientemente del coseno.
3. En modo híbrido se genera el embedding de la consulta y se calcula coseno sobre vectores compatibles del mismo modelo. El umbral depende del modelo y está en configuración.
4. Los rankings léxico y semántico se fusionan mediante RRF; se devuelven los mejores `top_k`. Un fallo semántico permite el respaldo léxico y se refleja en la traza.
5. Sin evidencia elegible el flujo se abstiene antes de llamar al modelo. Las consultas de checklist concentran la búsqueda en el trámite y perfil académico, evitando tratar toda la descripción del estudiante como palabras obligatorias.

Los valores iniciales son `top_k=4`, ventanas de 1400 caracteres, solapamiento de 160 y cobertura léxica 0,60. Los cosenos iniciales son 0,65 para Gemini y 0,55 para OpenAI. Son parámetros de esta muestra, **no probabilidades ni umbrales universales**. El panel permite modificarlos y obtiene las referencias por modelo desde el backend. Un estado existente conserva sus ajustes; cambiar los valores por defecto no reescribe decisiones previas del administrador.

SQLite conserva textos y vectores; el coseno es exhaustivo, limitado a 5000 fragmentos. Es la alternativa documentada a Chroma; no hay índice ANN. No se agrega otra base vectorial solo para reproducir el nombre de una biblioteca de la guía.

## Respuestas y agente

El prompt activo distingue normativa nacional, reglas internas, nivel y modalidad, permite preguntas educativas relacionadas con las fuentes y pide solo aclaraciones necesarias. La lista cerrada y el tope están en `app/agente.py`; el modelo solicita herramientas como JSON validado con Pydantic. No se presenta este protocolo como integración nativa de function calling del SDK.

Después de generar, el servidor verifica los IDs citados y la vigencia de los pasajes. Una cita inexistente, desactualizada o ausente en una respuesta normativa convierte la salida en abstención. Esto valida procedencia, **no la implicación semántica de cada frase**.

`generar_checklist` utiliza nivel y modalidad declarados, descarta reglas explícitamente incompatibles y requisitos de cargos. Mantiene citas textuales y referencias por ítem, informa dimensiones ambiguas y nunca marca requisitos cumplidos. El agente rechaza un nivel/modalidad inventado por el modelo. La UI muestra la lista generada por el servidor; las casillas indican lectura personal, sin certificar cumplimiento. Sigue siendo una lista extractiva limitada por la evidencia recuperada y requiere revisión humana de aplicabilidad y exhaustividad.

## Reproducción y operación

```bash
python scripts/ingest.py --data-dir data/eval-state --strategy lexical
python eval/evaluar.py
python -u eval/comparar.py --embedding-model text-embedding-3-small
python eval/evaluar_agente_real.py --data-dir data/eval-hybrid --modelo gemini
```

Las dos últimas órdenes consumen proveedores. Los resultados se explican en `docs/07-evaluacion.md`. La imagen del backend incluye una semilla **léxica**, generada sin credenciales durante el build, para que un contenedor nuevo tenga corpus. El valor por defecto para estados nuevos de la aplicación continúa siendo híbrido; activar híbrido en la imagen exige configurar un proveedor y reindexar. `/health` prueba el proceso; `/ready` exige fragmentos elegibles con índice actual, sin comprobar conectividad al proveedor.

Cloud Run ya está desplegado según el equipo. Su contrato exige escuchar en `0.0.0.0:$PORT` y advierte que las escrituras locales se pierden al detener la instancia: [contrato oficial](https://docs.cloud.google.com/run/docs/container-contract). La imagen respeta puerto y usuario no root. `RAG_DATA_DIR` permite seleccionar el directorio del estado; por sí solo no aporta almacenamiento duradero. No se debe presentar SQLite local, las sesiones en memoria ni la auditoría demo como estado compartido entre instancias. La semilla restaura el corpus inicial, no las cargas y decisiones administrativas posteriores. La configuración real del servicio y su persistencia deben revisarse con acceso al despliegue; no se redeployó durante esta revisión.

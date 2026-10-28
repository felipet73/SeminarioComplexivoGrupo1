# Ayudas y trazas interactivas del administrador

Actualización: 28 de octubre de 2026. No requiere dependencias nuevas. Reiniciar backend y recargar frontend para disponer del contrato ampliado.

## Ayudas de configuración

Los botones «?» se abren al pasar el cursor, al enfocarlos con teclado o al pulsarlos en móvil. Presentan finalidad, configuración y resultado esperado. Escape o salir del foco cierra la ayuda. El panel adapta su ancho al dispositivo y puede desplazarse si excede la altura disponible.

Configuración explica edición/activación de prompts, procedencia, aprobación, inclusión, vigencia y reemplazo de fuentes. Análisis explica versiones, proveedor y referencias de casos, más la lectura de las mediciones. RAG incorpora ayudas junto a estrategia, top-k, tamaño, solapamiento, umbral y documento; cada sección termina con un recuadro de orientación.

| Ajuste | Uso | Aplicación |
|---|---|---|
| Léxica / híbrida | BM25 o BM25 más embeddings Gemini | Guardar y reindexar al cambiar estrategia |
| Top-k 1–10 | Máximo de fragmentos que se devuelven | Guardar, sin reindexar |
| Tamaño 300–4000 caracteres | Máximo aproximado por ventana; no son tokens | Guardar y reindexar |
| Solapamiento 0–1000 y menor a media ventana | Continuidad entre ventanas del mismo bloque | Guardar y reindexar |
| Umbral 0–1 | Coseno mínimo para candidatos semánticos; no afecta BM25 | Guardar, sin reindexar |

Los valores iniciales de referencia son 1400 caracteres, solapamiento 160, top-k 4 y umbral 0.65. No representan una optimización evaluada sobre la normativa real. Cambios pendientes del formulario no afectan a la indexación o búsqueda del backend.

## Índice y almacenamiento vectorial reales

`chunks` almacena ID, documento, revisión, título, sección, página, texto, vector y modelo de embeddings. `chunks.vector` contiene un array JSON en modo híbrido; en léxico es nulo. `chunk_search` es una tabla virtual FTS5 con índice léxico. No existe una tabla vectorial especializada ni un índice ANN en esta versión.

Al indexar: se usa el texto extraído al cargar, se reconocen artículos, se fragmenta con continuidad local y se generan embeddings solo en híbrido. Los nuevos registros sustituyen los de la fuente en una transacción; fallos anteriores al reemplazo conservan el índice previo. Indexar no aprueba ni modifica la vigencia de una fuente.

Al buscar:

1. Se captura la configuración guardada.
2. Se filtran fuentes habilitadas, aprobadas, vigentes y con revisión/firma de índice compatibles.
3. BM25 busca hasta 24 términos unidos por OR y retiene hasta 40 candidatos.
4. En híbrido se leen hasta 5000 vectores compatibles y se genera el embedding de consulta solicitando 768 dimensiones. Python compara coseno, aplica el umbral y conserva el ranking semántico. En léxico se omite; ante fallo semántico se informa respaldo BM25.
5. Se fusionan posiciones con RRF, `1/(60+posición)`, y se toma top-k. El score no es confianza, probabilidad ni exactitud.
6. Se devuelven fragmentos con procedencia y duración observada. La prueba de recuperación no usa un modelo generativo; la búsqueda híbrida sí puede gastar API de embeddings.

## Diagramas y contrato

`POST /api/admin/rag/index/{id}` y `POST /api/admin/rag/search` devuelven `trace`: lista de pasos con `id`, `title`, `description`, `status` y `details`. La recuperación incluye ruta sin fuentes, léxica, híbrida y fallo semántico. Solo contiene conteos/metadatos explicativos, no el contenido de los vectores ni credenciales.

El gráfico y la lista usan botones accesibles. Seleccionar un nodo marca el paso correspondiente; seleccionar un paso marca el nodo y cambia el panel de detalles. Estados: realizado, omitido, error/respaldo, pendiente y en curso. El gráfico tiene desplazamiento horizontal en móvil. No es un diagrama de razonamiento privado de la IA: explica operaciones de la aplicación observadas en backend.

## Simulación: mediciones, sin juez de IA

Ya no se solicita evaluación de respuestas ni ganador a un modelo. Solo las variantes usan llamadas generativas cuando no son rechazadas localmente. RAG puede consumir embeddings por separado. `review` se mantiene nulo en trabajos nuevos por compatibilidad y `evaluation_mode` es `measurements_only`.

El trabajo guarda trazas de captura, recuperación, ejecución de variantes, validación del contrato, recopilación de mediciones y persistencia. Muestra latencia y tokens por variante, errores y duración total. La duración total incluye recuperación/guardado y no equivale a la media de latencias. Tokens desconocidos son N/D; no se inventan consumos ni exactitud. Los casos y referencias esperadas requieren revisión humana. Los trabajos antiguos sin traza se identifican como históricos, sin reconstruir pasos ficticios ni borrar sus datos.

## Verificación

- Backend: `.\.venv\Scripts\python.exe -m pytest -q`, desde `backend`.
- Frontend: `npm run build`, `npm run test` y `npm run test:admin`.
- Las pruebas comprueban que no hay llamada al juez, las trazas léxica/híbrida/respaldo, sincronización de nodos/pasos, tooltips y ancho móvil. La suite usa modelos/embeddings dobles y fuentes temporales, sin consumo de proveedores reales.

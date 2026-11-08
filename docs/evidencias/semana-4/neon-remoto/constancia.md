# Persistencia remota entre revisiones Cloud Run con PostgreSQL Neon

## Evidencia y resultado

El operador ejecutó las capturas y adjuntó los tres JSON completos. Se conserva el contenido JSON completo; solo se normalizan saltos de línea CRLF a LF. `verificacion.json` registra los SHA-256 de los adjuntos originales y de los archivos versionados y la comparación recalculada por el asistente con `scripts/verificar_persistencia_remota.py`. No se usaron credenciales de producción desde el entorno del asistente.

| Punto | Antes | Después |
| --- | --- | --- |
| Revisión Cloud Run declarada | titulacion-rag-00033-wvv | titulacion-rag-00034-bgp |
| Fecha UTC del reporte | 2026-11-08 14:36:51 | 2026-11-08 14:48:28 |
| SHA de código | d9f90b3c960a4a0da438e456e01e98a636ff8805 | d9f90b3c960a4a0da438e456e01e98a636ff8805 |
| Documentos | 6 | 6 |
| Fragmentos capturados | 1.047 | 1.047 |
| Revisión del instructivo | 2 | 2 |

La comparación da `resultado=aprobado`, documentos/prompts/configuración `true`, exit 0 según salida del operador. Para cada documento se conservan ID, revisión y hashes de metadatos, archivo descargado, historial y fragmentos. El script verifica el SHA del archivo descargado contra el registrado al capturar; no se versionan sus bytes ni textos de prompts/documentos. Los reportes no contienen campos de contraseña, cookie o DSN. El operador corrigió previamente el campo de revisión de la primera captura, donde había ingresado por error la contraseña; solo se incorpora el archivo corregido, sin reconstruir los demás datos.

## Capturas revisadas en la conversación

- Cloud Run muestra `titulacion-rag-00034-bgp` con 100 % del tráfico y `titulacion-rag-00033-wvv` con 0 %. Actualización, creación y enrutamiento aparecen completados. Las etiquetas del script las declara el operador; esta captura complementa la comparación.
- El chatbot responde con `gemini-3.5-flash-lite` y presenta enlaces al instructivo revisión 2, artículo 23/página 9 y artículo 42/página 17. Esto acredita funcionamiento con fuentes tras el cambio de revisión.
- **Observación de calidad:** el texto menciona el artículo 24 mientras uno de los enlaces corresponde al 23. Esta captura no certifica respaldo semántico correcto de cada afirmación. Revisar la fuente y la respuesta antes de cerrar esa observación; no cambiar el corpus ni aprobar OCR para hacerla pasar.

Las imágenes se observaron en la conversación; no se dispone de sus archivos originales en el checkout y no se presentan como imágenes versionadas. El equipo puede conservarlas junto con su material original de sustentación. Los JSON versionados son la evidencia reproducible de igualdad.

## Alcance y límites

Se acredita conservación del estado administrativo capturado entre dos revisiones Cloud Run, usando PostgreSQL Neon activado por el operador. Se observa una respuesta con fuentes después del cambio. No es una prueba de reinicio del servidor Neon, recuperación de desastre, durabilidad de métricas/sesiones, ni validación semántica completa. El endpoint limita a 512 fragmentos por documento; en este corte se capturaron 1.047 en total. No compara todos los vectores. La prueba local de PostgreSQL cubre vectores/caché y reinicio del servidor por separado.

No se ejecutó un nuevo smoke público 35/35 como parte de estos reportes. Los resultados anteriores mantienen su SHA y fecha; no se atribuyen automáticamente a esta revisión.

## Seguimiento de la discrepancia artículo 24/23

Se reprodujo el encabezado OCR `Art, 24` dentro del fragmento etiquetado artículo 23 y se preparó corrección del separador con regresiones. No cambia el resultado histórico de esta comparación. La aplicación al índice remoto y nueva consulta siguen pendientes. [Diagnóstico y reindexación](../../../28-citas-articulo-24.md).

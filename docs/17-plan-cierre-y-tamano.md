# Optimización de tamaño y plan de cierre verificable

Corte del 7 de noviembre de 2026. Base revisada: `6151271` (incluye merge del PR #20 y conversión de capturas de semana 2 a PDF). La base de producción con 35 casos públicos aprobados sigue siendo la registrada en la evidencia; este análisis no declara desplegada otra revisión.

## Tamaño actual: las imágenes no bastan

El ZIP de archivos versionados con DEFLATE nivel 9 mide **26.512.973 bytes (25,28 MiB)** antes de las mejoras de esta rama, frente a 28.818.950 bytes (27,48 MiB) de la revisión anterior. La reducción realizada por el equipo es real, aproximadamente 2,31 MB. Con WebP sin pérdida y las nuevas herramientas, la siguiente medición local es aproximadamente **24,82 MiB**; sigue fuera del límite.

| Grupo | Bytes comprimidos en esa medición | Observación |
| --- | --- | --- |
| `data/raw/` | 21.201.054 (20,22 MiB) | Por sí solo ya supera el máximo decimal de 20.000.000 bytes. |
| Imagen principal del frontend | 2.191.160 dentro del ZIP | Original PNG de 2.249.430 bytes. |
| Documentación | 2.646.677 (2,52 MiB) | Incluye evidencias y PDF; no representa el mayor bloqueo. |

Los mayores archivos son el instructivo de seguimiento a graduados (7,55 MiB comprimidos) y el instructivo de titulación con OCR (7,46 MiB). El resto de PDF oficiales completa la mayor parte del corpus. Aunque se eliminaran todas las imágenes de documentación, el corpus y el resto del código seguirían excediendo el límite. No se plantea quitar fuentes de la ingesta sin ajustar y verificar todo el proyecto.

## Optimización aplicada sin cambiar apariencia

La imagen principal del frontend se convierte de PNG a **WebP sin pérdida**: de 2.249.430 a 1.695.730 bytes (553.700 bytes menos, 24,6 %). Se compararon todos los píxeles RGBA decodificados: son idénticos. Se actualiza el import y pasan los tests y la compilación de Vite. No cambia el contenido visual ni la lógica del chat.

La recompresión estructural sin pérdida de los PDF se ensayó en `tmp/`, sin modificar originales. Los ahorros individuales son pequeños y no resuelven los más de seis millones de bytes necesarios. `Reglamento-de-Regimen-Academico.pdf` indica firmas digitales y se excluyó de la reescritura. Ningún archivo de `data/raw/`, hash de manifiesto u OCR fue modificado por esta optimización.

## Código preparado para los pendientes

1. **`scripts/empaquetar_entrega.py`:** crea un ZIP reproducible desde archivos conocidos por Git, excluye `.git`, secretos locales, dependencias, caches y estado de ejecución. Informa tamaños por archivo y rechaza el resultado si supera **20.000.000 bytes**: no deja un ZIP sobredimensionado como entregable. `--medir` permite diagnosticar sin crear el paquete. Las pruebas comprueban exclusión incluso de un `.env` versionado, reproducibilidad y rechazo de exceso de tamaño. No sustituye el análisis de secretos en archivos JSON arbitrarios o en el historial.
2. **`.github/workflows/evaluacion-final.yml`:** evaluación manual **sin despliegue**. Prepara corpus aislado, compara lexical/hybrid, ejecuta golden set generativo y seis checklists con el criterio estricto. Guarda resultados aunque falle una comprobación. Necesita `GEMINI_API_KEY` y `OPENAI_API_KEY` en Secrets de GitHub Actions; las claves de Secret Manager de Cloud Run no se inyectan automáticamente en el runner. No se copian claves al código ni a la documentación.
3. **WebP sin pérdida:** reduce el frontend con igualdad de píxeles y sin tocar corpus. Backend: 105 pruebas aprobadas, cobertura de aplicación 88,73 %. Frontend: 18 pruebas y build aprobados. Los 104 tests anteriores y el 35/35 remoto conservan su fecha/revisión originales; la nueva prueba verifica el empaquetador.

La evaluación manual nueva todavía no se ejecutó contra proveedores. El resultado del agente continúa siendo el último acreditado (5/6), hasta que otra ejecución demuestre lo contrario. El workflow no reduce umbrales ni aprueba el instructivo automáticamente.

## Qué necesita código y qué necesita otra actuación

| Pendiente | ¿Código? | Trabajo concreto y evidencia para cerrarlo |
| --- | --- | --- |
| ZIP menor de 20 MB | Empaquetador ya preparado; optimización del corpus requiere tratamiento adicional | Elegir entre optimizar PDF escaneados con revisión de calidad/hashes, o acordar corpus externo descargable y verificado con el docente. No basta comprimir capturas. Medir paquete final y probar instalación. |
| s4b historial sin credenciales | El mecanismo actual ya está corregido; no requiere otro parche de login | Acreditar no reutilización/rotación, revisar URLs antiguas y coordinar limpieza de ramas/tags/PR y clones. No se hace force push como parte de una optimización. |
| s4c corpus base tras reinicio | La semilla ya forma parte de la imagen | Capturar respuesta citada antes/después de una nueva instancia/revisión y comparar fuente, SHA y readiness. Declarar que el corpus es fijo si ese es el alcance de la demo. El ensayo aún falta. |
| s4c cambios administrativos duraderos | Sí, más infraestructura, si se deben conservar | Cloud Run no conserva SQLite local entre instancias. Una solución robusta es PostgreSQL gestionado para registros/índice y almacenamiento de objetos para originales, o cambiar a un alojamiento con disco duradero adecuado para SQLite y un solo proceso. Cambiar solo RAG_DATA_DIR o max-instances no lo resuelve; SQLite sobre FUSE no se acepta como arreglo ficticio. |
| s4e comparación final | Runner manual separado ya preparado | Configurar claves de Actions y ejecutar golden set comparable. Adjuntar métricas con denominadores, diferencias frente a semana 3 y fallos. No se atribuye 6/6 a tres consultas públicas distintas. |
| OCR y 6/6 del agente | Revisión humana primero; código solo si se confirma un defecto | Revisar páginas, vigencia y aplicabilidad; aprobar la fuente solo con esa evidencia, reindexar y ejecutar seis casos bajo los mismos criterios. Si una regla sigue ausente, conservar la abstención y explicar el límite. |
| s4d p95 y capturas | No necesariamente | Adjuntar JSON del intento exitoso, health, pipeline verde y salida de pruebas. No usar la latencia de una corrida fallida. |
| s4h instalación en diez minutos | Documentación ya preparada | Otro integrante instala con README, cronometra, registra ambiente y health. Ajustar el código solo si el ensayo detecta un bloqueo real. |
| s4i, s4j, s4k | No se pueden completar inventando contenido | Declaraciones individuales, ensayo de 12 min, vídeo de 2 min y observaciones reales del tribunal con responsable, acción y commit. |

## Cómo resolver el corpus y los hashes sin romper la ingesta

**Opción A, mantener todo dentro del ZIP:** optimizar los dos PDF grandes sin firma mediante reducción controlada de resolución/compresión de imágenes, manteniendo número de páginas, legibilidad y texto. Esto ya no es necesariamente sin pérdida; necesita revisión visual de todas las páginas y conservar constancia de transformación y hash original. Actualizar SHA del manifiesto y, para el PDF con OCR, su asociación `original_sha256` y el hash del JSON OCR; verificar la correspondencia página a página. Repetir ingesta, tests, recuperación y generación citada. Un original firmado debe mantenerse intacto para no invalidar su firma. No se aplicó ninguna transformación al corpus en esta rama.

**Opción B, preservar originales descargables:** mantener URL autorizada y hash exacto, descargar de forma reproducible antes de la ingesta y conservar verificación TLS/checksum. Requiere cambios de instalación/build y acuerdo del docente porque la guía pide el mismo contenido en ZIP y GitHub. No se cambia a esta modalidad sin aclarar ese criterio.

La decisión debe tomarse antes de invertir en otra ronda de compresión de capturas: el corpus por sí solo supera el límite.

## Comandos de uso y límites

Desde raíz:

```bash
python scripts/check_secrets.py
python scripts/empaquetar_entrega.py --medir --report tmp/paquete-informe.json
# Cuando el proyecto ya cumpla el límite y el informe sea correcto:
python scripts/empaquetar_entrega.py --output tmp/Titulacion_Semana4.zip
```

El modo medir devuelve exit 1 cuando detecta exceso de tamaño; es el resultado esperado del control, no un error de instalación. Solo incluye archivos conocidos por Git; revisar `git status` y añadir al índice los nuevos archivos legítimos antes de medir. No usar `git add .` sin comprobar qué se añade. El reporte señala cambios locales; no confundirlo con un release publicado.

Para s4e, después de revisar/mergear el workflow: Actions → **Evaluación final sin despliegue** → Run workflow. Consume API y requiere los Secrets indicados. No ejecuta Cloud Run ni cambia IAM. La limpieza de historial, la aprobación de normativa y la migración de persistencia son tareas independientes y requieren su propia verificación.

## Corrección adicional: dashboard de métricas en cero

Se reprodujo en la imagen anterior: el proceso UID 1000 intentaba escribir `/app/logs/metrics.jsonl`, pero el Dockerfile solo daba permisos sobre `/app/data`. El fallo se capturaba para no romper el chat y el dashboard quedaba en cero. Se crea `/app/logs` con propietario `app:app`, se desactiva caché de la respuesta y el cliente, y el smoke exige que una consulta aumente el contador. En la imagen corregida el contador pasó de 1 a 2; no se consumió proveedor para esa verificación. Ver [evidencia](evidencias/semana-4/metricas-permisos-2026-11-07.json). Hace falta desplegar esta imagen para corregir producción; no basta recargar la página ni cambiar claves. El histórico continúa siendo local a la instancia, no duradero entre reinicios.

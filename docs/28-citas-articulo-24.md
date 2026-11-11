# Artículo 24: diagnóstico de la etiqueta de cita y corrección

## Problema reproducido

La captura de la consulta posterior al ensayo Neon describe las dos fases del modelo de negocios y menciona artículo 24, mientras presenta una fuente artículo 23/página 9. Se revisó visualmente la página 9 del PDF versionado: artículo 23 trata defensa/evaluación del estudio de caso; artículo 24 trata modelo de negocios, con presentación del perfil para aprobación y del modelo culminado. La referencia al tutor se corresponde con artículo 42, que empieza en página 16 y continúa en 17.

El OCR versionado contiene `Art, 24.- Modelo de negocios`, con coma. El separador activo de `rag.split_document` no reconocía ese encabezado. El texto del artículo 24 se incluía entonces en el fragmento anterior etiquetado `Artículo 23`. Se reprodujo con el OCR exacto del corpus: no hace falta atribuir la discrepancia a que el modelo inventara el número. No se dispone del JSON original de esa respuesta para reconstruir todos sus IDs/contexto; se documenta la causa reproducible, no una reconstrucción completa de esa ejecución.

## Cambio y validación

Se admite coma o punto en el separador de artículos. El texto OCR, PDF, manifiesto, políticas y estado de revisión humana no se modifican. El constructor de fuentes usa el metadato del fragmento seleccionado, por lo que separar el encabezado evita heredar artículo 23 para este contenido.

Seis regresiones: cuatro variantes de encabezado, la página 9 del OCR real y el flujo indexar → recuperar → respuesta con modelo simulado → fuente pública artículo 24/página 9. Suite completa local: **147 aprobadas, 89,11 % cobertura app**. Corpus local reindexado: 1.048 fragmentos, instructivo 87 (antes 86). Recuperación léxica: **14/16 positivas, 4/4 negativas, cero errores**. [Diagnóstico, XML y golden set](evidencias/semana-4/citas-articulo-24/).

La corrección no verifica por sí sola la implicación semántica de todas las afirmaciones ni la vigencia de la normativa. No se considera aprobada la revisión humana pendiente del OCR. El contrato probado usa un modelo simulado, no una nueva respuesta de Gemini en producción.

## Aplicación en Neon después del merge y despliegue

1. Confirmar checks/despliegue aprobados y el nuevo SHA en `/health`.
2. Entrar al administrador → **RAG** → seleccionar **UNIANDES Instructivo de Titulación 2017** → **Indexar**. No reemplazar PDF, cambiar aprobación/vigencia ni editar prompts para aplicar esta corrección. En híbrido puede consumir embeddings; el consumo depende de la caché y del proveedor configurado.
3. El índice anterior es persistente y el cambio de código no lo reemplaza automáticamente. Que figure «Indexada» antes de este paso no significa que ya se haya aplicado el nuevo separador. No se alteró la firma de configuración ni se invalida todo el corpus al desplegar.
4. Inspeccionar en RAG el fragmento de `Art, 24.- Modelo de negocios`: debe indicar **Artículo 24, página 9**. Comprobar que no permanece ese encabezado dentro de un fragmento artículo 23.
5. Probar recuperación con «¿Cuáles son las dos fases del modelo de negocios para titulación?» y después realizar la consulta en el chatbot. Si responde esa norma, el enlace correspondiente debe indicar artículo 24/página 9. Guardar resultado real y su SHA/revisión; si el modelo se abstiene o selecciona otra fuente, conservarlo e investigar sin forzar un aprobado.

La evidencia Neon de persistencia anterior conserva su fecha/índice de 1.047: no se reescribe, porque corresponde al estado anterior a esta corrección. No repetir la migración SQLite ni borrar la base. Ese era el pendiente al preparar PR #39; el operador confirmó después su aplicación y consulta corregida, como se registra a continuación. Sigue sin versionarse un JSON nuevo de esa respuesta.

## Comprobación posterior reportada por el operador

Tras el merge del PR #39, el operador mostró el instructivo revisión 2 con 87 fragmentos y una respuesta de Gemini con las dos fases del modelo de negocios y fuente artículo 24/página 9/revisión 2. Se considera verificada esa discrepancia puntual en la conversación; no se incorporó un JSON nuevo de la respuesta ni se atribuye un SHA/revisión Cloud Run no aportado.

La revisión integral del OCR no se marca completada. **\* Debe analizarse el improvement** de revisión asistida definido en [ADR-0005](ADR-0005.md).

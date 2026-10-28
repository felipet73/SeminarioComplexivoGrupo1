# Administración, fuentes RAG y laboratorio de prompts

Implementación del 24 de octubre de 2026. `/admin` pertenece al frontend React. Los recursos se sirven exclusivamente desde endpoints protegidos `/api/admin/*`; ocultar la pantalla no es el mecanismo de seguridad.

## Acceso y ejecución

En `.env` local se configuró `ADMIN_USERNAME=admin` y la contraseña inicial solicitada. `.env.example` contiene `ADMIN_PASSWORD=` vacío. No se devuelve la contraseña al cliente ni se registra en logs. Para una instalación nueva, definirla antes de iniciar el servidor.

```powershell
# terminal 1, desde backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
# terminal 2, desde frontend
npm install
npm run dev
```

Abrir `http://localhost:5173/admin`. Vite reenvía `/api/admin` al backend conservando el Host; así la cookie funciona en el mismo origen sin almacenar tokens en localStorage. Reiniciar Vite al modificar su configuración. Para backend en otro puerto, usar `VITE_ADMIN_API_TARGET=http://127.0.0.1:PUERTO`.

Despliegue: reverse proxy del mismo origen para `/api/admin`, rutas del frontend a `index.html`, HTTPS y `ADMIN_COOKIE_SECURE=true`. La sesión dura 60 minutos, no se renueva indefinidamente y se invalida al reiniciar o cerrar sesión. Cookie HttpOnly/SameSite Strict, token opaco de 40 bytes y comprobación de origen/cabecera en mutaciones. Cinco intentos de login fallidos por IP provocan un bloqueo de cinco minutos. No sustituye controles de infraestructura frente a ataques distribuidos.

Esta versión está diseñada para un proceso del backend. Sesiones y exclusión de simulaciones están en memoria. Para múltiples workers se requiere almacén de sesiones y cola de trabajos compartidos; no desplegar múltiples instancias sin esa adaptación.

## Configuración: prompts y fuentes

El botón «Cancelar» de fuentes descarta el borrador sin escribir en backend. Si se estaba editando/reemplazando, abandona la selección y vuelve a «Agregar una fuente»; si se estaba agregando, limpia el alta. Restablece campos, archivo, errores y casillas; no elimina ni modifica la fuente original. Se deshabilita mientras se guarda.

Las secciones del administrador incorporan controles Contraer/Expandir, con animación respetuosa de la preferencia de movimiento reducido, `aria-expanded`, `aria-controls` e `inert` para que el contenido cerrado no reciba foco. Se mantienen montadas al contraerlas: no se pierden campos ni resultados. Se inician abiertas; el estado no se guarda entre recargas o cambios de pestaña.

«Nueva fuente» abre y limpia siempre el formulario, aun si ya se estaba creando una fuente: restablece título, fechas, texto, notas, archivo, casillas y errores, y enfoca el título. Editar/reemplazar abre el formulario con los datos del documento. Tras guardar se prepara un formulario nuevo; el botón de reinicio se deshabilita durante el guardado para no interrumpirlo.

- V1/V2/V3 se leen de `backend/app/prompts/system_vN.md`. La administración permite consultar contenido/descripción, modificar una versión y crear la siguiente Vn.
- Cada edición crea una revisión con fecha, actor y snapshots antes/después. También se detectan modificaciones externas a los archivos .md y se registran como `filesystem`. La copia SQLite mantiene los snapshots; los archivos reflejan el estado actual.
- El botón «Usar en el chat» cambia la versión activa en backend; el laboratorio no necesita alterar esa versión para comparar variantes. Guardados con revisión esperada impiden pisar una edición concurrente.
- Fuentes: PDF con texto, DOCX, TXT, MD, CSV UTF-8; hasta 10 MB, 200 páginas PDF, un millón de caracteres, 100 documentos. Los PDF escaneados requieren OCR externo previo. DOCX/TXT/MD/CSV tienen unidad lógica de página 1; no se inventa paginación física de Word.
- También se puede escribir información adicional: se carga como fuente Markdown con los mismos metadatos y controles. Las observaciones de gestión se guardan privadas, no se incluyen como evidencia.
- Cada fuente registra título, procedencia, tipo normativa/informativo, inicio/fin de vigencia, aprobación, inclusión, revisión y SHA-256. La fecha se evalúa según Ecuador (UTC-5); un fin de vigencia es inclusivo.
- Deshabilitar una fuente la excluye inmediatamente de recuperación; no se borra su historial. Actualizar metadatos o reemplazar un archivo crea revisión y exige reindexar. Reemplazar el archivo además retira su aprobación, para que se revise nuevamente.
- Originales inmutables bajo `data/admin/files/<id>/<revision>.<ext>`, estado e historial en `data/admin/admin.sqlite3`. Ambos están ignorados por Git; respaldar el directorio completo. El registro es append-only a través de la aplicación, no una firma criptográfica contra cambios directos al disco.
- Los documentos de `data/referencias` son materiales docentes y no se importan como normativa. Se inicia sin fuentes aprobadas: el administrador debe cargar y revisar documentos reales.

Para redactar nuevas versiones se recomienda explicitar rol, tarea, criterios, restricciones, abstención y un ejemplo. El historial conserva las revisiones para comparar su efecto.

## RAG: dividir, indexar, recuperar y citar

Sí corresponde mantener los índices en backend. Se implementó persistencia local con SQLite FTS5/BM25 y un modo híbrido opcional con embeddings multilingües `gemini-embedding-001` (768 dimensiones), guardados por fragmento. No se necesita Chroma para este corpus acotado; si aumenta el volumen, migrar los vectores a pgvector/Chroma preservando IDs y metadatos.

1. Cargar la fuente y revisar vigencia/aprobación en Configuración.
2. Elegir estrategia, tamaño (300–4000 caracteres), solapamiento (< mitad), top-k (1–10), umbral semántico y guardar.
3. Seleccionar documento y pulsar «Dividir e indexar». Se reconocen encabezados Art./Artículo, se conserva sección/página/revisión y se limita a 512 fragmentos por documento y 5000 globales.
4. Inspeccionar fragmentos y probar recuperación. Solo fuentes incluidas, aprobadas, vigentes y con índice compatible entran a la búsqueda.
5. El chat usa la versión de prompt activa más reglas obligatorias de evidencia. Solicita JSON validado con Pydantic y acepta únicamente IDs de fragmentos recuperados. Las URLs, títulos, páginas y hashes se construyen en backend; no los inventa el modelo. Si el formato/citas son inválidos, se abstiene.

El índice se reemplaza en una transacción solo después de generar todos los nuevos fragmentos/vectores; si falla una API de embeddings, se conserva el anterior. Cambiar fragmentación o estrategia invalida el índice compatible hasta reindexar. Cambiar top-k, umbral o prompt activo no requiere reindexación. Se verifica nuevamente la elegibilidad al devolver citas para evitar usar revisiones modificadas durante la generación.

Modo híbrido: las fuentes y consultas se envían a Google para embeddings; consume API. La fusión combina rankings BM25 y coseno con Reciprocal Rank Fusion. Si falla la búsqueda semántica se informa y se usa la léxica. Una prueba de disponibilidad real devolvió un vector de 768 dimensiones; no equivale a una evaluación del recuperador sobre normativa real. Referencia: https://ai.google.dev/gemini-api/docs/embeddings

Las fuentes aprobadas sin URL externa pueden descargarse por `/api/sources/{id}/{revision}` solo mientras estén activas y vigentes; se sirven como adjuntos con `nosniff`. Los originales históricos solo están disponibles para administración. La aprobación autoriza el uso de esa información en el chatbot público.

## Análisis: simulación reproducible

La visualización utiliza conversaciones por caso y respuestas por versión, con las mismas reglas del bot público. Permite completar campos y repetir el caso para todas las versiones; ver [interacción de aclaraciones y simulación](09-aclaraciones-y-campos-necesarios.md). El trabajo conserva las reglas obligatorias del chat junto con los prompts base; la huella individual corresponde a la versión base del prompt. También se conserva la salida original del modelo, separada de la respuesta validada que vería el usuario.

- Selección múltiple de hasta cinco versiones, un proveedor y hasta diez casos. Botón para cargar los 10 ejemplos propuestos: 7 normales, 2 negativos y 1 fuera de dominio. No reemplazan FAQ levantadas ni un golden set validado.
- Pregunta y respuesta/artículo esperado editable por caso. Con RAG, todas las variantes reciben exactamente la misma recuperación para cada pregunta.
- Captura versión, revisión y contenido completo del prompt; SHA-256 por resultado. Una edición posterior no altera el experimento guardado.
- Un trabajo en segundo plano por proceso, con progreso consultable. Al reiniciar, los trabajos inconclusos se marcan interrumpidos y pueden ejecutarse nuevamente. No hay reanudación parcial automática.
- Las simulaciones no cambian al proveedor de respaldo: así se evita comparar modelos diferentes sin advertirlo. Los errores de cada variante quedan separados y no detienen el resto.
- Cada respuesta muestra modelo real, tiempo de generación, tokens de entrada/salida/total reportados por SDK y errores. Tokens desconocidos permanecen como N/D. El resumen por versión incluye éxitos, fallos y latencia media.
- Desde la actualización del 28 de octubre de 2026 no se solicita comparación, calificación, resumen ni elección de ganador a un juez de IA. Se generan únicamente las respuestas y se muestran las mediciones. La referencia esperada se revisa manualmente, no se usa para dirigir la respuesta del modelo.
- Los tokens mostrados son los reportados para generación; embeddings son operaciones adicionales. `evaluation_mode=measurements_only` identifica los trabajos nuevos. Se puede exportar el experimento completo en JSON, incluidos snapshots, métricas y trazas. Los contenidos permanecen privados bajo la sesión admin, no aparecen en `/metricas`. Los informes antiguos no se borran del almacenamiento, pero la pantalla ya no presenta evaluaciones de IA.

Cada experimento conserva también la configuración RAG y los fragmentos recuperados, además de la duración total. Esto permite revisar posteriormente qué evidencia recibió cada variante, incluso si se reemplaza una fuente.

Las secciones incluyen ayudas ampliadas y recuadros explicativos. Después de indexar, recuperar o simular se muestran trazas del backend en diagramas de nodos seleccionables, sincronizados con sus pasos y detalles. Véase [guía de ayudas y procesos](10-ayudas-y-trazas-rag.md).

## Pruebas

```powershell
# backend
.\.venv\Scripts\python.exe -m pytest -q
# frontend
npm run build
npm run test
npm run test:admin
```

`test:admin` levanta backend 9019 y frontend 4180 aislados, con contraseña, fuentes, prompts, métricas y LLM de prueba. No consume proveedores reales ni modifica fuentes de producción. Requiere Chromium (`npx playwright install chromium`). Las pruebas verifican login/logout, bloqueo, CSRF, revisiones, fechas, exclusión, indexación, citas falsas, embeddings simulados y comparación de versiones. Capturas en `frontend/test-results` ignoradas por Git.

## Qué sigue pendiente

Validar la vigencia real de documentos, levantar FAQ de campo, medir el recuperador y exactitud sobre 20 casos con artículos esperados; la validación de IDs no demuestra por sí sola que cada afirmación esté respaldada semánticamente. Continúan pendientes herramientas deterministas de requisitos/plazos/checklist, memoria de conversación, SSE real desde SDK, cancelación, rate limits del chat, evaluación de accesibilidad/cobertura y despliegue público. OCR y tablas complejas requieren revisión humana antes de activar fragmentos.

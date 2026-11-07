# ADR: agente educativo y alcance controlado

> **Estado de entrega al 7 de noviembre de 2026:** Consultar el [checklist vigente s4a–s4k](14-checklist-entrega-final.md). Despliegue y 35 casos públicos aprobados; el historial, evaluación final comparable y demás pendientes se distinguen allí.

Actualización del 6 de noviembre de 2026: el chat comparte un presupuesto global por proceso de 30 POST en 60 segundos entre `/api/chat`, `/api/chat/stream` y `/api/agente`, definido en `config/parametros.yaml`. Se responde 429 con Retry-After accesible por CORS antes de invocar el flujo. No se confía en cabeceras de IP enviadas por el cliente ni se declara una cuota por usuario o distribuida. Reiniciar el proceso reinicia la ventana; múltiples instancias amplían el presupuesto.

El módulo de credenciales legacy está eliminado. Un detector AST bloquea contraseñas/claves constantes de baja entropía en código de aplicación, mientras `--historial-legacy` informa la presencia histórica sin imprimir valores. La credencial fue aceptada por la imagen antigua antes de corregir el despliegue. Las rutas antiguas ya se probaron retiradas y Actions 42389025186 aprobó el despliegue de `c1a5f3f`. El historial y la revocación de cualquier reutilización requieren su propia evidencia; un ignore del escáner no los resuelve.

El despliegue implementado y ejecutado exige los cinco jobs de calidad, promueve la imagen que pasó el smoke y verifica el SHA mediante `/health.revision`. La etiqueta identifica el build declarado, no una firma criptográfica. La persistencia de SQLite y sesiones sigue siendo local; max-instances 1 no resuelve esa limitación. Las decisiones de infraestructura y la revisión/aprobación del OCR requieren intervención del equipo. Detalles en [operación y despliegue](13-despliegue.md).

Fecha: 31 de octubre de 2026. Grupo 1. Implementación de la Entrega 3; no es una transcripción de los archivos originales del taller, que no se aportaron.

El chat usa `backend/app/agente.py` desde el flujo compartido con el laboratorio. El modelo devuelve un JSON final o una solicitud de herramienta. Se valida con Pydantic antes de ejecutar; no se interpreta código ni se permite elegir funciones arbitrarias. `PERMITIDAS` contiene buscar_fragmentos, consultar_requisitos, generar_checklist, calcular_plazo y registrar_solicitud_tutor. `MAX_ITER=4`, configurado en `config/parametros.yaml`, limita las llamadas al modelo por consulta. Una salida inválida o el agotamiento del bucle produce abstención.

`ejecutar_agente` contiene el bucle real `for vuelta in range(MAX_ITER)`. Siguiendo la organización de la guía, `PERMITIDAS` relaciona cada nombre con `(modelo_entrada, función)`; los contratos y las funciones libres están en `backend/app/tools/academicas.py`. Los parámetros compartidos se leen en `app/parametros.py`. El protocolo de llamadas sigue siendo JSON validado a través de ClienteLLM, compatible con Gemini y OpenAI; no utiliza directamente `chat.completions.tool_calls` del ejemplo. La respuesta de cada herramienta se entrega al siguiente turno en el contexto. Las propuestas se pausan para una decisión humana persistente fuera del bucle.

La API publica `POST /api/agente` y `POST /api/agente/confirmar/{id}`. El chat y las rutas anteriores de confirmación siguen usando la misma implementación y permiten conservar compatibilidad con el frontend.

Las consultas y el checklist devuelven pasajes con procedencia para que el modelo los interprete. No comparan con un expediente estudiantil ni certifican aptitud. El calendario usa fecha ISO y días hábiles declarados: excluye fecha inicial y fines de semana, no incorpora feriados ni fija vencimientos institucionales. Trabaja con fechas e enteros; Decimal no corresponde a este cálculo, ya que no hay montos. No se copió el plazo ficticio del ejemplo del HTML ni su artículo TODO.

`REQUIEREN_OK` incluye registrar_solicitud_tutor. Solo prepara un borrador académico demo local. La API devuelve argumentos exactos, caducidad e identificador; React muestra Confirmar/Cancelar. Hasta confirmar no existe solicitud en `solicitud_demo`. La decisión usa una capacidad secreta no almacenada en claro, válida para esa propuesta. La confirmación y el registro ocurren en una transacción SQLite; el ID de la acción es la clave idempotente. Repetir una decisión no duplica registros; una decisión contradictoria devuelve 409; una propuesta caducada devuelve 410. No hay correos, envíos institucionales ni asignación real de tutor.

La auditoría registra cuándo se propuso y quién decidió mediante `usuario_demo:<huella de capacidad>`, herramienta, argumentos y resultado. Esa huella identifica la capacidad utilizada, no una identidad institucional autenticada. Esta limitación es deliberada para un MVP con datos ficticios.

Se conserva SQLite FTS5/BM25 y vectores persistentes de 768 dimensiones con coseno y fusión RRF. Es una alternativa a Chroma, permitida por la guía cuando satisface el mismo resultado. No se declara Chroma ni un índice ANN inexistente. El límite es 5000 fragmentos y búsqueda exhaustiva; cambiar de base no mejora por sí solo la calidad de las fuentes. Cambiar el modelo de embeddings obliga a reindexar y nunca mezcla espacios vectoriales. Gemini y OpenAI se seleccionan explícitamente; no hay cambio silencioso de proveedor.

La validación posterior comprueba pertenencia de IDs recuperados, revisión vigente e integridad del contrato. No demuestra automáticamente que cada afirmación esté implicada por la cita: las respuestas esperadas se revisan con las fuentes. La evaluación real y las pruebas con modelo doble se publican por separado.

Fuera de alcance: aprobar temas, alterar notas o récords, decidir titulaciones, tramitar solicitudes ante terceros y realizar asesoría de otros dominios. El despliegue público corresponde a la semana 4.

El laboratorio comparativo comparte validación y herramientas de lectura, pero deshabilita propuestas de escritura. Así las simulaciones no crean acciones ni guardan capacidades secretas en el historial de experimentos.

El checklist construye ítems extractivos de las fuentes normativas recuperadas. Conserva el texto de cada pasaje, documento, sección, página e ID; marca todos como pendientes de verificar y `completo=false`. No convierte fuentes informativas en obligaciones ni deduce que el estudiante cumplió un requisito. El modelo explica su aplicabilidad y señala las reglas internas que falten.

Referencia de implementación del proveedor alternativo: [Create embeddings, documentación oficial de OpenAI](https://developers.openai.com/api/reference/python/resources/embeddings/methods/create). Se usa la API con dimensiones explícitas y formato float; el proveedor se selecciona en configuración, nunca mezclando sus vectores con los de Gemini.

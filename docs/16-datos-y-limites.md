# Tratamiento de datos y límites del asistente

Estado del 7 de noviembre de 2026; alcance educativo de demostración. Ver [checklist final](14-checklist-entrega-final.md).

La interfaz identifica el uso de IA, indica que la orientación no es una resolución institucional, pide verificar fuentes y muestra “No compartas contraseñas, datos sensibles ni información de terceros”. El contexto académico es opcional y acotado; no requiere nombre, cédula ni expediente. No se conectan sistemas de matrícula o expedientes universitarios.

La pregunta y el contexto enviados por el usuario, junto con los pasajes recuperados, se transmiten al proveedor generativo elegido y, si procede, al respaldo. En modo híbrido también se envían textos de documentos o consultas al proveedor de embeddings. Por eso no deben introducirse datos personales o material que no pueda tratarse en esos servicios. Las condiciones y retención propias de los proveedores deben revisarse antes de un uso institucional. El cliente OpenAI de generación configura store=False; esto no equivale a una garantía universal de retención cero de ambos proveedores.

La conversación de la interfaz vive en memoria de la sesión y no se ofrece una memoria conversacional persistente en servidor. Las métricas registran metadatos técnicos, sin preguntas, respuestas, claves, IP ni contexto académico; su endpoint es público. Las simulaciones administrativas conservan casos, salidas, trazas y evidencia bajo autenticación, por lo que deben usar datos ficticios. Las cargas administrativas y borradores demo son almacenamiento local de la aplicación; no se presentan como expedientes institucionales ni como durabilidad garantizada en Cloud Run.

La capacidad de confirmación de un borrador se muestra al cliente que lo propuso y solo se conserva su hash en el estado local. La confirmación no prueba identidad universitaria y nunca envía una solicitud a terceros. Las credenciales de modelos y administración permanecen en configuración privada/Secret Manager; no se muestran en frontend ni documentación. No se pide compartir `.env` ni valores de secretos para diagnosticar.

Las citas validan pertenencia a fragmentos elegibles; no prueban implicación semántica total. La vigencia y aprobación de la fuente requieren intervención humana. Los marcadores de inyección son controles parciales y el presupuesto de consultas es global por proceso. La aplicación es orientativa y requiere Secretaría Académica para decisiones, plazos legales o certificaciones.

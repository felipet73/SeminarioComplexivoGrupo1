# Actuación sobre credenciales legacy

## Registro y alcance

Constancia incorporada el **8 de noviembre de 2026 (UTC)**, a partir de la confirmación directa del operador en esta conversación: «Ya cambié e hice nuevo despliegue y entré con la nueva». La fecha exacta de la operación y su zona horaria no fueron aportadas; la fecha de registro no se presenta como hora de ejecución.

| Dato | Registro |
| --- | --- |
| Proyecto | `agentetitulacion` |
| Servicio | Cloud Run, `titulacion-rag`, región `us-central1` |
| Entorno objeto de la actuación | Producción, según el contexto y confirmación del operador |
| Configuración intervenida | Contraseña administrativa `ADMIN_PASSWORD` |
| Referencia mostrada en Cloud Run | `ADMIN_PASSWORD` → `admin-password`, versión configurada **2** en la captura más reciente aportada por el operador |
| Nueva versión mostrada | Versión **2**, habilitada; creación visible **7/11/26, 9:47 p. m.**, sin zona horaria visible. La captura más reciente muestra el encabezado `admin-password` y el recurso `projects/386902880383/secrets/admin-password` |
| Versión anterior | Versión **1**, **inhabilitada** en la captura más reciente (anteriormente habilitada) |
| Responsable | Operador que confirmó la actuación; nombre pendiente de incorporar |
| Revisión de Cloud Run y SHA de aplicación después del cambio | Pendientes de adjuntar; no se infieren del último commit de Git |
| Evidencia disponible de la operación | Confirmación del operador y capturas sucesivas de metadatos revisadas en el chat; imágenes aún no versionadas en el repositorio. Falta reporte posterior ligado a la nueva revisión |

No se registran valores de contraseñas, claves, tokens, hashes de contraseñas ni respuestas autenticadas del panel.

## Contraseña administrativa: cambio y comprobación realizados

El operador confirmó haber cambiado la contraseña administrativa, realizado un nuevo despliegue e iniciado sesión correctamente con la nueva contraseña. Se registra así una **rotación operativa declarada y comprobación manual de acceso exitoso por el operador**. No se afirma que el asistente accediera al proyecto de Google Cloud o comprobara el valor del secreto.

La confirmación acredita el cambio y el acceso con la nueva contraseña dentro del alcance declarado. No acredita por sí sola su generación aleatoria, unicidad entre otros servicios, revocación de sesiones previas ni retirada de todas las revisiones antiguas. No se volvió a probar la contraseña histórica.

Para completar la trazabilidad, adjuntar únicamente metadatos: fecha/hora con zona, responsable, referencia y versión del secreto efectivamente usada, nombre de la revisión que recibe tráfico y SHA que devuelve `/health`. Una captura puede mostrar esos metadatos, pero debe ocultar el valor del secreto y cualquier token.

## Metadatos adicionales aportados mediante capturas

Las primeras capturas mostraban `ADMIN_PASSWORD` → `admin-password:latest` y las versiones 1 y 2 habilitadas. Las capturas posteriores actualizan esa evidencia: el secreto se identifica expresamente como `projects/386902880383/secrets/admin-password`, la versión **2** permanece habilitada y la **1** figura inhabilitada. En el formulario de Cloud Run, `ADMIN_PASSWORD` referencia explícitamente la versión **2**. Los proveedores conservan `gemini-api-key:latest` y `openai-api-key:latest`. No se muestran valores secretos.

La fijación de la referencia a **2** y la inhabilitación de **1** están acreditadas visualmente en las pantallas aportadas. El formulario no muestra por sí solo una implementación completada ni identifica la revisión que recibe tráfico. Falta vincular esta configuración concreta a una revisión desplegada y comprobar el acceso después de esa última implementación; el acceso confirmado antes no se atribuye automáticamente a esta configuración posterior.

Inhabilitar la versión 1 impide nuevas lecturas de esa versión, pero no borra valores ya cargados por instancias existentes ni elimina la contraseña del historial Git. No se afirma que todas las revisiones antiguas hayan dejado de ser accesibles. La versión no se muestra destruida y no es necesario destruirla para registrar su inhabilitación.

## Clave JWT histórica y mecanismo retirado

La contraseña y la clave JWT del antiguo `backend/app/seguridad.py` eran credenciales funcionales históricas; no son los falsos positivos del advisory excluidos en `.gitleaksignore`. El módulo se eliminó en `08ef882`. El mecanismo administrativo actual usa `ADMIN_PASSWORD` inyectada y sesiones opacas, y no consume aquella clave JWT. No se declara una rotación de JWT: el mecanismo que la utilizaba fue retirado.

La retirada del módulo y sus rutas está documentada en la [auditoría histórica](../../15-auditoria-credenciales-historicas.md). Los valores siguen recuperables del historial Git. La revisión de otras aplicaciones, entornos, URLs o revisiones antiguas y la limpieza coordinada del historial continúan pendientes; este registro no certifica «historial limpio» ni riesgo cero.

## Pruebas públicas y validación posterior

La evidencia completa `produccion-279580e-20261107-214127.json`, incorporada mediante el PR #25, registra 35/35 correctos, cero omitidos y revisión esperada `279580e7276cff1b3cd7b625caabd8e2cd510fcc`, con fecha `2026-11-08T02:41:45.806842+00:00`. Se conserva como prueba de esa ejecución. **No se presenta como prueba posterior a esta rotación:** no se aportaron fecha ni revisión suficientes para establecer esa relación.

Después de identificar el SHA realmente desplegado, repetir el procedimiento del [plan de cierre](../../19-pasos-cierre-y-compresion.md), guardar otro JSON completo con nombre propio y verificar los casos de rutas legacy retiradas, además del resultado global. Si el despliegue manual conserva el SHA probado pero cambia la configuración, registrar también la revisión de Cloud Run y la fecha: el SHA de código por sí solo no identifica la versión del secreto.

## Estado de cierre

- **Confirmado por el operador:** cambio de contraseña administrativa, nuevo despliegue y acceso manual con la nueva contraseña.
- **Acreditado mediante capturas posteriores:** secreto `admin-password` identificado, versión 2 habilitada, versión 1 inhabilitada y referencia `ADMIN_PASSWORD` fijada a 2 en el formulario de Cloud Run.
- **Pendiente de trazabilidad técnica:** responsable nominal, fecha exacta con zona, versión efectivamente cargada por la revisión de Cloud Run y SHA publicado; reporte HTTP posterior asociado a esa actuación. La versión 2 y su fecha visible ya constan como metadatos de captura.
- **Pendientes independientes:** revisión de reutilización en otros entornos y revisiones accesibles; decisión y ejecución coordinadas sobre el historial Git.

La rotación declarada mejora la protección del servicio actualizado. El requisito global de protección de credenciales sigue parcial mientras falte acreditar el resto de su alcance.

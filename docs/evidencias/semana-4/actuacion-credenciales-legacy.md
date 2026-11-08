# Actuación sobre credenciales legacy

## Registro y alcance

Constancia incorporada el **8 de noviembre de 2026 (UTC)**, a partir de la confirmación directa del operador en esta conversación: «Ya cambié e hice nuevo despliegue y entré con la nueva». La fecha exacta de la operación y su zona horaria no fueron aportadas; la fecha de registro no se presenta como hora de ejecución.

| Dato | Registro |
| --- | --- |
| Proyecto | `agentetitulacion` |
| Servicio | Cloud Run, `titulacion-rag`, región `us-central1` |
| Entorno objeto de la actuación | Producción, según el contexto y confirmación del operador |
| Configuración intervenida | Contraseña administrativa `ADMIN_PASSWORD` |
| Referencia mostrada en Cloud Run | `ADMIN_PASSWORD` → `admin-password`, versión configurada `latest`; captura aportada por el operador |
| Nueva versión mostrada | Versión **2**, habilitada; creación visible **7/11/26, 9:47 p. m.**, sin zona horaria visible. La lista se aporta en el contexto de `admin-password`, aunque el recorte no muestra el encabezado del secreto |
| Versión anterior | Versión **1**, también habilitada en la captura |
| Responsable | Operador que confirmó la actuación; nombre pendiente de incorporar |
| Revisión de Cloud Run y SHA de aplicación después del cambio | Pendientes de adjuntar; no se infieren del último commit de Git |
| Evidencia disponible de la operación | Confirmación del operador y dos capturas de metadatos revisadas en el chat; imágenes aún no versionadas en el repositorio. Falta reporte posterior ligado a la nueva revisión |

No se registran valores de contraseñas, claves, tokens, hashes de contraseñas ni respuestas autenticadas del panel.

## Contraseña administrativa: cambio y comprobación realizados

El operador confirmó haber cambiado la contraseña administrativa, realizado un nuevo despliegue e iniciado sesión correctamente con la nueva contraseña. Se registra así una **rotación operativa declarada y comprobación manual de acceso exitoso por el operador**. No se afirma que el asistente accediera al proyecto de Google Cloud o comprobara el valor del secreto.

La confirmación acredita el cambio y el acceso con la nueva contraseña dentro del alcance declarado. No acredita por sí sola su generación aleatoria, unicidad entre otros servicios, revocación de sesiones previas ni retirada de todas las revisiones antiguas. No se volvió a probar la contraseña histórica.

Para completar la trazabilidad, adjuntar únicamente metadatos: fecha/hora con zona, responsable, referencia y versión del secreto efectivamente usada, nombre de la revisión que recibe tráfico y SHA que devuelve `/health`. Una captura puede mostrar esos metadatos, pero debe ocultar el valor del secreto y cualquier token.

## Metadatos adicionales aportados mediante capturas

La pantalla de variables y secretos muestra `GEMINI_API_KEY` → `gemini-api-key:latest`, `ADMIN_PASSWORD` → `admin-password:latest` y `OPENAI_API_KEY` → `openai-api-key:latest`. No muestra valores secretos. La lista de versiones muestra la versión 2 habilitada y la versión 1 todavía habilitada. Se registra lo visible sin inferir la zona horaria ni que la captura del formulario pruebe por sí sola su despliegue.

`latest` es una referencia dinámica. En variables de entorno Cloud Run obtiene el valor al iniciar la instancia; la captura no demuestra qué versión cargó cada instancia o revisión. Para una evidencia inequívoca de esta rotación, fijar `ADMIN_PASSWORD` a la versión **2**, desplegar y comprobar el acceso y la revisión que recibe tráfico. Conservar metadatos de esa revisión y repetir las pruebas públicas. Esto no exige cambiar las referencias de los proveedores para documentar esta actuación.

Tras comprobar que los servicios que deben seguir activos utilizan la versión nueva, inhabilitar la versión 1 si ya no tiene consumidores legítimos. No destruirla como primer paso. Inhabilitar una versión impide nuevas lecturas, pero no borra valores ya cargados por instancias existentes ni elimina la contraseña del historial Git. No se considera inhabilitada a partir de las capturas aportadas.

## Clave JWT histórica y mecanismo retirado

La contraseña y la clave JWT del antiguo `backend/app/seguridad.py` eran credenciales funcionales históricas; no son los falsos positivos del advisory excluidos en `.gitleaksignore`. El módulo se eliminó en `08ef882`. El mecanismo administrativo actual usa `ADMIN_PASSWORD` inyectada y sesiones opacas, y no consume aquella clave JWT. No se declara una rotación de JWT: el mecanismo que la utilizaba fue retirado.

La retirada del módulo y sus rutas está documentada en la [auditoría histórica](../../15-auditoria-credenciales-historicas.md). Los valores siguen recuperables del historial Git. La revisión de otras aplicaciones, entornos, URLs o revisiones antiguas y la limpieza coordinada del historial continúan pendientes; este registro no certifica «historial limpio» ni riesgo cero.

## Pruebas públicas y validación posterior

La evidencia completa `produccion-279580e-20261107-214127.json`, incorporada mediante el PR #25, registra 35/35 correctos, cero omitidos y revisión esperada `279580e7276cff1b3cd7b625caabd8e2cd510fcc`, con fecha `2026-11-08T02:41:45.806842+00:00`. Se conserva como prueba de esa ejecución. **No se presenta como prueba posterior a esta rotación:** no se aportaron fecha ni revisión suficientes para establecer esa relación.

Después de identificar el SHA realmente desplegado, repetir el procedimiento del [plan de cierre](../../19-pasos-cierre-y-compresion.md), guardar otro JSON completo con nombre propio y verificar los casos de rutas legacy retiradas, además del resultado global. Si el despliegue manual conserva el SHA probado pero cambia la configuración, registrar también la revisión de Cloud Run y la fecha: el SHA de código por sí solo no identifica la versión del secreto.

## Estado de cierre

- **Confirmado por el operador:** cambio de contraseña administrativa, nuevo despliegue y acceso manual con la nueva contraseña.
- **Pendiente de trazabilidad técnica:** responsable nominal, fecha exacta con zona, versión efectivamente cargada por la revisión de Cloud Run y SHA publicado; reporte HTTP posterior asociado a esa actuación. La versión 2 y su fecha visible ya constan como metadatos de captura.
- **Pendientes independientes:** revisión de reutilización en otros entornos y revisiones accesibles; decisión y ejecución coordinadas sobre el historial Git.

La rotación declarada mejora la protección del servicio actualizado. El requisito global de protección de credenciales sigue parcial mientras falte acreditar el resto de su alcance.

# GitHub Support: solicitud enviada, caso #4985701

**Estado vigente: enviada por el propietario; pendiente de respuesta y actuación de GitHub Support.** Capturas aportadas en la conversación muestran «Tu mensaje ha sido enviado correctamente» y el ticket #4985701 de `felipet73`, prioridad Normal, estado abierto. No confirman retirada de referencias ni purga. La pantalla indica creación «ahora», sin fecha/hora absoluta visible; ese dato queda pendiente de la confirmación por correo.

El texto siguiente se conserva como referencia del contenido preparado para la solicitud. No contiene valores de credenciales.

Asunto: Solicitud de revisión de referencias de PR y cachés tras retirar credenciales históricas

Repositorio: https://github.com/felipet73/SeminarioComplexivoGrupo1
Propietario solicitante: felipet73 (enviar desde la cuenta autorizada del repositorio).

Se expusieron históricamente una contraseña administrativa y una clave JWT en backend/app/seguridad.py. No se adjuntan sus valores. La contraseña de ejecución fue cambiada y el mecanismo JWT/rutas legacy se retiró del código operativo; no se afirma ausencia de reutilización en todos los entornos.

Se conservó un respaldo privado, se reescribieron atómicamente 27 ramas con leases y se mantuvieron las 28 ramas. Main inmediatamente después de la limpieza: 2482401e50b607296151b5a7ac47738536c0b2d5 (corte histórico, no HEAD vigente). Un clon nuevo sin refs de PR pasa el detector histórico y el activo; el código actual de aplicación se conservó. GitHub mantiene referencias de PR de solo lectura y el commit histórico todavía responde en la API.

Commits históricos de referencia:
- 1348b065feaba46b6dfea20bf26b1f7d8b455dc8
- 3e38895fff1e60d983b7bf43206e86d69c1be2c2
Ruta sensible retirada: backend/app/seguridad.py.

Primeros commits cambiados indicados por git-filter-repo (SHA anterior y SHA filtrado, respectivamente):
- 2a958636a569a300aa79877e22bb0c686a595e69 f7a5bb8e71bfc1e372c4256f2ece690a0ceeebbb

Referencias de PR afectadas detectadas en el espejo:
- refs/pull/10/head
- refs/pull/17/head
- refs/pull/18/head
- refs/pull/19/head
- refs/pull/2/head
- refs/pull/20/head
- refs/pull/21/head
- refs/pull/22/head
- refs/pull/23/head
- refs/pull/24/head
- refs/pull/25/head
- refs/pull/26/head
- refs/pull/27/head
- refs/pull/28/head
- refs/pull/29/head
- refs/pull/3/head
- refs/pull/30/head
- refs/pull/31/head
- refs/pull/32/head
- refs/pull/4/head
- refs/pull/5/head
- refs/pull/6/head
- refs/pull/7/head
- refs/pull/8/head
- refs/pull/9/head

Solicitamos evaluar la retirada de referencias/vistas en caché que permitan acceder al contenido sensible anterior, siguiendo su procedimiento de eliminación de datos sensibles. Podemos aportar el mapa de commits y referencias por un canal privado; no enviar valores de credenciales ni el respaldo completo.

La publicación de ramas no elimina por sí sola forks/clones/cachés ni las refs internas de PR. Indiquen qué referencias pueden retirarse y qué actuaciones adicionales necesita realizar el propietario.

El propietario completó el envío mediante GitHub Support y aportó confirmación; el asistente no envió el formulario. Seguimiento desde la cuenta propietaria en https://support.github.com/ .

## Registro del envío

| Campo | Estado registrado |
| --- | --- |
| Enviado desde cuenta propietaria | Confirmado por capturas del formulario y listado de tickets de felipet73 |
| Fecha de envío | Fecha/hora absoluta pendiente de correo; la captura indica «ahora» |
| Número de caso | **#4985701** |
| Estado/respuesta de Support | **Abierto, prioridad Normal; pendiente de respuesta y actuación** |
| Verificación posterior de refs/cachés | Pendiente de respuesta y comprobación |

El envío fue realizado por el propietario desde su sesión; el asistente registró las capturas aportadas. La respuesta generada por IA durante la preparación no equivale a respuesta del equipo de soporte. Que exista ticket no demuestra que las referencias ya se retiraron: esperar comunicación del equipo y comprobar después refs/cachés/commit antes de marcar el cierre completo. No se versionan correos privados, valores ni respaldo del repositorio.

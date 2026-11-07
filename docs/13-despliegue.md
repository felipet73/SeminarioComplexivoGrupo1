# Operación y despliegue - Vercel y Cloud Run

Servicio existente: `titulacion-rag`, región `us-central1`, [URL backend](https://titulacion-rag-386902880383.us-central1.run.app). Frontend: [Vercel](https://seminario-complexivo-grupo1.vercel.app/), Root Directory `frontend`. El proxy y fallback SPA se definen en `frontend/vercel.json`.

## Construcción verificable

Ejecutar desde la raíz del repositorio, con el working tree limpio:

```powershell
$revisionProyecto = git rev-parse HEAD
docker build --build-arg APP_REVISION=$revisionProyecto -f backend/Dockerfile -t titulacion-rag:local .
docker run --rm --name titulacion-rag-local -p 8080:8080 titulacion-rag:local
# En otra terminal:
python scripts/smoke_container.py --url http://127.0.0.1:8080 --expected-revision $revisionProyecto
```

La semilla léxica incluida permite readiness y pruebas sin claves. La imagen usa Python 3.12 slim, usuario sin privilegios y `PORT`. `.dockerignore` excluye venv, estados SQLite y archivos de credenciales; el archivo público del frontend es la excepción explícita. `/health.revision` incorpora el argumento de build. No es una firma criptográfica: identifica el commit declarado por el proceso de construcción.

Para usar proveedores o administración local, pasar un archivo de entorno privado con `--env-file .env`, sin incluirlo en la imagen ni pegar claves en comandos o documentación. El arranque y el smoke no necesitan claves de modelos.

## Pipeline preparado

`.github/workflows/ci.yml` conserva las pruebas en push/PR y añade `desplegar` con `needs: [secretos, backend, frontend, navegador, contenedor]`. Solo puede desplegar en main, por push o ejecución manual. Las evaluaciones con API reales son manuales y requieren activar `evaluar_modelo_real`.

El job contenedor guarda **la misma imagen que pasó el smoke**, etiquetada con el SHA. El job de despliegue descarga ese artefacto, publica en Artifact Registry y actualiza el servicio existente; no reconstruye otra imagen después de probar. Se verifica SHA, readiness, retirada de rutas y SSE, y luego los 35 casos contra las URLs públicas, incluidos tres de generación real (dos directos y uno por proxy SSE de Vercel). El job exige `--incluir-modelo`; una abstención, respuesta vacía, falta de modelo, cita incorrecta, HTTP 500 o SSE incompleto falla la validación. Estas tres consultas consumen cuota del proveedor de ejecución, sin exponer sus claves al runner. Un fallo posterior al deploy deja el job rojo: requiere intervención; no se anuncia rollback automático a una revisión posiblemente vulnerable.

No se cancelan workflows main a mitad del despliegue al entrar otro push. PR y otras ramas conservan cancelación de corridas anteriores. El entorno de GitHub es `production`; sus revisores y restricciones deben configurarse por el equipo si se desea aprobación manual.

## Configuración que falta en GitHub y Google Cloud

| Tipo | Nombre | Valor requerido |
|---|---|---|
| Variable | `GCP_PROJECT_ID` | ID real del proyecto; no se deduce del número de la URL |
| Variable | `GCP_AR_REPOSITORY` | Repositorio Docker ya creado en Artifact Registry, región us-central1 |
| Variable, recomendado | `GCP_WORKLOAD_IDENTITY_PROVIDER` | Proveedor WIF restringido al repositorio y rama main |
| Variable, para WIF | `GCP_SERVICE_ACCOUNT` | Cuenta de despliegue autorizada |
| Secreto, alternativa del ejemplo docente | `GCP_SA_KEY` | JSON de cuenta de servicio; solo si no se usa WIF |

El workflow falla al faltar configuración; no declara un deploy omitido como aprobado. Se utiliza [auth@v3](https://github.com/google-github-actions/auth) y [deploy-cloudrun@v3](https://github.com/google-github-actions/deploy-cloudrun). WIF evita guardar una clave JSON de larga duración. La cuenta debe poder publicar imágenes, actualizar el servicio y usar su cuenta de ejecución; seguir los permisos documentados de esas acciones y restringirlos a los recursos necesarios.

Las claves LLM y `ADMIN_PASSWORD` pertenecen a la configuración/secrets **de ejecución de Cloud Run**, no al frontend ni al build. El workflow mezcla las variables públicas con las existentes y conserva las referencias a secretos. Se establecen APP_ENV production, cookie Secure, CORS con el dominio exacto y APP_REVISION SHA. Límites del servicio: memoria 1 GiB, máximo 1 instancia, mínimo 0. Mantener el IAM público del servicio según la configuración existente; no se cambia automáticamente desde este workflow.

## Cierre de la falla crítica

La prueba remota inicial confirmó que `/admin/login` aún aceptaba la credencial histórica. El código actual ya elimina ese módulo y ambas rutas. Para cerrar la incidencia:

1. Construir/publicar una imagen del commit revisado y desplegarla en el servicio indicado, con todo el tráfico dirigido a la revisión corregida.
2. Comprobar SHA y que POST a ambas rutas antiguas devuelve **404**; no basta que exijan un token.
3. Revocar/rotar cualquier contraseña actual o clave JWT que haya reutilizado el valor expuesto. Revisar otras revisiones/URLs etiquetadas que sigan accesibles. No reutilizar la credencial histórica.
4. Ejecutar las pruebas de `docs/08-pruebas.md`; guardar la evidencia posterior. Verificar en Cloud Logging el traceback si el 500 persiste.

Ni la ruta antigua ni su clave son usadas por la autenticación actual `admin_auth.py`. Retirar la ruta invalida su utilidad para esa revisión, pero no borra valores del historial ni cierra otras copias del servicio.

## Historial y estado persistente

`python scripts/check_secrets.py` detecta ahora asignaciones fijas de secretos/contraseñas en código activo, además de formatos de API keys. `--historial-legacy` audita el módulo retirado en todas las referencias y continúa dando exit 1. La evidencia está en `docs/evidencias/semana-4/historial-credenciales.json`. No se añadieron excepciones para ocultar esa credencial ni se ejecutó un force push.

Una limpieza del historial requiere una copia espejo de respaldo, enumerar ramas/tags afectados, coordinar todos los clones y reescribir la ruta retirada, con publicación forzada autorizada y revisión de referencias de PR/cachés. No sustituye la revocación del servicio activo. La [guía de GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) detalla ese procedimiento.

La semilla recupera el corpus inicial, pero las cargas administrativas, decisiones y sesiones locales no son persistencia compartida. `RAG_DATA_DIR` cambia la ubicación, no crea almacenamiento duradero. El límite de una instancia tampoco asegura durabilidad ni exclusión entre revisiones durante un despliegue. Un bucket montado por Cloud Storage FUSE no ofrece el bloqueo de archivos requerido por SQLite; [limitaciones oficiales](https://docs.cloud.google.com/run/docs/configuring/services/cloud-storage-volume-mounts#limitations). No se presenta ese montaje como solución. La persistencia duradera necesita una decisión y configuración de infraestructura antes de usar datos importantes; los borradores siguen siendo demostraciones con datos ficticios.

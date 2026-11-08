# Activación de PostgreSQL en Neon: datos antes de cambiar el servicio

Estado actualizado: **importación ejecutada y activación en Cloud Run reportada por el operador; ensayo remoto entre revisiones pendiente de evidencia**. Las capturas de Neon muestran 6 documentos, 3 prompts, 1 configuración, 1.047 fragmentos, 1.047 entradas de búsqueda, 6 archivos y 12 eventos de auditoría en el momento de importar. Después el operador indicó reindexación del instructivo (revisión 2) y compartió el panel con seis documentos indexados. Estos conteos son del corte de importación, no un nuevo inventario tras la reindexación. No prueban por sí solos durabilidad tras reiniciar.

El secreto `rag-database-url`, versión 1, se vinculó como `RAG_DATABASE_URL` según la captura del formulario. El asistente no dispone del DSN, no consultó la base real ni operó Cloud Run. Cloud SQL continúa diferido por costos. La secuencia inferior queda como procedimiento reproducible, no como tareas todas pendientes para la base ya importada.

### Incidente del reporte de migración

El importador confirmó la transacción y luego falló con `AttributeError: sqlite3.Connection ... serialize` en el computador del operador. No falló la escritura transaccional. **No repetir la importación ni borrar la base para generar el reporte faltante.** PR #35 calcula el hash del archivo fuente antes de escribir y lo identifica como `sqlite_source_sha256`, sin requerir `serialize()`. No se reconstruye retrospectivamente un JSON de éxito inexistente. El ensayo automatizado ahora simula SQLite sin ese método, verifica el hash y rechaza un segundo intento contra destino ocupado.

## Conexión y certificados

Usar la conexión **directa**, sin pooling, seleccionando la base `titulacion`. Este procedimiento aún no valida PgBouncer. La aplicación exige `sslmode=verify-full`, mantiene el resto de opciones de Neon (incluido `channel_binding=require`) y, si no se indica una CA explícita, proporciona el almacén Mozilla de `certifi` a libpq. Así no depende de que exista `~/.postgresql/root.crt` en Windows o Cloud Run. No se desactiva verificación de cadena ni hostname.

Una CA explícita en el DSN se respeta. Conexiones locales y el socket Cloud SQL mantienen su comportamiento. Pruebas con driver simulado verifican selección/archivo CA y preservación de opciones; **no sustituyen una conexión real a Neon**.

Neon no requiere Cloud SQL Client, conector Cloud SQL, Functions, Object Storage ni AI Gateway para nuestro backend. La URL y contraseña se guardan exclusivamente como secreto de backend. No introducirlas en variables VITE, Git, capturas o chat.

## 1. Descargar el estado actual ANTES de cualquier despliegue nuevo

1. Abrir el panel administrativo del frontend e iniciar sesión.
2. En esa misma pestaña del sitio, navegar a `/api/admin/backup`.
3. Guardar `respaldo-privado.zip` y extraerlo en una carpeta privada, fuera de los archivos de entrega. Debe contener `admin.sqlite3` y `files/`.
4. Acordar con el equipo no añadir documentos, editar prompts/configuración ni iniciar simulaciones hasta terminar el corte. La copia es un punto en el tiempo: cambios posteriores no se importarán automáticamente.

El respaldo puede contener datos administrativos; no adjuntarlo al chat ni subirlo al repositorio o portal. Si el endpoint devuelve 401, volver a iniciar sesión y repetir desde la pestaña del sitio. Si falla la descarga, conservar el error y no activar la base vacía.

## 2. Incorporar compatibilidad TLS y preparar el computador

Después de guardar el respaldo, fusionar el ajuste de CA y esperar sus comprobaciones/despliegue. Actualizar el clon limpio e instalar requisitos backend. Los nuevos despliegues SQLite pueden reconstruir la semilla: conservar la copia previa.

```powershell
git switch main
git pull --ff-only
python -m pip install -r backend/requirements.txt
```

No usar un clon previo a la limpieza del historial.

## 3. Importar en Neon vacío

Comprobar privadamente que el valor de `rag-database-url` contiene `sslmode=verify-full`; la cadena por defecto copiada de Neon puede traer `sslmode=require`, que no satisface la política del backend. Mantener los demás parámetros. Si hace falta corregir el secreto, crear una versión nueva y anotar su número, sin mostrar el contenido.

En PowerShell, introducir **esa misma conexión correcta** con entrada oculta y ejecutar la importación. Sustituir la ruta de ejemplo por la carpeta que contiene `admin.sqlite3` y `files/`:

```powershell
$dsnSeguro = Read-Host "Pega la conexión PostgreSQL guardada en Secret Manager (entrada oculta)" -AsSecureString
$env:RAG_DATABASE_URL = [System.Net.NetworkCredential]::new("", $dsnSeguro).Password
try {
    python scripts/migrar_sqlite_postgres.py --source-dir "C:\RUTA_PRIVADA\respaldo-extraido" --report tmp/migracion-neon.json
    if ($LASTEXITCODE -ne 0) { throw "La importación no terminó correctamente; no activar Cloud Run todavía." }
} finally {
    Remove-Item Env:RAG_DATABASE_URL -ErrorAction SilentlyContinue
    $dsnSeguro = $null
}
```

No pegar el URI como una asignación literal en la consola: quedaría en el historial del terminal. El importador no imprime credenciales; el JSON de resultado solo informa conteos/hash y alcance. Rechaza destino ocupado, verifica archivos originales y realiza una transacción completa. Si falla, revisar el error sin compartir el DSN; no vaciar la base ni reemplazar datos para forzar un aprobado.

La primera conexión a Neon puede despertar el cómputo suspendido. Confirmar conectividad y cuotas del panel antes de repetir una operación fallida. No se promete disponibilidad continua o uso ilimitado por ser un plan gratuito.

## 4. Activar el secreto en Cloud Run después de migrar

En servicio `titulacion-rag` → editar e implementar → Variables y Secrets:

| Nombre de variable | Secreto | Versión |
| --- | --- | --- |
| `RAG_DATABASE_URL` | `rag-database-url` | Número real de la versión validada/importada |

Conservar las referencias de Gemini, OpenAI y ADMIN_PASSWORD. No agregar un conector de Cloud SQL para Neon. La cuenta `titulacion-run@agentetitulacion.iam.gserviceaccount.com` requiere Secret Manager Secret Accessor sobre el secreto. Implementar solo después de la importación exitosa.

## 5. Acreditar funcionamiento y persistencia

Registrar nueva revisión, SHA, `/health`, `/ready`, documentos/índice/configuración/prompts y descarga de un original con hash coincidente. Volver a iniciar sesión: sesiones en memoria no se conservan por diseño. Crear un documento sintético si se necesita demostrar una carga posterior; registrar su ID, revisión y cita.

Después de recrear una instancia/revisión de forma controlada, verificar que siguen presentes el documento administrativo, su archivo y el índice, y que responde con fuentes. Guardar un reporte antes/después y repetir los 35 casos públicos ligados al SHA. Repetir la evaluación del alcance que se pretenda acreditar. No marcar s4c cumplido solo por crear el secreto o importar la base.

El plan gratuito tiene cuotas de almacenamiento/cómputo/conexiones que deben revisarse en el panel vigente. Documentos, índices y vectores consumen espacio dentro de PostgreSQL. Cloud Run, Secret Manager y LLM conservan sus propias condiciones de facturación. No se creó ningún recurso Cloud SQL en este procedimiento.


## Verificación remota reproducible, sin volver a migrar

La herramienta no crea revisiones ni cambia documentos/configuración: inicia/cierra su propia sesión y descarga datos para calcular hashes. No consume modelos. Requiere acceso administrativo; contraseña por entrada oculta, nunca como argumento o variable versionada. Los reportes guardan IDs, revisiones y hashes, no texto documental ni cookies. Guardarlos primero en `tmp/` y revisarlos antes de versionar.

1. Actualizar el clon con este PR. En Cloud Run anotar el nombre exacto de la revisión que tiene 100 % del tráfico. Detener ediciones administrativas durante ambas capturas.
2. Capturar desde la URL directa del backend (no depende del proxy frontend):

```powershell
python scripts/verificar_persistencia_remota.py capturar --url https://titulacion-rag-386902880383.us-central1.run.app --revision-cloud-run NOMBRE_REAL_ANTES --output tmp/neon-antes.json
```

3. Crear una revisión nueva con la misma imagen y referencias de secretos. Se puede cambiar una variable inocua `PERSISTENCE_CHECK=neon-01`. No quitar `RAG_DATABASE_URL`. Esperar readiness y 100 % de tráfico. Guardar captura del nombre y tráfico; la etiqueta que recibe el script es una declaración del operador, no una consulta al API de Google.
4. Capturar con el nombre real nuevo, luego comparar:

```powershell
python scripts/verificar_persistencia_remota.py capturar --url https://titulacion-rag-386902880383.us-central1.run.app --revision-cloud-run NOMBRE_REAL_DESPUES --output tmp/neon-despues.json
python scripts/verificar_persistencia_remota.py comparar --antes tmp/neon-antes.json --despues tmp/neon-despues.json --output tmp/neon-comparacion.json
$LASTEXITCODE
```

Exit 0 indica igualdad; 1, diferencias; 2, error o evidencia insuficiente. Si cambia un hash, investigar sin borrar datos ni aprobar el resultado manualmente. La herramienta verifica originales descargados contra SHA registrado, metadatos, historial, prompts, configuración y muestras de hasta 512 fragmentos por documento (límite actual del endpoint). No acredita todos los vectores, recuperación citada ni disponibilidad continua. Completar una consulta citada y los 35 casos HTTP con SHA esperado; conservar reportes y capturas de revisiones en `docs/evidencias/semana-4/` tras revisarlos.

La suite Docker sí prueba el reinicio del servidor PostgreSQL local, nuevas conexiones, archivos/índice/prompts/configuración/vectores/auditoría y rollback. Esa evidencia no se presenta como un reinicio de Neon ni de Cloud Run. Las sesiones, métricas y límites siguen locales al proceso. Indexar un documento no equivale a aprobar OCR o vigencia normativa.


### Terminal Windows que muestra la contraseña

Cancelar con Ctrl+C si se observa eco. El script rechaza el fallback de getpass con eco. Para terminales incompatibles, PowerShell obtiene la contraseña mediante su propio lector seguro y la entrega exclusivamente al entorno temporal del proceso (no como argumento ni literal en el historial):

```powershell
$revisionActual = Read-Host "Revisión Cloud Run con 100% del tráfico"
$claveSegura = Read-Host "Contraseña administrativa" -AsSecureString
try {
    $env:PERSISTENCE_ADMIN_PASSWORD = [System.Net.NetworkCredential]::new("", $claveSegura).Password
    python scripts/verificar_persistencia_remota.py capturar --url https://titulacion-rag-386902880383.us-central1.run.app --revision-cloud-run "$revisionActual" --password-env --output tmp/neon-antes.json
    $resultadoCaptura = $LASTEXITCODE
} finally {
    Remove-Item Env:PERSISTENCE_ADMIN_PASSWORD -ErrorAction SilentlyContinue
    $claveSegura = $null
}
$resultadoCaptura
```

Python elimina la variable de su entorno al leerla; PowerShell la elimina al terminar incluso si falla la ejecución. No se escribe un archivo de contraseña. No usar transcripciones ni capturas que muestren secretos. Repetir con nombre de revisión y salida `tmp/neon-despues.json` para la segunda captura.

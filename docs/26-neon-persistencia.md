# Activación de PostgreSQL en Neon: datos antes de cambiar el servicio

Estado: **preparación para Neon; conexión real, migración y activación pendientes**. El equipo creó una base `titulacion` en PostgreSQL 17 y preparó el secreto `rag-database-url` con permiso de lectura para la cuenta de ejecución. El asistente no conoce su contenido ni verificó directamente la conexión. Cloud SQL continúa diferido por costos; Neon es una alternativa independiente, sujeta a los límites vigentes de su plan.

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

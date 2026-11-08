# Persistencia PostgreSQL / Cloud SQL: preparación sin activar costos

Estado: **opción implementada y validada localmente; activación pospuesta por costos**. El **8 de noviembre de 2026, fecha de Ecuador**, el equipo decidió conservar la preparación técnica y activar PostgreSQL/Cloud SQL oportunamente, cuando exista presupuesto aprobado y necesidad operativa. No hay fecha comprometida ni autorización vigente para crear recursos facturables. Sin `RAG_DATABASE_URL` se conserva SQLite y el despliegue actual. Fusionar este código no crea una instancia ni ejecuta Terraform.

## Decisión vigente para la entrega

Se conserva SQLite con semilla reproducible en producción. La implementación, infraestructura propuesta, migrador y pruebas de PostgreSQL quedan disponibles para una activación futura; no se ejecutará `terraform apply` ni se configurará `RAG_DATABASE_URL` por esta decisión. Los pasos de aprovisionamiento y activación que siguen son una guía futura, no tareas autorizadas para ejecutar ahora.

La persistencia administrativa entre instancias **sigue siendo una limitación conocida**. Las pruebas locales acreditan la preparación técnica; no certifican una base Cloud SQL activa ni cierran s4c en producción. Para retomar: aprobar presupuesto/cotización, revisar plan, respaldar/migrar datos, activar y registrar el ensayo remoto. No se presume que el docente haya dispensado ese requisito: la postergación y su alcance quedan declarados.

## Qué se persiste

Con la variable privada del proceso `RAG_DATABASE_URL`, PostgreSQL guarda registros administrativos, revisiones/auditoría, configuración RAG, prompts, fragmentos, vectores/caché y originales de documentos en `BYTEA`. Los archivos no dependen del disco efímero de Cloud Run. Los prompts editados no se reemplazan por las copias de la imagen al reiniciar. Cada mutación usa transacción y un advisory lock compartido entre procesos. Se conserva el límite de una instancia del servicio; este trabajo no añade un sistema de ejecución distribuida de jobs.

La búsqueda léxica cambia de SQLite FTS5/BM25 a **PostgreSQL FTS en español / ts_rank_cd con índice GIN**; se mantiene cobertura léxica, top-k y fusión RRF con los vectores. No se presenta PostgreSQL como si ejecutara BM25 ni se añade pgvector: el coseno sigue calculándose en Python sobre los vectores JSON guardados. El golden set local de PostgreSQL mantiene 14/16 positivos y 4/4 negativos, sin LLM. Repetir híbrido/generación al activar contra el nuevo backend.

Las sesiones administrativas siguen siendo opacas y en memoria: después de reiniciar se exige iniciar sesión de nuevo. Los datos se conservan; la sesión no. Métricas y límites por proceso conservan su alcance local. Los resultados parciales de análisis se conservan, pero el trabajo en curso puede marcarse interrumpido y requiere repetición; no se promete reanudar ejecuciones de proveedores después de un reinicio.

Si PostgreSQL está configurado pero falla, no se cambia silenciosamente a SQLite: eso produciría dos estados divergentes. Los fallos operativos se responden con 503 controlado sin DSN ni detalle del driver. TCP remoto exige `sslmode=verify-full`; el socket nativo Cloud SQL y el proxy local son las alternativas previstas.

## Evidencia reproducible sin recursos de Google Cloud

```bash
python scripts/probar_postgres.py --with-corpus --report tmp/persistencia-postgres.json
```

Necesita Docker local y requisitos backend. Crea únicamente contenedores de prueba locales y los elimina. Usa contraseña temporal y datos ficticios; no necesita secretos LLM, no acepta un DSN de producción como argumento y no imprime contraseña/cookie. Comprueba dos procesos nuevos con directorios diferentes, descarga de archivo íntegro, índice y citas, prompts/configuración/auditoría/vectores, rollback y reautenticación. También prueba exportar SQLite desde el endpoint administrativo protegido, importarlo en PostgreSQL vacío y rechazar una segunda importación sobre un destino ocupado. Un tercer DB aislado ejecuta ingesta y golden set.

CI agrega un job PostgreSQL aislado y lo exige antes del despliegue. Además, el job de contenedor recrea dos instancias **sin volumen** y comprueba recuperación citada de la semilla; eso no prueba persistencia administrativa en SQLite. [Reportes de preparación](evidencias/semana-4/preparacion-postgres/). Son pruebas locales; **s4c remoto permanece pendiente hasta activar la infraestructura y registrar el ensayo de Cloud Run**.

## Infraestructura propuesta y revisión de costo

El módulo `infra/cloudsql/` propone:

| Concepto | Configuración inicial para cotizar |
| --- | --- |
| Servicio | Cloud SQL PostgreSQL 17, Enterprise |
| Región / disponibilidad | us-central1, zonal, sin alta disponibilidad |
| Instancia | `db-f1-micro` compartida, propuesta económica de demostración; no se presenta como dimensionamiento de producción con SLA |
| Disco | SSD 10 GB, crecimiento automático desactivado; monitorear espacio antes de ampliar |
| Respaldos | Diarios, retención de siete; PITR desactivado en esta propuesta |
| Acceso | Conector Cloud SQL con identidad del servicio; sin redes autorizadas de acceso directo |
| Borrado | Protección en Cloud SQL y `prevent_destroy` de Terraform |
| Credenciales | Usuario/contraseña/secreto creados fuera de Terraform; el módulo no los guarda en tfvars, plan ni estado |

**No hay cotización oficial obtenida ni presupuesto aceptado todavía.** Antes de `apply`, usar [Cloud SQL pricing](https://cloud.google.com/sql/pricing) y la [calculadora de Google Cloud](https://cloud.google.com/products/calculator) con esa región/tier/disco. Registrar moneda, fecha, estimación mensual y máximo aceptado por el equipo. Presupuestar cómputo por horas (aproximadamente 730 h/mes si está encendido), almacenamiento, backups facturables, red y cargos de IP que correspondan. Cloud SQL no escala a cero como Cloud Run; detener cómputo no elimina cargos de almacenamiento/respaldos. Un presupuesto/alerta de Billing no es un tope automático de gasto.

Terraform 1.14.0 y provider Google 7.46.2: `fmt`, `init -backend=false` y `validate` aprobados localmente. **No se ejecutó `plan` autenticado ni `apply`.** Un plan requiere identidad del proyecto y revisión de recursos/IAM; habilita únicamente la API SQL Admin y agrega `roles/cloudsql.client` a la cuenta de ejecución, además de instancia y base. No modifica automáticamente el servicio existente.

Tras aprobar presupuesto y revisar el plan con el equipo:

```powershell
cd infra/cloudsql
Copy-Item terraform.tfvars.example terraform.tfvars
# Revisar proyecto, región, tier y cuenta de servicio.
terraform init
terraform plan -out revision.tfplan
# Solo tras revisar costo y plan concreto:
terraform apply revision.tfplan
cd ../..
```

El estado y el plan son privados. El empaquetador excluye `.terraform`, `.tfstate`, `.tfplan` y `.tfvars` incluso si alguien los versionara por error; conserva ejemplos y el lock del provider.

## Preparación de usuario SQL y secretos

En Cloud SQL crear un usuario de aplicación `rag_app` con contraseña nueva y única desde la consola. No usar `postgres`/superusuario para la aplicación. Con un administrador SQL, conectado a la base `titulacion`, preparar un esquema propio:

```sql
CREATE SCHEMA rag AUTHORIZATION rag_app;
GRANT CONNECT ON DATABASE titulacion TO rag_app;
ALTER ROLE rag_app IN DATABASE titulacion SET search_path = rag;
```

Revisar que `rag_app` no tenga privilegios de administración global ni membresía superusuario heredada; la aplicación solo necesita su esquema y crear/actualizar sus propias tablas/índices. La cuenta de ejecución de Cloud Run necesita Cloud SQL Client y acceso únicamente al secreto correspondiente.

Crear un archivo privado con entrada de contraseña oculta:

```powershell
python scripts/crear_dsn_cloudsql.py --project agentetitulacion --output tmp/cloudsql-dsn.txt
gcloud secrets create rag-database-url --project agentetitulacion --data-file=tmp/cloudsql-dsn.txt
gcloud secrets add-iam-policy-binding rag-database-url --project agentetitulacion --member=serviceAccount:titulacion-run@agentetitulacion.iam.gserviceaccount.com --role=roles/secretmanager.secretAccessor
Remove-Item tmp/cloudsql-dsn.txt
```

Si el secreto ya existe, añadir una versión en lugar de sobrescribir por otro procedimiento. Fijar la versión numérica revisada al desplegar. No pegar DSN, contraseña ni contenido de backups en el chat o Git. En Windows comprobar también los permisos locales del archivo temporal. Los comandos de esta sección son para después de revisar costos/aprovisionar; no se ejecutaron en esta preparación.

## Migrar el estado actual antes de cambiar tráfico

1. Coordinar una ventana sin escrituras y dejar terminar simulaciones en curso. El respaldo es un punto en el tiempo, no una migración en vivo: cambios posteriores al respaldo no se transferirán. Si no se puede detener la actividad, se necesita una estrategia de corte adicional antes de activar; no anunciar cero pérdida sin ello.
2. Con el backend nuevo desplegado aún en SQLite y sesión admin abierta, descargar desde `https://seminario-complexivo-grupo1.vercel.app/api/admin/backup`. El endpoint exige autenticación, responde no-store y exporta solo una copia consistente `admin.sqlite3` y `files/`. No incluye `.env`, sesiones ni credenciales del proceso. Límite web 100 MB; para copias mayores se requiere procedimiento fuera de línea. El backup puede contener datos administrativos privados: nunca subirlo al repositorio o ZIP de entrega.
3. Conservar backup privado fuera de `main`, extraerlo en una carpeta privada y verificar integridad del ZIP. Para migrar desde el computador, instalar [Cloud SQL Auth Proxy desde la guía oficial](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy), autenticarse al proyecto y mantenerlo abierto en otra terminal, por ejemplo `cloud-sql-proxy.exe --port=5433 agentetitulacion:us-central1:titulacion-postgres` en Windows. El proxy necesita una identidad con Cloud SQL Client; configurar credenciales locales con `gcloud auth application-default login` si corresponde. Escuchar solo en localhost, no abrir redes públicas ni desactivar TLS remoto.
4. Generar otro DSN privado para ese proxy y ejecutar importación sobre destino vacío:

```powershell
python scripts/crear_dsn_cloudsql.py --project agentetitulacion --local-proxy-port 5433 --output tmp/cloudsql-dsn-local.txt
$env:RAG_DATABASE_URL = Get-Content tmp/cloudsql-dsn-local.txt -Raw
python scripts/migrar_sqlite_postgres.py --source-dir RUTA_PRIVADA_DEL_RESPALDO_EXTRAIDO --report tmp/migracion-postgres.json
$LASTEXITCODE
Remove-Item Env:RAG_DATABASE_URL
Remove-Item tmp/cloudsql-dsn-local.txt
```

El importador verifica hashes de originales, preserva IDs/revisiones/fragmentos/vectores/prompts/auditoría, reconstruye FTS, importa archivos históricos y confirma todo en una transacción. Rechaza un destino ocupado o editado. No borra ni modifica el origen. El archivo de reporte no contiene DSN ni contenido de documentos. Una activación con DB vacía sin migración dejará `/ready` en 503: no cambiar tráfico hasta preparar datos y validar.

Si el equipo confirma que no hay cambios administrativos que conservar, la alternativa es sembrar un DB nuevo con `scripts/ingest.py --strategy lexical` mediante una ejecución con el mismo contenedor y secreto Cloud SQL. No se debe escoger esa alternativa por defecto ni usarla para borrar/omitir el estado existente. El Dockerfile sigue sembrando SQLite en build sin claves; no abre PostgreSQL durante la construcción.

## Activar, verificar y probar reinicio remoto

Solo después de datos preparados, backup privado conservado y costo aprobado:

```powershell
$conexion = "agentetitulacion:us-central1:titulacion-postgres"
gcloud run services update titulacion-rag --project agentetitulacion --region us-central1 --add-cloudsql-instances=$conexion --update-secrets=RAG_DATABASE_URL=rag-database-url:1
```

Usar la versión real del secreto si no es 1. `--update-secrets` conserva los demás secretos; no sustituirlos por una lista incompleta. El pipeline conserva configuración/secretos del servicio al cambiar imagen. Revisar revisión lista y tráfico antes de retomar escrituras.

Registrar estado y prueba **antes y después** de una nueva revisión/instancia: `/health` (SHA), `/ready`, fuente base y documento administrativo sintético con sus IDs, bytes/hash, índice y respuesta citada. Probar prompt/configuración y volver a iniciar sesión; se espera invalidación de la sesión anterior. Una nueva revisión puede crear otra instancia, pero no demuestra reinicio del servidor Cloud SQL: registrar qué se hizo realmente. Repetir los 35 casos públicos y la evaluación comparable del backend que se pretenda acreditar.

Un rollback debe considerar los datos escritos tras el corte: quitar `RAG_DATABASE_URL` volvería a una semilla SQLite, no a esos cambios. No anunciar ese comando como rollback sin pérdida. Conservar backups y definir recuperación en PostgreSQL antes de habilitar datos importantes. Sesiones, métricas y trabajos en curso mantienen los límites descritos arriba.

# Cierre de pruebas de persistencia: PostgreSQL local y evidencia remota

## Resultado automatizado

Ejecutado el 8 de noviembre de 2026 en una base Docker PostgreSQL 17 aislada, sin credenciales de producción ni consumo de modelos. [JSON completo, XML y resumen](evidencias/semana-4/persistencia-neon/). El SHA base y el árbol modificado están declarados; el reporte incluye hash del script ensayado. No se atribuye la ejecución a un futuro commit de merge.

| Comprobación | Resultado / alcance |
| --- | --- |
| Proceso nuevo sin archivos locales compartidos | Conserva documento, original descargado con hash correcto y recuperación con sección citada |
| Reinicio del servidor PostgreSQL local y otro proceso nuevo | Conserva documento, original, índice, prompt editado, configuración, vectores/caché y auditoría |
| Sesiones | Cookie del proceso anterior rechazada; nuevo login aprobado, comportamiento esperado |
| Atomicidad | Escritura con excepción revertida; no queda registro de prueba |
| Backup SQLite por HTTP protegido e importación | Datos y archivos conservados; hash del origen verificado |
| SQLite sin serialize | Importación y generación de reporte aprobadas sin depender del método |
| Segundo intento de migración | Destino ocupado rechazado sin sobreescritura |
| Golden set en PostgreSQL con corpus completo | 14/16 positivas, 4/4 negativas, cero errores; no generación LLM |
| Suite backend | 139 aprobadas, cobertura app 89,11 % |
| Comparador de capturas remotas | Siete casos verifican igualdad y rechazo de cambios/evidencia insuficiente |

El reinicio de Docker puede cambiar su puerto efímero; el ensayo consulta el puerto reasignado antes de reconectar. La imagen y las bases de prueba son locales y se eliminan al terminar. No se reinició Neon ni se cambió el tráfico de Cloud Run desde este entorno.

## Reproducir

Con Docker local y requisitos backend instalados, desde la raíz:

```bash
python scripts/probar_postgres.py --with-corpus --report tmp/persistencia-postgres.json
python -m pytest -q backend/tests --cov=app --cov-fail-under=85
```

El script Docker usa el socket Linux `/var/run/docker.sock`; ejecutar en Linux, CI o WSL con Docker disponible. La herramienta remota siguiente funciona también desde PowerShell/Windows.

## Pendiente concreto de producción

El operador compartió conteos de Neon (6 documentos, 3 prompts, 1 configuración, 1.047 fragmentos y entradas de búsqueda, 6 archivos, 12 eventos) y reportó activación/reindexación; el panel muestra el instructivo revisión 2. Las capturas no se adjuntaron como archivos al repositorio y no prueban un reinicio posterior.

Falta ejecutar `scripts/verificar_persistencia_remota.py` antes/después de una nueva revisión Cloud Run con 100 % de tráfico, sin modificaciones administrativas entre capturas. [Comandos, límites y evidencia requerida](26-neon-persistencia.md). La herramienta compara originales/metadatos/historial, prompts/configuración y muestras de fragmentos; no consulta Google para verificar los nombres de revisión declarados por el operador. Adjuntar capturas de revisiones/tráfico y una consulta citada; ejecutar el smoke de 35 casos con SHA esperado. No versionar DSN, cookies, contraseñas ni el backup privado.

Mientras falte esa evidencia, s4c permanece **parcial**. Tampoco se acreditan con estas pruebas un plan de recuperación de Neon, restauración de backups administrados, disponibilidad continua, persistencia de métricas/sesiones ni aprobación humana del OCR. No hay recursos Cloud SQL creados.

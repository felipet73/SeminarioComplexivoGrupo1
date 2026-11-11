# Limpieza histórica publicada y verificación de main

El **8 de noviembre de 2026 (Ecuador)**, después de respaldo confirmado y autorización explícita del equipo, se publicaron **27 ramas reescritas** con un push atómico y leases por referencia. Se conservaron las 28 ramas existentes y no había tags. No se ejecutó un push mirror indiscriminado ni se intentó modificar refs internas de PR. [Resultado y mapa de ramas/commits](evidencias/semana-4/limpieza-publicada/).

Main anterior: `319dc6cfc292d2d3b4014ba518a47724622b7856`. Main publicado y probado: **`2482401e50b607296151b5a7ac47738536c0b2d5`**. El código actual de aplicación quedó idéntico: cambiaron `.gitleaksignore` (cinco fingerprints del advisory/reportes ya justificados, sin excluir las credenciales legacy) y CI (control histórico para detectar reintroducción del módulo).

## Verificación acreditada

- Un clon nuevo desde GitHub pasó `scripts/check_secrets.py` y `--historial-legacy`, ambos con exit 0. El módulo retirado no aparece en la historia de las ramas descargadas normalmente.
- La copia filtrada pasó Gitleaks con redacción completa, exit 0 y cero hallazgos. No se presenta como garantía universal de ausencia de secretos.
- [Actions 42453615683](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42453615683) terminó **success** sobre `2482401`: secretos/control histórico, backend, frontend, navegador, contenedor, PostgreSQL aislado y despliegue aprobados. El job opcional de evaluación real quedó omitido; su evaluación independiente previa 6/6 mantiene su alcance histórico.
- El deploy volvió a comprobar SHA, corpus, rutas retiradas/chat y contratos públicos. El artefacto completo HTTP de esa ejecución debe conservarse con su propio SHA si se descarga; no se reetiquetan JSON anteriores para aparentar que probaron este commit. Las pruebas públicas siguen siendo un conjunto diferente de las 20+6 preguntas del workflow de evaluación.
- ZIP del clon limpio en ese corte: **19.040.024 bytes**, debajo de 20.000.000. Regenerar después de incorporar esta constancia, desde el main final, con el empaquetador.

El proveedor Cloud SQL no fue creado ni activado. La decisión de posponerlo por costos sigue vigente. La reescritura no rota secretos de ejecución ni demuestra retirada de todas las revisiones/URLs antiguas.

## Pendiente de GitHub: PR y cachés

Se detectaron **25 referencias de PR afectadas** en el espejo (de 26 referencias adicionales existentes). No son referencias que podamos actualizar con el push de ramas. La API todavía permite consultar al menos el commit histórico comprobado `3e38895`; no se consultaron ni imprimieron sus valores.

Por eso no se certifica «eliminación completa de GitHub» ni riesgo cero. [Solicitud a soporte](25-solicitud-soporte-github.md) **enviada por el propietario, caso #4985701, abierto y pendiente de respuesta/actuación** según capturas aportadas posteriormente. Su resultado depende de GitHub; la existencia del ticket no acredita purga. Cerrar PR o borrar comentarios no elimina estas referencias. Forks y clones externos también están fuera de este saneamiento.

## Instrucciones para cada integrante

1. Conservar el respaldo privado y cualquier trabajo local no publicado. No subir el bundle al portal ni a Git: contiene el historial sensible original.
2. Usar un clon nuevo para continuar. No hacer un merge de la historia anterior ni subir nuevamente el repositorio antiguo completo. Los archivos de trabajo pendientes pueden trasladarse selectivamente, después de revisión, sin copiar `.git`.
3. Los secretos locales necesarios pueden copiarse de forma privada al `.env` del clon nuevo; no versionarlos. Reinstalar dependencias y seguir el README para ejecutar localmente.
4. Si una operación intenta reintroducir la historia anterior, el nuevo control de CI lo detectará; no desactivarlo para hacer pasar la entrega.

Ejemplo desde la carpeta superior del clon antiguo en PowerShell, eligiendo un nombre que no exista:

```powershell
git clone https://github.com/felipet73/SeminarioComplexivoGrupo1.git titulacion-rag-limpio
cd titulacion-rag-limpio
git rev-parse HEAD
python scripts/check_secrets.py --historial-legacy
```

Los reportes antiguos conservan sus SHA originales y fechas. El mapa versionado permite relacionarlos con commits filtrados; **no demuestra que una ejecución antigua probara el SHA nuevo**. Algunos enlaces a objetos antiguos pueden dejar de resolver después del tratamiento por soporte, lo cual es esperable.

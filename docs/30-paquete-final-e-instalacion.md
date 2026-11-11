# Paquete final automático y comprobación de instalación

## Problema resuelto

Versionar el JSON del último despliegue en un commit nuevo cambia el SHA y genera otra ejecución. Para entregar código y evidencia del mismo SHA sin esa repetición, el job `desplegar` genera ahora el ZIP **después** de que pasen las pruebas públicas. Incorpora explícitamente el JSON generado en ese job, aunque no esté rastreado en Git. No se agrega ningún otro archivo no versionado.

El empaquetador exige checkout sin cambios rastreados, SHA del reporte igual a HEAD, 35 casos completos aprobados, IDs exactos del catálogo, cero omitidos, modelo incluido, frontend incluido y revisión obtenida coincidente. Rechaza evidencia anterior, resumen sin casos, duplicados/casos ajenos, fallos y fuente modificada. El JSON se guarda dentro del paquete como `docs/evidencias/semana-4/produccion-despliegue-SHA.json`. El informe externo incluye SHA, hash del ZIP y hash/ruta del reporte. Las exclusiones privadas y el máximo de 20.000.000 bytes se mantienen.

Esto no afirma que el nuevo JSON esté versionado como commit: se entrega como evidencia del mismo despliegue dentro del ZIP y como artefacto de Actions. El reporte completo histórico de ab21d85 sí está versionado. No se crea un commit automático ni se modifica main desde el workflow.

## Descargar el entregable después del merge y CI aprobado

1. Abrir la ejecución de **Pruebas Grupo 1** correspondiente al SHA final de main; comprobar despliegue, verificación de referencia Neon, casos públicos y generación del paquete aprobados.
2. En Summary → Artifacts descargar **`entrega-final-SHA`**. GitHub entrega un ZIP contenedor del artefacto: extraerlo.
3. Dentro están **`Titulacion_Grupo1_SHA.zip`** y **`paquete-final.json`**. El primero es el único archivo para el portal; no subir el contenedor del artefacto ni el JSON separado.
4. Revisar en el informe `commit`, `working_tree_con_cambios=false`, `cumple_limite=true`, `zip_creado=true`, `evidencia_produccion.revision` y `zip_sha256`. Comparar el hash con `Get-FileHash` local. El ZIP debe pesar ≤20.000.000 bytes.
5. Abrir el ZIP sin modificarlo y confirmar que incluye el JSON público del mismo SHA. Subir ese único ZIP con el código real del grupo y conservar el acuse del portal. Este paso sigue siendo responsabilidad del equipo, no se marca completado por generar el archivo.

Si no aparece el artefacto, revisar el paso fallido: no reutilizar un ZIP anterior como si fuera del SHA final. La generación se omite si falla el smoke o algún caso público. No borrar ni desactivar seguridad para forzar una ejecución verde.

### Alternativa local explícita

Desde el clon limpio del SHA desplegado, con su JSON descargado fuera de los archivos rastreados:

```powershell
$sha = git rev-parse HEAD
python scripts/empaquetar_entrega.py --evidencia-produccion tmp/results-produccion-funcional.json --expected-revision "$sha" --output "tmp/Titulacion_Grupo1_$sha.zip" --report tmp/paquete-final.json
if ($LASTEXITCODE -ne 0) { throw "No entregar: revisar el reporte o el límite." }
```

## Instalación limpia automatizada realizada

Se clonó main `8d353473256a3d35580d78d9c3edf868b5d9802c` en un directorio nuevo, se creó venv y cachés pip/npm nuevos, se instalaron requisitos de desarrollo y frontend, se hizo ingesta léxica, se arrancaron ambos servicios y se verificaron readiness/página y smoke de SHA, corpus, SSE de rechazo y métricas.

Resultado: **aprobado, 51,633 segundos**. Linux administrado, Python 3.12.14, Node 24.22.1 y npm 11.9.0 ya instalados. No incluye preparar esos prerrequisitos, generar respuestas con LLM, credenciales, servicios externos, navegador interactivo ni tiempo humano leyendo instrucciones. No acredita disponibilidad 24 h ni instalación en cualquier red/equipo. [Reporte completo](evidencias/semana-4/paquete-final-automatizado/instalacion-limpia-automatizada.json).

Es una medición automatizada real, **no** un ensayo por un integrante nuevo. Si el criterio docente exige esa persona, sigue pendiente hasta recibir nombre, sistema, duración real, resultado y alcance. No se cambia el checkbox humano a partir de estos 51,633 segundos.

## Validación técnica del empaquetado

Se probó el nuevo empaquetador contra un checkout limpio real ab21d85 y su JSON real 35/35: ZIP de **19.098.586 bytes**, sin cambios rastreados y evidencia completa dentro. Es una prueba de integración del empaquetador, no una nueva corrida HTTP ni el entregable del futuro merge. [Informe](evidencias/semana-4/paquete-final-automatizado/integracion-zip-con-evidencia.json).

La suite agrega casos para evidencia válida, resumen incompleto, fallo, omitidos, IDs incorrectos, otro SHA y árbol modificado. El conteo completo vigente se registra en docs/21 y el XML adjunto; no se cambia ningún resultado histórico.

## Pendientes que una automatización no puede declarar realizados

- Respuesta de GitHub Support al caso #4985701 y verificación de retirada de referencias/cachés.
- Revisión OCR/vigencia: **\* Debe analizarse el improvement**, no se marca aprobación integral.
- Fecha/acta de sustentación, ensayo humano y capturas originales cuando los exija el docente: solo el equipo puede aportar esos hechos.
- Subida al portal y acuse, antes del plazo comunicado: miércoles 11 de noviembre, 23:59 Ecuador.

La captura puntual de artículo 24/página 9 y el ensayo Neon antes/después sí están documentados con sus límites. No se requieren cambios funcionales nuevos para repetirlos; no se reimporta ni se borra la base.

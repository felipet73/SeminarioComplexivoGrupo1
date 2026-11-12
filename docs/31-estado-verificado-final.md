# Estado de entrega verificado: qué está probado y dónde está la evidencia

## LISTO PARA SUBIDA — corte 2e0bf2d

Main `2e0bf2d68b7ecf8a4557da3890bd235990010a86`, merge del PR #42, aprobó [Actions 42939713143](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42939713143). Creación de ejecución: 2026-11-11 01:32:39 UTC; actualización final: 01:35:32 UTC. [Metadatos reales versionados](evidencias/semana-4/main-2e0bf2d/actions-verificado.json) y [estado de subida de ese SHA](evidencias/semana-4/main-2e0bf2d/listo-para-subida.json).

Pasaron los seis controles previos, el job backend/pytest sobre ese checkout, despliegue, referencia Neon, smoke de revisión/corpus/rutas/chat, casos funcionales públicos, **Generar ZIP final con evidencia pública del mismo SHA** y publicación del artefacto final. No es cierto que el paso de empaquetado solo se haya ejecutado localmente: los pasos y conclusiones de esta ejecución están en el JSON de API.

«Listo para subida» es una condición previa al portal. No significa «ya entregado», que se hayan purgado copias antiguas de GitHub ni que se haya aprobado toda fuente normativa. Tampoco certifica un merge posterior: cada SHA posterior tendrá su ejecución/artefacto propios.

## Evidencias y diferencia entre Git y artefactos

| Afirmación | Evidencia disponible y límite |
| --- | --- |
| CI/despliegue/empaquetado de 2e0bf2d aprobados | GitHub API: run/jobs/steps y artefactos; metadatos versionados sin depender del resumen de 8d35347. |
| JSON 35/35 dentro del entregable de 2e0bf2d | El paso del empaquetador terminó en success. Su contrato exige 35 casos completos aprobados, IDs exactos, cero omitidos, SHA esperado/obtenido coincidente y checkout sin cambios rastreados. El JSON de ese job se incorpora al ZIP. El propietario aportó el [JSON original de 35 casos](evidencias/semana-4/produccion-despliegue-2e0bf2d68b7ecf8a4557da3890bd235990010a86.json), ahora versionado y validado: 35/35, sin omitidos, IDs de catálogo y revisión obtenida coincidentes. Su hash coincide con el informe del paquete. El ZIP binario no se descargó aquí. |
| ZIP final generado | Artefacto **entrega-final-2e0bf2d68b7ecf8a4557da3890bd235990010a86**, ID **13820491498**. [Descarga](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42939713143/artifacts/13820491498). No es una medición local ab21d85 renombrada. |
| Límite 20 MB | Paso de empaquetado aprobado: exit 0 exige ≤20.000.000 bytes. El tamaño de API del artefacto, **19.069.602 bytes**, es el contenedor comprimido de GitHub, **no** la cifra exacta del ZIP interior. El [paquete-final.json original](evidencias/semana-4/main-2e0bf2d/paquete-final.json), recibido después del propietario, indica **19.129.820 bytes** para el ZIP interior, `cumple_limite=true`, `working_tree_con_cambios=false` y SHA correcto. El hash del ZIP es el reportado por CI; no se recalculó aquí sin su binario. |
| 154 tests y árbol local modificado | El XML local de desarrollo declara correctamente su base y cambios. Además, el job backend/pytest de 2e0bf2d terminó aprobado sobre el checkout de Actions; ya no es evidencia exclusiva de un árbol local. El XML de CI está en el artefacto `evaluacion-rag`, ID 13820266012. La cifra 154 publicada corresponde al XML local versionado; no se inventa una lectura del XML remoto. |
| JSON completo versionado en Git | El de **2e0bf2d** y su `paquete-final.json` ya están versionados a partir de los originales aportados por el propietario. Ab21d85, Actions 42494812366, y reportes anteriores conservan su fecha/SHA históricos. |
| Instalación humana | Los tres integrantes reinstalaron desde copias limpias; el equipo estima aprox. seis minutos, sin cronómetro. [Constancia](evidencias/semana-4/instalacion-equipo.md). No se afirma una persona ajena ni tres tiempos exactos medidos. |
| Instalación automatizada | Prueba independiente sobre 8d35347: 51,633 s, con prerrequisitos instalados y sin proveedores. No se le atribuye al tiempo humano ni a 2e0bf2d. |

Se recibieron los dos JSON originales del artefacto mediante el propietario y se conservaron byte a byte. Se validó SHA del checkout/reporte, 35 casos, IDs, resultados, árbol limpio, límite y hash del reporte coincidente con el informe. [Validación y hashes de ambos archivos](evidencias/semana-4/main-2e0bf2d/validacion-primarios.json). El ZIP binario no se recibió; no se afirma haber recalculado su hash. La limitación de descarga directa de Actions no implica ya ausencia de estos JSON en el repositorio.

## Qué debe subir el propietario

1. Descargar el artefacto final y extraer el contenedor de Actions.
2. Verificar `paquete-final.json`: `cumple_limite=true`, `working_tree_con_cambios=false`, `evidencia_produccion.revision=2e0bf2d68b7ecf8a4557da3890bd235990010a86`. Comparar `zip_sha256` con `Get-FileHash`.
3. Tomar **solo** `Titulacion_Grupo1_2e0bf2d68b7ecf8a4557da3890bd235990010a86.zip`, renombrarlo con el nombre exacto exigido por el docente, conservando `.zip`, y subir ese único archivo. No subir `paquete-final.json` por separado, el contenedor de Actions ni la imagen de backend.
4. Los JSON de evidencia dentro del proyecto se mantienen. Cambiar el nombre externo del ZIP no cambia sus bytes/hash. No reconstruirlo desde otra revisión mientras se usa el reporte de 2e0bf2d.

Si se fusiona esta actualización documental, usar el nuevo artefacto de esa ejecución aprobada; no adjudicarle a la revisión nueva el reporte del corte anterior. El empaquetador incluye automáticamente su propia prueba pública, sin un nuevo commit para copiarla.

## Pendientes reales y alcance

- **Support #4985701:** enviado por el propietario. Correo de confirmación observado: **10/11/2026 19:42**, zona no visible; confirma recepción, no actuación técnica. Siguen publicadas las 25 refs consultadas y el commit histórico responde. [Seguimiento](evidencias/semana-4/main-2e0bf2d/seguimiento-support.json). No se declara JWT rotado: se retiró el mecanismo. Forks/clones externos quedan fuera del saneamiento.
- **PDF/OCR:** el cliente debe entregar PDF legible con texto fiel. El código valida integridad técnica, no fidelidad integral/vigencia. El instructivo está sin aprobar en la política semilla de Git y aprobado en el panel según el operador; la configuración administrativa es mutable y no se sincroniza desde Git. Esto no acredita revisión integral de la fuente. No se cambia approved para aparentar concordancia. OCR/revisión asistida sigue fuera del alcance del producto: **\* Debe analizarse el improvement**.
- **Artículo 24:** corrección local probada y uso remoto corregido confirmado por el operador (87 fragmentos, fuente artículo 24/página 9/revisión 2). No sigue como corrección funcional pendiente. La captura original/JSON de esa respuesta no está versionada; el relato no se presenta como un archivo inexistente.
- **Evaluación híbrida:** 16/16 pertenece a OpenAI text-embedding-3-small/0,55; no es una medición de Gemini/0,65 o del estado actual del panel. No se requiere repetirla solo para aclarar su alcance; sí antes de certificar otra configuración con esa cifra.
- **Sesiones, métricas y rate limit:** siguen por proceso. Persistencia Neon de documentos/índice/configuración no implica durabilidad/distribución de esos datos.
- **Sustentación y primarios visuales:** observaciones y uso de la presentación están declarados por el equipo. No se fabrican acta, fecha exacta, vídeo ni capturas originales que no se aportaron como archivo; conservarlos si se exigen.

Los pendientes externos, la calidad del insumo y las mejoras fuera de alcance no se convierten en funcionalidades cumplidas. El estado «listo para subida» se refiere al código y paquete de la ejecución acreditada, con estas limitaciones declaradas.

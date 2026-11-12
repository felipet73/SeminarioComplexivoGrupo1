# Estado de entrega verificado: qué está probado y dónde está la evidencia

## LISTO PARA SUBIDA — corte 2e0bf2d

Main `2e0bf2d68b7ecf8a4557da3890bd235990010a86`, merge del PR #42, aprobó [Actions 42939713143](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42939713143). Creación de ejecución: 2026-11-11 01:32:39 UTC; actualización final: 01:35:32 UTC. [Metadatos reales versionados](evidencias/semana-4/main-2e0bf2d/actions-verificado.json) y [estado de subida de ese SHA](evidencias/semana-4/main-2e0bf2d/listo-para-subida.json).

Pasaron los seis controles previos, el job backend/pytest sobre ese checkout, despliegue, referencia Neon, smoke de revisión/corpus/rutas/chat, casos funcionales públicos, **Generar ZIP final con evidencia pública del mismo SHA** y publicación del artefacto final. No es cierto que el paso de empaquetado solo se haya ejecutado localmente: los pasos y conclusiones de esta ejecución están en el JSON de API.

«Listo para subida» es una condición previa al portal. No significa «ya entregado», que se hayan purgado copias antiguas de GitHub ni que se haya aprobado toda fuente normativa. Tampoco certifica un merge posterior: cada SHA posterior tendrá su ejecución/artefacto propios.

## Evidencias y diferencia entre Git y artefactos

| Afirmación | Evidencia disponible y límite |
| --- | --- |
| CI/despliegue/empaquetado de 2e0bf2d aprobados | GitHub API: run/jobs/steps y artefactos; metadatos versionados sin depender del resumen de 8d35347. |
| JSON 35/35 dentro del entregable de 2e0bf2d | El paso del empaquetador terminó en success. Su contrato exige 35 casos completos aprobados, IDs exactos, cero omitidos, SHA esperado/obtenido coincidente y checkout sin cambios rastreados. El JSON de ese job se incorpora al ZIP. El binario y el JSON original de ese corte **no se descargaron en este entorno**: permanecen en Actions, no se reconstruyen como archivos supuestamente descargados. |
| ZIP final generado | Artefacto **entrega-final-2e0bf2d68b7ecf8a4557da3890bd235990010a86**, ID **13820491498**. [Descarga](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42939713143/artifacts/13820491498). No es una medición local ab21d85 renombrada. |
| Límite 20 MB | Paso de empaquetado aprobado: exit 0 exige ≤20.000.000 bytes. El tamaño de API del artefacto, **19.069.602 bytes**, es el contenedor comprimido de GitHub, **no** la cifra exacta del ZIP interior. Consultar `paquete-final.json` para bytes/hash interiores. No se asigna un hash de contenedor al ZIP del proyecto. |
| 154 tests y árbol local modificado | El XML local de desarrollo declara correctamente su base y cambios. Además, el job backend/pytest de 2e0bf2d terminó aprobado sobre el checkout de Actions; ya no es evidencia exclusiva de un árbol local. El XML de CI está en el artefacto `evaluacion-rag`, ID 13820266012. La cifra 154 publicada corresponde al XML local versionado; no se inventa una lectura del XML remoto. |
| JSON completo versionado en Git | El de ab21d85, Actions 42494812366, conserva su fecha/SHA. Los reportes 279580e y anteriores también son históricos. No equivalen a pruebas de 2e0bf2d. |
| Instalación humana | Los tres integrantes reinstalaron desde copias limpias; el equipo estima aprox. seis minutos, sin cronómetro. [Constancia](evidencias/semana-4/instalacion-equipo.md). No se afirma una persona ajena ni tres tiempos exactos medidos. |
| Instalación automatizada | Prueba independiente sobre 8d35347: 51,633 s, con prerrequisitos instalados y sin proveedores. No se le atribuye al tiempo humano ni a 2e0bf2d. |

Los metadatos de API no sustituyen una lectura de los archivos internos. La descarga desde almacenamiento Actions devuelve Forbidden aquí; es una limitación de acceso del entorno, no prueba de que falte el artefacto. Para versionar los primarios de 2e0bf2d, el propietario puede aportar `paquete-final.json` y el JSON de 35 casos extraído del ZIP, sin adjuntar el ZIP completo ni añadir vídeos pesados. Hasta entonces no figuran como descargados/versionados en este checkout.

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

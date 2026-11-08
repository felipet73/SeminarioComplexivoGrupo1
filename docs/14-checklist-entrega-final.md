# Estado de entrega final y sustentación — Grupo 1

Corte vigente: 8 de noviembre de 2026 UTC. Evaluación final sin despliegue aprobada en [Actions 42443602234](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42443602234), SHA `16081c8224ba07d1b0b917f89266f6bb562fb0e5`: recuperación/chat y agente estricto 6/6. Los cortes anteriores conservan su alcance histórico. Esta ejecución aislada no acredita un despliegue HTTP nuevo.

Se contrastaron los documentos del docente **Sustentacion_sabado_7_paso_a_paso.pdf** y **Entrega_final_proyecto_comite_evaluacion (1).pdf**, aportados por el equipo. Sus hashes constan en la [auditoría](evidencias/semana-4/auditoria-secretos-y-comite-2026-11-07.json). Se usan como requisitos de entrega, no como prueba de que el grupo ya los cumplió.

## Lista s4a–s4k: marcar solo lo acreditado

| Punto | Estado actual | Evidencia / acción de cierre |
| --- | --- | --- |
| s4a — URL pública en README y health | **Cumplido en la revisión probada** | URLs reales, smoke de SHA y 35 casos públicos aprobados; mostrar navegador privado durante la demo. |
| s4b — Credenciales solo en plataforma, incluido historial limpio | **Ramas saneadas; PR/cachés y alcance externo parcial** | Contraseña actual rotada, versión 1 inhabilitada y mecanismo JWT retirado. Reescritura coordinada de 27 ramas publicada; clon nuevo y CI/despliegue `2482401` aprobados. Cinco fingerprints de falsos positivos adaptados, sin exclusiones para credenciales legacy. [Constancia](24-cierre-historial-publicado.md). Restan 25 refs de PR afectadas/cachés, revisión de otras copias/revisiones accesibles y detalle nominal/fecha exacta de rotación si se exige. No se declara purga completa del servidor. |
| s4c — Índice persistente tras reinicio | **Parcial: Neon activado por el equipo; ensayo remoto pendiente** | Importación observada: 6 documentos, 1.047 fragmentos y 6 archivos; operador reportó activación/reindexación. Suite PostgreSQL ampliada prueba procesos nuevos, reinicio del servidor local y migración sin serialize. Falta comparación remota entre revisiones con consulta citada. Cloud SQL continúa diferido por costos. [Estado y comandos](26-neon-persistencia.md). |
| s4d — 15+ casos públicos, incluida inyección | **Cumplido en ejecución; completar material visual** | 35/35 con fecha, SHA y tres consultas generativas, más inyección y rutas retiradas. Guardar el JSON por caso del intento 2 y su p95; no reutilizar el p95 del intento fallido. La red del chat bloquea descargar el artefacto, no se inventa su contenido. |
| s4e — Evaluación final repetida frente a semana 3 | **Cumplido en el alcance automatizado** | Mismo golden set de 20 preguntas y seis casos del agente; léxico 14/16, híbrido/citas 16/16, negativas 4/4 y agente estricto 6/6, sin fallback. [Comparación y límites](07-evaluacion.md), Actions 42443602234, SHA `16081c8`; JSON completos versionados. No acredita exhaustividad semántica ni aprobación del OCR. |
| s4f — Tasa y errores seguros | **Cumplido en alcance implementado** | 30 consultas/60 s/proceso, alias compartidos, 429/Retry-After, timeout, respaldo y errores categorizados sin excepción cruda; tests estrictos. No es cuota distribuida ni por usuario. |
| s4g — Aviso de IA y minimización de datos | **Cumplido en alcance educativo básico** | Interfaz identifica IA, orientación no oficial, pide verificar fuentes y prohíbe compartir contraseñas/datos sensibles. Contexto opcional acotado, métricas sin texto libre. El texto de consulta/contexto sí se envía al proveedor seleccionado; ver [tratamiento de datos](16-datos-y-limites.md). |
| s4h — README y decisiones; instalación en diez minutos | **Documentación preparada; ensayo humano pendiente** | README, requisitos, ADR y comandos corresponden al código. Registrar instalación por un integrante nuevo, duración real, ambiente y health. No hay un tiempo de diez minutos medido por otra persona. |
| s4i — IA y aportes por integrante | **Aportes y herramientas confirmados; detalle de revisión de IA parcial** | README detalla tareas de Christian (despliegues/CI/optimización), Olmes (pruebas manuales/backend semana 4) y Widman (tests/documentación backend, QA frontend y fuentes). Declaración de IA incluye Gemini, ChatGPT y Codex. Ejecución local, PR y verificación de pruebas confirmadas por todos. Faltan ejemplos de salida de IA revisada por cada persona y enlaces de PR nominados si se exige ese detalle. |
| s4j — PDF de la presentación de doce minutos | **Archivo preparado** | `docs/presentacion-entrega4.pdf` actualizado y PDF técnico de apoyo. Falta ensayo cronometrado y confirmar que esta es la versión realmente usada. El informe técnico extenso no sustituye la exposición de 12 minutos. |
| s4k — Evidencias y observaciones de sustentación | **Observación aclarada y registrada; material de respaldo parcial** | [SUST-01](evidencias/semana-4/observaciones-sustentacion.md): faltó una pregunta de demo que activara solicitud de datos adicionales, no hubo un fallo del sistema. El equipo confirma verificación posterior y existen tests específicos del contrato de aclaración. No se inventa una reparación ni se atribuyen los 429 de evaluación a la demo. Fecha exacta de sesión y vídeo de respaldo pendientes de aportar. |

## Qué ya está cerrado de la ficha antigua

- [x] Módulo legacy eliminado de HEAD y rutas antiguas retiradas en la URL probada.
- [x] Despliegue con SHA verificable y pipeline dependiente de seis controles previos.
- [x] 35 casos públicos, incluida generación real directa y por proxy SSE; se resolvieron los tres 503 anteriores.
- [x] Tests estrictos restaurados y aislados de claves reales: **139 backend, cobertura de app 89,11 %**, en rama de pruebas de persistencia; [XML y resumen](evidencias/semana-4/persistencia-neon/). Los cortes de 130 y anteriores se conservan fechados en [el registro de conteos](21-conteos-de-pruebas.md). Frontend/navegador mantienen sus evidencias separadas.
- [x] Límite de consultas compartido, errores seguros y documentación técnica de endpoints/secuencias.
- [x] Falsos positivos de las seis exclusiones de Gitleaks identificados y separados de credenciales legacy.
- [x] Ramas saneadas con respaldo y publicación coordinada; clon nuevo y controles histórico/activo aprobados.
- [ ] Eliminación completa del servidor: referencias antiguas de PR/cachés y copias externas pendientes; no se satisface solo con reescribir ramas.
- [x] Evaluación final comparable y seis listas citadas: Actions 42443602234, agente estricto 6/6.
- [ ] Aprobación humana del instructivo y de su OCR; no se deduce del 6/6.
- [ ] Persistencia de cambios, declaración individual, ensayo y observaciones del tribunal.

## Acciones concretas y orden recomendado

1. **Evidencia de producción:** descargar desde Actions el artefacto `evidencias-despliegue-0dab82dd9258e9794684ea806b055d61a04d5bb5` del intento 2; conservar JSON por caso, p95, SHA, fecha y capturas. Comprobar que pertenece al segundo intento, no al archivo anterior 32/35.
2. **Credenciales:** identificar si el valor legacy se reutilizó sin divulgarlo; cambiarlo en cualquier uso vigente, retirar revisiones antiguas accesibles y registrar la actuación. Coordinar la limpieza de historia con el equipo; no hacer force push sin respaldo e inventario de referencias. Las exclusiones de `.gitleaksignore` no son la solución a este punto.
3. **Evaluación comparable cerrada:** conservar los JSON completos y la comparación con semana 3 de [Actions 42443602234](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42443602234). No repetir por falta de evidencia: ya está versionada en este corte. La revisión humana del corpus y la persistencia son pendientes separados.
4. **Corpus:** revisar OCR/páginas, vigencia y aplicabilidad antes de cambiar `approved`. Repetir la evaluación estricta del agente después. No aprobar una fuente solo para pasar la prueba.
5. **Persistencia:** prueba remota controlada con datos ficticios: respuesta citada antes del reinicio, reinicio/nueva instancia y respuesta citada después; registrar revisión y fuente. Por separado, crear documento de prueba aprobado/índice o borrador demo y verificar retención después. Si solo sobrevive la semilla, documentar el alcance y desplegar una solución duradera antes de declarar retención administrativa.
6. **Equipo:** completar aportes y uso de IA, ensayar instalación en diez minutos con cronómetro, exposición de doce y vídeo de respaldo de dos. Mantener autenticación y usar una cuenta demo; no abrir valores de secretos al compartir pantalla.

## Sustentación: guion y material que exige el PDF del docente

Doce minutos de exposición y tres de preguntas; todos los integrantes deben presentar un tramo y poder explicar cualquier parte. Orden sugerido: problema/usuario 1 min; demo pública 4 min (respuesta con cita, fuera de tema/abstención, acción demo con confirmación); arquitectura 2 min; evidencias 2 min; seguridad 1 min; límites 2 min. El integrante que explica cada tramo debe decidirlo y confirmarlo el grupo.

Antes del turno: ensayar una vez con reloj, grabar vídeo real de dos minutos, abrir URL/repositorio/PDF, probar cámara/micrófono 30 minutos antes, despertar health y hacer una pregunta diez minutos antes. Si falla la demo, usar el vídeo/capturas y avisar, sin desactivar seguridad.

## Entrega ZIP y plazo: un bloqueo adicional encontrado

El docente exige **un ZIP de máximo 20 MB**, sin `.env`, `.venv`, `node_modules` ni `__pycache__`, y el mismo contenido del proyecto en GitHub. Nombre: `NombreProyecto_Semana4.zip`. Fecha oficial: **lunes 9 de noviembre de 2026 a las 23:59 de Ecuador**; prórroga máxima: **miércoles 11 a las 23:59**.

La medición del proyecto conocido, con ZIP DEFLATE nivel 9 y exclusiones de secretos/dependencias/metadatos, produjo **28.818.950 bytes (27,48 MiB)** para 262 archivos. Ver [medición](evidencias/semana-4/tamano-paquete-2026-11-07.json). Solo seis archivos grandes ya sumaban aproximadamente 22,08 MiB con DEFLATE nivel 6. No cabe sin intervención en un ZIP estándar de 20 MB. Los PDF del corpus y la imagen del frontend son los mayores. No se entregó un ZIP sobredimensionado ni se quitaron PDFs referenciados por el manifiesto de ingesta para ocultarlo.

Opciones a acordar: optimizar recursos con validación de calidad e integridad y actualizar hashes/pruebas cuando cambien originales; o solicitar al docente una excepción o modalidad de corpus externo verificable. Esta segunda opción debe acordarse porque el requisito pide mismo contenido en ZIP y GitHub. Una optimización no puede invalidar el manifiesto o perder páginas/texto. No se incluye `.git` en el ZIP, pero excluirlo no elimina el problema del historial del repositorio remoto.

## Qué no debe marcarse aún

No marcar todas las casillas por tener CI verde. El docente pide historial limpio, evaluación final comparable, índice que sobreviva a reinicio, aportes individuales, evidencias de sustentación y ZIP dentro del límite. El reporte actual permite acreditar varios puntos, pero deja explícitas estas condiciones y cómo verificarlas.

## Optimización y tareas de código posteriores

La conversión de capturas a PDF en `6151271` redujo el ZIP medido a 25,28 MiB. Esta rama añade WebP sin pérdida, empaquetador con límite y evaluación manual sin despliegue. El corpus comprimido por sí solo ocupa 21.201.054 bytes: optimizar imágenes de documentación no basta para 20 MB. Las medidas previas se conservan como históricas. Ver [plan actualizado](17-plan-cierre-y-tamano.md) para acciones por s4b/s4c/s4e, opciones de corpus y pruebas que faltan. Ninguno de esos pendientes se cierra por tener preparados los scripts.

## Corte posterior de main e3e8b22

Actions 42422021200 aprobó el despliegue de `e3e8b22` y sus casos públicos. Ya existen responsabilidades/herramientas de IA y verificación común confirmadas en README; no siguen todas sin declarar. Se añadieron `docs/Presentacion.pdf` y `EvidenciasSemana4.pdf`, pero sigue sin versionarse el JSON completo exitoso ni constancia de no reutilización/rotación de valores legacy. El paquete actual es **27,39 MiB**, no 24,82 MiB. Ver [contraste detallado y pasos de cierre](18-verificacion-cierre-legacy.md). Se preservan cortes y mediciones previas como históricos.

## Siguiente corte después del merge #23

El [plan operativo actualizado](19-pasos-cierre-y-compresion.md) ordena los comandos y evidencias pendientes. Base `279580e`: paquete actual 28.727.410 bytes. Una propuesta temporal con compresión con pérdida mide 18.909.976 bytes, pero **no está aplicada ni es un ZIP entregable**: requiere revisión visual, trazabilidad de derivados, hashes/OCR e ingesta/pruebas. Los pendientes de credenciales, JSON completo, evaluación final y observaciones permanecen abiertos hasta aportar su evidencia.

## Registro de actuación sobre la contraseña administrativa

El operador confirmó cambio de contraseña, nuevo despliegue y acceso exitoso con la nueva. La [constancia de actuación](evidencias/semana-4/actuacion-credenciales-legacy.md) distingue esa declaración de los metadatos y validaciones aún pendientes. El JSON completo 35/35 ya se incorporó mediante el PR #25, pero no se atribuye a una ejecución posterior a la rotación sin comprobar fecha/revisión. Se conservan los cortes anteriores como históricos.

## Optimización del paquete preparada para revisión

Se aplican en la rama dos PDF derivados y un avatar WebP menor, con hashes/procedencia y asociación del OCR actualizados; se conservan las fuentes y ambas presentaciones. La ingesta aislada mantiene 1.047 fragmentos y el baseline léxico 14/16 + 4/4. [Transformación, validaciones y revisión visual pendiente](20-paquete-comprimido.md). No equivale a aprobar normativa/OCR ni a desplegar automáticamente esta rama. El ZIP final se mide de nuevo después de reunir los PR de evidencia y optimización.

## Cierre documental de equipo y conteos

README amplía aportes y declara Gemini, ChatGPT y Codex según confirmación del equipo. El [registro de sustentación](evidencias/semana-4/observaciones-sustentacion.md) ya contiene SUST-01; no permanece vacío ni se fabrica un acta del tribunal. El corte de esa revisión fue **112 pruebas backend y 88,84 % de cobertura de app**, con [XML nuevo y reconciliación histórica](21-conteos-de-pruebas.md). Los reportes de 99, 104 y 105 conservan sus fechas y no se reescriben.

## Preparación adicional de persistencia e historial

PostgreSQL/Cloud SQL optativo y exportación/importación están implementados y probados localmente; no se activaron recursos facturables. [Procedimiento y revisión de costo](22-postgresql-cloudsql.md). S4c no se marca cumplido antes del ensayo remoto. La [simulación de limpieza histórica](23-limpieza-historial-preparada.md) solo modifica una copia privada; GitHub conserva el historial sensible hasta acordar/publicar la reescritura. Ninguno de estos pasos se equipara a entregar el ZIP en el portal o aprobar el OCR.

## Decisión de costos del equipo — 8 de noviembre de 2026, Ecuador

PostgreSQL/Cloud SQL queda técnicamente preparado y probado localmente. Su activación se difiere por costos y se realizará oportunamente con presupuesto aprobado y validación remota. No se crean recursos ahora ni se presume una dispensa del requisito docente; la operación actual conserva SQLite y su limitación de persistencia administrativa. [Decisión y guía futura](ADR-0004.md).

## Publicación coordinada del historial — 8 de noviembre de 2026, Ecuador

Se publicaron 27 ramas mediante operación atómica con leases. Main `2482401` aprobó [Actions 42453615683](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42453615683) y despliegue. Los clones deben renovarse. [Resultado, mapa y pendientes de PR/cachés](24-cierre-historial-publicado.md); no se envió una solicitud a soporte ni se afirma purga completa. La decisión de costos de Cloud SQL sigue vigente.

## Neon: importación y activación reportadas

El equipo creó la base PostgreSQL 17, guardó el respaldo privado, importó y reportó activación mediante Secret Manager en Cloud Run. Falta acreditar la conservación entre revisiones con reportes antes/después. [Guía Neon](26-neon-persistencia.md). Cloud SQL continúa diferido por costos. El corte de pruebas TLS es 132 aprobadas, cobertura app 89,11 %, con dos casos nuevos respecto a 130; no acredita conexión real a Neon.

## Actualización Neon y persistencia

Se conservan arriba los cortes históricos. El estado vigente ya no es «Neon en preparación»: el operador importó, vinculó el secreto y reportó reindexación en producción. Falta la evidencia antes/después de recrear revisión, con descarga íntegra y consulta citada. No repetir la migración por el error del reporte posterior al commit. [Incidente y ensayo remoto](26-neon-persistencia.md). La suite ampliada y evidencia local se describen en [el cierre de pruebas](27-pruebas-persistencia.md).

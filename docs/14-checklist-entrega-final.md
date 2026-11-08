# Estado de entrega final y sustentación — Grupo 1

Corte vigente: 8 de noviembre de 2026 UTC. Evaluación final sin despliegue aprobada en [Actions 42443602234](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42443602234), SHA `16081c8224ba07d1b0b917f89266f6bb562fb0e5`: recuperación/chat y agente estricto 6/6. Los cortes anteriores conservan su alcance histórico. Esta ejecución aislada no acredita un despliegue HTTP nuevo.

Se contrastaron los documentos del docente **Sustentacion_sabado_7_paso_a_paso.pdf** y **Entrega_final_proyecto_comite_evaluacion (1).pdf**, aportados por el equipo. Sus hashes constan en la [auditoría](evidencias/semana-4/auditoria-secretos-y-comite-2026-11-07.json). Se usan como requisitos de entrega, no como prueba de que el grupo ya los cumplió.

## Lista s4a–s4k: marcar solo lo acreditado

| Punto | Estado actual | Evidencia / acción de cierre |
| --- | --- | --- |
| s4a — URL pública en README y health | **Cumplido en la revisión probada** | URLs reales, smoke de SHA y 35 casos públicos aprobados; mostrar navegador privado durante la demo. |
| s4b — Credenciales solo en plataforma, incluido historial limpio | **Parcial** | Código y rutas legacy retirados, WIF y secretos de ejecución. Exclusiones de Gitleaks justificadas por falsos positivos; otros valores funcionales siguen en historial. Rotación de ADMIN_PASSWORD, nuevo despliegue y acceso con la nueva contraseña confirmados por el operador; ver [constancia](evidencias/semana-4/actuacion-credenciales-legacy.md). Faltan metadatos y pruebas posteriores a esa actuación, revisión de otros entornos/copias y limpieza coordinada del historial si se exige el literal del requisito. Ver [auditoría](15-auditoria-credenciales-historicas.md). |
| s4c — Índice persistente tras reinicio | **Parcial / ensayo remoto pendiente** | La imagen contiene semilla léxica y el corpus base se restaura al desplegar. No acredita retención de cargas/índices administrativos. Ensayar reinicio de la revisión y una respuesta con cita; documentar alcance base y resolver almacenamiento duradero para cambios. |
| s4d — 15+ casos públicos, incluida inyección | **Cumplido en ejecución; completar material visual** | 35/35 con fecha, SHA y tres consultas generativas, más inyección y rutas retiradas. Guardar el JSON por caso del intento 2 y su p95; no reutilizar el p95 del intento fallido. La red del chat bloquea descargar el artefacto, no se inventa su contenido. |
| s4e — Evaluación final repetida frente a semana 3 | **Cumplido en el alcance automatizado** | Mismo golden set de 20 preguntas y seis casos del agente; léxico 14/16, híbrido/citas 16/16, negativas 4/4 y agente estricto 6/6, sin fallback. [Comparación y límites](07-evaluacion.md), Actions 42443602234, SHA `16081c8`; JSON completos versionados. No acredita exhaustividad semántica ni aprobación del OCR. |
| s4f — Tasa y errores seguros | **Cumplido en alcance implementado** | 30 consultas/60 s/proceso, alias compartidos, 429/Retry-After, timeout, respaldo y errores categorizados sin excepción cruda; tests estrictos. No es cuota distribuida ni por usuario. |
| s4g — Aviso de IA y minimización de datos | **Cumplido en alcance educativo básico** | Interfaz identifica IA, orientación no oficial, pide verificar fuentes y prohíbe compartir contraseñas/datos sensibles. Contexto opcional acotado, métricas sin texto libre. El texto de consulta/contexto sí se envía al proveedor seleccionado; ver [tratamiento de datos](16-datos-y-limites.md). |
| s4h — README y decisiones; instalación en diez minutos | **Documentación preparada; ensayo humano pendiente** | README, requisitos, ADR y comandos corresponden al código. Registrar instalación por un integrante nuevo, duración real, ambiente y health. No hay un tiempo de diez minutos medido por otra persona. |
| s4i — IA y aportes por integrante | **Parcial** | Asistencia declarada y tabla de identidades observadas. Cada integrante debe confirmar tareas, herramientas, revisiones y ejemplos; no se rellena como si la IA conociera sus contribuciones. |
| s4j — PDF de la presentación de doce minutos | **Archivo preparado** | `docs/presentacion-entrega4.pdf` actualizado y PDF técnico de apoyo. Falta ensayo cronometrado y confirmar que esta es la versión realmente usada. El informe técnico extenso no sustituye la exposición de 12 minutos. |
| s4k — Evidencias y observaciones de sustentación | **Parcial** | Reportes locales, producción y seguridad presentes; añadir capturas de health, pipeline verde y resultados públicos. Registrar observaciones reales del tribunal y commits de cierre en [registro](evidencias/semana-4/observaciones-sustentacion.md). No se inventan observaciones. |

## Qué ya está cerrado de la ficha antigua

- [x] Módulo legacy eliminado de HEAD y rutas antiguas retiradas en la URL probada.
- [x] Despliegue con SHA verificable y pipeline dependiente de cinco controles previos.
- [x] 35 casos públicos, incluida generación real directa y por proxy SSE; se resolvieron los tres 503 anteriores.
- [x] Tests estrictos restaurados y aislados de claves reales: 104 backend, cobertura 88,73 %, 18 frontend y suite de navegador de 10 escenarios según la evidencia disponible.
- [x] Límite de consultas compartido, errores seguros y documentación técnica de endpoints/secuencias.
- [x] Falsos positivos de las seis exclusiones de Gitleaks identificados y separados de credenciales legacy.
- [ ] Requisito literal de historial sin credenciales: no se satisface solo eliminando HEAD.
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

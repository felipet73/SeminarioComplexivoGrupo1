# Observaciones reales de la sustentación y correcciones

## Fuente del registro

El equipo aportó el siguiente balance en esta conversación: «La sustentación estuvo muy bien, la única falla fue que no obtuvimos respuesta solicitando información, pero quedó subsanado porque ya identificamos algunas».

Se registra como **relato del equipo sobre la sustentación**, no como transcripción literal ni acta firmada del tribunal. La fecha/hora exacta de la sesión, la pregunta fallida y la causa concreta corregida no fueron especificadas. Se solicitó ese detalle para completar trazabilidad; no se deduce de errores observados en otras ejecuciones.

## Observación reportada

| ID | Fecha/hora Ecuador | Observación aportada | Estado y alcance | Acción y evidencia | Responsable |
| --- | --- | --- | --- | --- | --- |
| SUST-01 | Fecha/hora de la sesión no aportadas | Una solicitud de información no obtuvo respuesta durante la demostración. El equipo indica que fue la única falla y que quedó subsanada. | **Corregida según confirmación del equipo**, con validación posterior general. Reproducción de la pregunta exacta pendiente de identificación. | Se conservan las verificaciones públicas 35/35 y la evaluación final aprobada de 20 preguntas y agente 6/6. Esos conjuntos respaldan funcionamiento posterior en sus casos, pero no demuestran por sí solos la corrección de la pregunta concreta de la demo. Ver referencias siguientes. | Equipo del proyecto; responsable específico de esta corrección no identificado. Los aportes por persona se declaran en README sin asignar esta incidencia a alguien por inferencia. |

El equipo describió positivamente la sustentación. No se convierten ese balance ni la frase «la única falla» en una calificación oficial, acta del tribunal o garantía de ausencia de otras observaciones. No se aportaron otras observaciones específicas para registrar.

## Validaciones posteriores disponibles

- Pruebas públicas completas: [JSON de revisión 279580e](produccion-279580e-20261107-214127.json), **35/35**, cero omitidos, fecha interna 8/11/2026 02:41 UTC. El reporte identifica su SHA, URLs y casos; no se vincula automáticamente con la pregunta de la demo ni con posteriores cambios de configuración.
- Evaluación final: [Actions 42443602234](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42443602234), SHA `16081c8224ba07d1b0b917f89266f6bb562fb0e5`, **recuperación/chat aprobados y agente estricto 6/6 sin fallback**. [Reportes completos](2026-11-08-evaluacion-final-aprobada/).
- Los 429 del segundo intento de evaluación se diagnosticaron como saturación por RPM y se corrigió el ritmo en `d5cca81`. Ese diagnóstico está acreditado para la evaluación automatizada; **no se atribuye a la falla de la sustentación sin confirmación específica**. Ver [evaluación y comparación](../../07-evaluacion.md).

Para completar SUST-01: añadir la pregunta exacta o una síntesis fiel, fecha de sesión, causa identificada, cambio/commit que la resolvió y repetición del mismo caso con resultado. Mantener las evidencias generales y los fallos anteriores, aunque se añada una comprobación específica.

## Revisión técnica de cierre documental

Estos puntos fueron solicitados por el equipo en la revisión del repositorio; **no se presentan como observaciones del tribunal**:

| ID | Punto | Actuación documentada |
| --- | --- | --- |
| DOC-01 | Registro de sustentación vacío | Se incorpora SUST-01 con el relato aportado y sus límites de verificación. |
| DOC-02 | Aportes demasiado resumidos y declaración de IA incompleta | README detalla despliegues/CI/optimización de Christian, pruebas manuales/backend semana 4 de Olmes y tests/documentación backend, automatización frontend y fuentes de Widman. La declaración incluye Gemini, ChatGPT y Codex. |
| DOC-03 | Conteos de pruebas diferentes | [Registro de conteos](../../21-conteos-de-pruebas.md): 99 → 104 → 105 → 110 → 112 por incorporación de casos; no se borró ninguno de los 99 originales. Nuevo XML con 112 aprobadas y cobertura de app 88,84 %. Evidencias anteriores preservadas como históricas. |

## Material y pendientes separados

**Presentación usada en vivo:** el equipo confirmó `docs/Presentacion.pdf` (10 páginas con infografías). `docs/presentacion-entrega4.pdf` es material anterior.

Las capturas aportadas de Cloud Run, configuración de secretos, health y panel se describen en la [constancia de rotación](actuacion-credenciales-legacy.md); no se confunden con comentarios del tribunal ni con imágenes ya versionadas si solo se aportaron en el chat. Adjuntar el vídeo de respaldo cuando el equipo lo aporte. Ver [checklist de entrega](../../14-checklist-entrega-final.md).

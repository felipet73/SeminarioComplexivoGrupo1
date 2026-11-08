# Observaciones reales de la sustentación y aclaraciones

## Fuente y aclaración del equipo

El equipo describió positivamente la sustentación y aclaró expresamente: «No fue falla del sistema, solo que en ese momento no tenía una pregunta que requiera información adicional, está 100 % probado posteriormente».

La observación corresponde a **un escenario que no se logró mostrar durante la demo**, no a una consulta fallida ni a una ausencia de respuesta del sistema. Se corrige la interpretación inicial del registro. Se documenta el relato del equipo, no una transcripción literal o acta firmada del tribunal. La fecha/hora exacta de la sesión no fue aportada.

## Observación reportada

| ID | Fecha/hora Ecuador | Observación aclarada | Estado y alcance | Acción y evidencia | Responsable |
| --- | --- | --- | --- | --- | --- |
| SUST-01 | Fecha/hora de la sesión no aportadas | Durante la demostración no se dispuso de una pregunta que activara la solicitud de información adicional del asistente. No fue un fallo del sistema. | **Descartada como defecto del sistema por aclaración del equipo.** El comportamiento fue verificado posteriormente según confirmación del equipo. | Registrar el escenario de aclaración para futuras demos. Hay pruebas automatizadas específicas de campos adicionales; la verificación manual posterior es declarada por el equipo, sin adjuntar aquí un reporte de ese caso en producción. | Equipo del proyecto; no se atribuye una corrección de código ni una incidencia a un integrante porque no se reportó un defecto. |

La expresión «100 % probado» se conserva como confirmación del equipo de que verificó el comportamiento. No se convierte en una garantía universal ni en una métrica nueva sin dataset. No se necesita localizar una supuesta pregunta fallida, causa o commit de reparación: esa interpretación fue retirada. No se aportaron otras observaciones específicas.

## Evidencia específica de solicitud de información adicional

La suite actual incluye estas pruebas en [test_endpoints.py](../../../backend/tests/test_endpoints.py):

- `test_aclaracion_expone_controles_permitidos_y_omite_datos_ya_ingresados`: una salida de modelo simulada solicita carrera/curso; valida campos únicos, tipo y opciones, omisión de datos ya ingresados, respuesta SSE y abstención si la aclaración ya no puede completarse.
- `test_no_solicita_datos_sensibles_o_campos_en_un_rechazo` comprueba que una solicitud de contraseña se descarta y que una consulta fuera de dominio sigue rechazándose.

Estas pruebas usan un modelo doble y acreditan el contrato de la aplicación, no una elección espontánea del proveedor en producción. Sus resultados forman parte del [XML actual de 112 pruebas aprobadas](2026-11-08-conteo-pruebas/pytest-backend.xml). La comprobación manual posterior del escenario con el asistente real consta por declaración del equipo; no se atribuye a un caso de otro reporte.

## Otras validaciones de alcance separado

- [Pruebas públicas completas](produccion-279580e-20261107-214127.json): **35/35**, cero omitidos; fecha interna 8/11/2026 02:41 UTC y SHA `279580e`. No se presentan como la prueba específica de aclaración.
- [Evaluación final, Actions 42443602234](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42443602234), SHA `16081c8224ba07d1b0b917f89266f6bb562fb0e5`: recuperación/chat aprobados y agente estricto 6/6 sin fallback. [Reportes completos](2026-11-08-evaluacion-final-aprobada/).
- Los 429 de un intento anterior de evaluación fueron una saturación de solicitudes por minuto corregida mediante ritmo de llamadas. No se vinculan con la sustentación ni con la falta de un ejemplo de aclaración.

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

# Consultas con datos académicos faltantes

El bot principal puede solicitar datos relevantes sin obligar a completar todo el formulario de contexto. La IA responde JSON con `estado: "aclaracion"` y `campos_necesarios`, una lista de identificadores permitidos. Las reglas se agregan en backend a cualquier versión activa del system prompt.

Ejemplo de salida de la IA:

```json
{
  "respuesta": "Para orientarte necesito tu carrera y nivel de estudios.",
  "estado": "aclaracion",
  "fragmentos": [],
  "campos_necesarios": ["carrera", "curso"]
}
```

El backend valida la salida, elimina duplicados y omite campos ya presentes en el contexto. No interpreta texto libre para inventar formularios. Solo admite carrera, curso, modalidad, período, jornada, tema, objetivo, sede y modalidad de titulación. Campos desconocidos invalidan la salida y provocan abstención segura. La ausencia de normativa no se resuelve pidiendo datos del estudiante: debe producir abstención, no una solicitud indiscriminada de campos.

La respuesta pública de `/api/chat` y el evento SSE `done` de `/api/chat/stream` contienen descriptores de controles definidos por el servidor:

```json
{
  "campos_necesarios": [
    {"campo":"carrera","etiqueta":"Carrera","tipo":"texto","opciones":[],"max_length":120},
    {"campo":"curso","etiqueta":"Nivel / curso","tipo":"select","opciones":["Primer nivel","Segundo nivel","Tercer nivel","Cuarto nivel","Quinto nivel","Sexto nivel","Séptimo nivel","Octavo nivel","Noveno nivel","Décimo nivel","Egresado/a"],"max_length":80}
  ]
}
```

El array es vacío por defecto en respuestas normales, rechazos, abstenciones y aclaraciones sin campos pendientes. El frontend tolera su ausencia para compatibilidad con respuestas anteriores.

## Interacción

La respuesta se conserva en la conversación y se repite en un diálogo modal nativo accesible, con controles de texto o selección. Este controla foco, Escape y bloqueo del fondo. Incluye animación suave y respeta reducción de movimiento.

- **Volver a consultar:** valida todos los campos solicitados; no permite texto vacío, espacios, valores demasiado largos ni opciones fuera del selector. Reenvía la pregunta original, el proveedor elegido y el contexto previo combinado con los nuevos datos. No envía el texto de la aclaración como una pregunta nueva.
- **Salir sin consultar / Escape:** cierra el diálogo sin llamar al modelo y conserva la respuesta del chat.
- La respuesta conserva un botón **Completar datos necesarios** para reabrir el diálogo. Se conserva la pregunta y el proveedor de esa respuesta, incluso después de enviar otras consultas. Solo se ofrecen los campos aún pendientes en el contexto actual; tras completarlos, desaparece el botón de esa aclaración.
- Durante la llamada se bloquean envíos duplicados y se muestra el estado de espera. Si falla el proveedor, se mantienen los valores y el diálogo para reintentar. Si hacen falta otros campos, se muestra la nueva aclaración.
- Tras una consulta exitosa los datos se reflejan en «Personaliza tu orientación» y se usan en las siguientes preguntas. Solo se mantienen en memoria, no en localStorage.

Los campos de contexto también se normalizan y validan en backend. Las opciones académicas son orientativas, no una certificación de la oferta institucional; carrera, sede y período permiten texto libre. No se solicitan nombres, cédulas, credenciales ni datos de terceros.

## Sugerencias públicas y simulación administrativa

El chat normal propone preguntas útiles de matrícula, titulación y prácticas. Las pruebas rápidas de positivo/abstención/inyección se ofrecen exclusivamente dentro de Análisis en `/admin`; seleccionarlas rellena el caso, no llama al modelo hasta ejecutar.

La simulación muestra cada caso con una pregunta de usuario y una burbuja de respuesta por versión/revisión de prompt. Mantiene tiempos, tokens, estado, citas, huella y salida original del modelo inspeccionable. Usa el mismo flujo backend que el chat público: defensas locales, instrucciones obligatorias JSON, validación de citas y campos necesarios. Las pruebas negativas bloqueadas localmente no gastan tokens de generación. Desde el 28 de octubre no se ejecuta un juez posterior: solo respuestas, mediciones y trazas explicativas.

Al completar datos desde una variante se lanza una nueva comparación de **ese caso** para todas las versiones de la ejecución, con las revisiones actualmente vigentes, mismo proveedor y contexto para todas. Se conserva el trabajo anterior y se avisa en la pantalla que es una nueva comparación; consume llamadas adicionales. Las preguntas son casos independientes, no una memoria conversacional persistente. Durante la evaluación no hay fallback para evitar mezclar proveedores. Los trabajos anteriores sin contrato estructurado siguen siendo consultables como texto.

## Verificación

Backend: `cd backend` y `.\.venv\Scripts\python.exe -m pytest -q`.

Frontend: `cd frontend`, `npm run build`, `npm run test`, `npm run test:admin`. Esta última suite incluye el flujo del popup con SSE simulado, validación, mismo modelo/pregunta y vista móvil, sin consumo de proveedores. Captura en `frontend/test-results/chat-campos-movil.png`.

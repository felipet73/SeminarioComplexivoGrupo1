# Flujo automatizado de orientación

El pipeline actual agrega despliegue posterior a secretos, backend, frontend, navegador y contenedor mediante `needs`. En main se conserva y promueve la imagen probada a Artifact Registry/Cloud Run; después se comprueba SHA, corpus, rutas retiradas, SSE y 32 contratos HTTP públicos. Requiere configurar o confirmar identidad Google Cloud y repositorio de imágenes; no se afirma que el job nuevo haya sido ejecutado. La documentación operativa está en [13-despliegue.md](13-despliegue.md) y los casos en [08-pruebas.md](08-pruebas.md).

La entrada se valida con `ConsultaChat`. `backend/app/flujo.py` expone orientar y resolver, usadas por la API y la evaluación. El flujo bloquea inyección conocida, recupera fuentes aprobadas y vigentes, aplica umbrales de pertinencia, y se abstiene sin llamar al modelo si no hay evidencia. Las consultas de preparación de borradores usan contexto de titulación en lugar de los valores libres del formulario para buscar.

Con evidencia, el agente ejecuta solicitudes de herramientas validadas y puede consultar más pasajes. El backend valida el JSON final, las citas y los campos faltantes. Solo se piden datos necesarios; una aclaración sin campos pendientes se descarta. El frontend muestra respuesta, referencias, controles de aclaración y, cuando corresponde, los argumentos de una propuesta que requiere decisión humana.

Las propuestas caducan a los 30 minutos. Aprobar guarda un borrador local; cancelar no guarda solicitud. La capacidad de confirmación no se escribe en los logs de métricas ni en auditoría. Reintentar la misma decisión es idempotente. Los endpoints de decisión no aceptan nuevos argumentos ni permiten modificar la propuesta al aprobarla.

Ejecutar desde la raíz, con el entorno backend activado:

```bash
python scripts/ingest.py --data-dir data/eval-state --strategy lexical
python eval/evaluar_flujo.py
```

Los 20 casos de `eval/casos_flujo.jsonl` cubren preguntas educativas, citas, ausencia de evidencia, inyección, JSON inválido, herramientas prohibidas, bucle, checklist y confirmación/cancelación. Usan corpus real y un modelo doble de guion explícito: verifican contratos y controles, no calidad generativa. El resultado falla si no pasan los 20 casos. CI lo ejecuta en cada push y pull request.

La evaluación del modelo real es independiente:

```bash
python eval/evaluar.py --chat --prompt system_v3
```

Incluye consumo real de API. El informe contiene pregunta, respuesta esperada, documento/artículo esperado, resultados recuperados, respuesta producida y acierto de cita. Una coincidencia de artículo no sustituye la revisión del contenido.

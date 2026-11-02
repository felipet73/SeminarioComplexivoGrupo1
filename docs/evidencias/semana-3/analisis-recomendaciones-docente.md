# Análisis de las recomendaciones del docente e implementación — Grupo 1

**Proyecto:** Titulación y normativa académica — UNIANDES.  
**Corte de la verificación:** 1 de noviembre de 2026.  
**Referencia:** `Guia_practica_Entrega3_por_proyecto (3).html`, observaciones del grupo 1, sección «3 · El camino, paso a paso» y requisitos de «Lo que piden a todos».

Este documento resume qué solicitó el docente, qué se implementó y por qué responde a cada observación. Distingue implementación comprobada localmente, decisiones equivalentes a los ejemplos de la guía y pendientes que requieren publicación o revisión humana. La matriz técnica ampliada está en [auditoría de la Entrega 3](../../12-auditoria-entrega3-grupo1.md).

## 1. Análisis de los hallazgos específicos del grupo 1

| Observación del docente | Análisis y solución implementada | Por qué atiende la observación |
|---|---|---|
| La normativa real no estaba disponible en un clon limpio; el manifiesto solo mostraba descargas fallidas. | Se incorporaron cinco originales al directorio `data/raw`, con hashes y procedencia en el manifiesto. `scripts/ingest.py` reconstruye los fragmentos con el mismo indexador del administrador. Las políticas de vigencia y aprobación se leen de `config/fuentes.yaml`. | El conocimiento ya no depende exclusivamente de la base privada del panel. Se reconstruyeron **961 fragmentos desde un estado limpio**, conservando documento, revisión, sección y página. Los fallos históricos de descarga se preservaron en un archivo separado. |
| La evaluación asignaba resultados según el nombre del prompt y no medía respuestas reales. | Se eliminó `scripts/evaluar_prompts.py`. Se añadieron 20 preguntas con fuente/artículo y respuesta esperados, evaluación de recuperación, comparación léxica/híbrida y ejecución del chat real mediante `--chat`. | Las puntuaciones se calculan a partir de fragmentos y respuestas obtenidos. Los informes conservan casos, resultados y denominadores; las pruebas con modelo doble se identifican expresamente y no se presentan como calidad del modelo real. |
| El modo activo por defecto era léxico aunque se documentaba búsqueda semántica. | Las nuevas configuraciones usan `hybrid`; se midieron ambos modos y se activó el índice híbrido evaluado en el panel local. El proveedor de embeddings se selecciona explícitamente y cambiarlo exige reindexación. | Se verificó una recuperación de **14/16 con BM25 frente a 16/16 con híbrido**, manteniendo silencio en 4/4 negativas. La búsqueda por significado quedó implementada y medida, sin mezclar vectores de modelos distintos. |
| Existían documentación desactualizada, variables de Chroma sin uso y diapositivas temporales en el repositorio. | Se actualizaron README y arquitectura para describir React/Vite, FastAPI y SQLite con vectores persistentes. Se retiraron variables de Chroma sin uso. Las 20 diapositivas se trasladaron a un respaldo local ignorado por Git. | La documentación describe componentes existentes y sus límites. Las diapositivas se conservaron localmente, separadas del material que se prepara para publicar. |

Evidencias: [ingesta limpia](ingesta-limpia.json), [comparación real](comparacion-real.json) y [chat con proveedores reales](chat-real-hibrido.json). Las fuentes incluyen LOES, Reglamento de Régimen Académico y documentos institucionales aportados por el equipo; su incorporación técnica no reemplaza la validación humana de actualidad normativa.

## 2. Revisión de todos los pasos del camino, incluidos los niveles avanzados

### 2.1. Corpus e ingesta, y paso propio g1a

**Recomendación:** disponer de documentos reales, ingesta repetible, fragmentos con procedencia, manifiesto con hash y fechas, y vigencia por fuente desde YAML.

**Implementación:** originales en `data/raw`, validación SHA-256 antes de modificar documentos, ingesta compartida con el panel, división por artículo/sección y exportación de fragmentos. `config/fuentes.yaml` aporta las políticas de cada fuente. Los documentos idénticos y sus índices compatibles se reutilizan.

**Justificación:** un evaluador puede reconstruir el corpus sin utilizar el estado local previo. Se conserva trazabilidad desde cada fragmento al original. En las fuentes cargadas por el administrador se registra la fecha de incorporación; la fecha de descarga desconocida permanece nula para no inventar procedencia. Esto cubre el objetivo del manifiesto, con esa diferencia declarada respecto al ejemplo de descarga del HTML.

Archivos: [manifiesto](../../../data/raw/manifest.json), [políticas de fuentes](../../../config/fuentes.yaml) e [ingesta](../../../scripts/ingest.py).

### 2.2. RAG con citas y silencio

**Recomendación:** ranking léxico real como mínimo, recuperación semántica, persistencia, búsqueda híbrida, citas y abstención cuando no exista evidencia suficientemente cercana.

**Implementación:** SQLite FTS5/BM25, umbral de cobertura léxica, embeddings persistentes, similitud coseno, umbral semántico y fusión RRF. Solo participan fuentes aprobadas, habilitadas, vigentes y con índice compatible. El chat se abstiene sin llamar al modelo cuando no recupera evidencia. Después de generar valida IDs citados y revisión vigente.

**Justificación:** se comprueban recuperación y silencio con las mismas 20 preguntas en ambos modos. Se conserva el control que impide publicar una respuesta con IDs inventados. La solución usa SQLite con vectores persistentes como alternativa arquitectónica a Chroma, conforme a la posibilidad de una implementación diferente que permite la guía. Se declara el límite de 5000 fragmentos y la búsqueda exhaustiva; no se atribuye al sistema un índice ANN inexistente.

Evidencias: [comparación](comparacion-real.json), [respuestas y citas reales](chat-real-hibrido.json) y [arquitectura](../../03-arquitectura.md).

### 2.3. Herramientas con contrato

**Recomendación:** herramientas tipadas, cálculos deterministas, parámetros configurables, casos límite y esquemas publicados; en el nivel recomendado, herramientas de lectura/cálculo y una con confirmación.

**Implementación:** `buscar_fragmentos`, `consultar_requisitos`, `generar_checklist`, `calcular_plazo` y `registrar_solicitud_tutor`. Pydantic valida entradas y salidas; los esquemas están disponibles en `/api/herramientas` y `/docs`. Los parámetros viven en `config/parametros.yaml`.

El checklist construye ítems extractivos con documento, sección, página e ID. Todos quedan pendientes de verificar y la salida declara que la lista no es exhaustiva. No transforma documentos informativos en obligaciones ni certifica cumplimiento estudiantil.

**Justificación:** las herramientas son ejecutables y verificables, con entradas inválidas rechazadas y pruebas de casos límite. El calendario trabaja con fechas e enteros, por lo que no necesita Decimal. Simula días hábiles indicados por el usuario, excluyendo fecha inicial y fines de semana; **no incorpora feriados ni calcula un vencimiento institucional oficial**. No se inventaron los parámetros normativos ni el artículo pendiente del ejemplo del HTML.

Archivos: [herramientas académicas](../../../backend/app/tools/academicas.py), [contratos HTTP](../../../backend/app/tool_routes.py) y [parámetros](../../../config/parametros.yaml).

### 2.4. Agente: lista cerrada, tope, confirmación e idempotencia

**Recomendación:** el modelo debe pedir herramientas, el backend debe limitar cuáles puede ejecutar y cuántas veces, y las escrituras deben requerir decisión humana. El nivel avanzado agrega idempotencia y auditoría.

**Implementación:** solicitudes JSON del modelo validadas antes de ejecutarse, `PERMITIDAS`, `MAX_ITER=4` y `REQUIEREN_OK`. Preparar una solicitud de tutor devuelve una propuesta con argumentos exactos y caducidad. React permite confirmar o cancelar. Solo la confirmación registra el borrador local.

El archivo [backend/app/agente.py](../../../backend/app/agente.py) contiene `ejecutar_agente` y el bucle `for vuelta in range(MAX_ITER)`. Se adoptó la organización recomendada: el registro relaciona cada nombre permitido con su modelo de entrada y función ejecutora; las herramientas están separadas en `app/tools/academicas.py`. El protocolo conserva el cliente Gemini/OpenAI existente y solicita una herramienta por turno mediante JSON. La API expone `/api/agente` y `/api/agente/confirmar/{id}`, además de las rutas previas compatibles.

**Justificación:** una herramienta ajena a la lista no se ejecuta y un bucle se detiene en el tope. Cada propuesta tiene un ID idempotente y una capacidad secreta; repetir la misma decisión no duplica el registro. Hay transacción, caducidad, auditoría y rechazo de decisiones contradictorias. Las pruebas cubren herramienta permitida, prohibida, agotamiento del bucle y confirmación/cancelación. El laboratorio comparativo deshabilita propuestas de escritura.

El registro es una **demostración local**: no envía solicitudes, no asigna tutores ni modifica expedientes. La auditoría identifica la capacidad de demostración que decidió, no una identidad universitaria autenticada.

Evidencias: [pruebas del agente](../../../backend/tests/test_agente.py), [pruebas de decisiones](../../../backend/tests/test_actions.py), [decisiones de diseño](../../09-decisiones.md) y [vista móvil de confirmación](confirmacion-movil.png).

### 2.5. Evaluación reproducible, y paso propio g1b

**Recomendación:** 20 preguntas con fuentes esperadas, al menos cuatro sin respuesta en el corpus, medición de recuperación, citas y abstención, comparación de estrategias y escenarios A–D del agente; en avanzado, ejecución con umbrales en CI.

**Implementación:** `eval/preguntas.jsonl`, `eval/respuestas_esperadas.json`, `eval/evaluar.py` y `eval/comparar.py`. La opción `--chat` llama al flujo con proveedores reales. Existen además 20 contratos del flujo con modelo doble declarado. El workflow incorpora evaluación automática y una ejecución manual con secretos para las pruebas reales.

**Justificación:** los informes permiten comprobar qué pregunta acertó o falló y qué artículo se recuperó o citó. El resultado depende del comportamiento observado. Los umbrales hacen fallar la ejecución cuando no se cumplen: recuperación ≥70%, silencio ≥90%, contratos 20/20; en chat real, citas ≥80% y negativas 100%. La presencia de una cita correcta no se presenta como demostración automática de todas las afirmaciones de la respuesta.

Evidencias: [preguntas](../../../eval/preguntas.jsonl), [respuestas esperadas](../../../eval/respuestas_esperadas.json), [chat real](chat-real-hibrido.json) y [contratos del flujo](flujo-contratos.json).

### 2.6. Calidad: pruebas, CI, secretos y README honesto

**Recomendación:** pruebas automáticas, validación de entradas, errores HTTP adecuados, ausencia de secretos y documentación de lo que existe; en avanzado, cobertura, lint y revisión de dependencias.

**Implementación:** pruebas backend, frontend y navegador; cobertura mínima de 85%; Ruff para errores críticos; comprobador de patrones de secretos; auditorías de dependencias y workflow para push/PR. README y arquitectura distinguen funciones disponibles, límites y pendientes.

**Justificación:** las verificaciones locales terminaron correctamente y cuentan con evidencia. Se corrigieron dependencias vulnerables y se documentó separadamente la limitación del tooling heredado en Python 3.10. El inventario auditado de ejecución/pruebas y el frontend reportaron cero vulnerabilidades conocidas en la revisión final.

**Pendiente:** publicar los cambios y observar Actions en verde. Disponer del workflow y aprobar pruebas locales no demuestra que ya se haya ejecutado correctamente en GitHub.

Evidencias: [workflow](../../../.github/workflows/ci.yml), [cobertura](cobertura.xml), [auditoría de ejecución/pruebas](auditoria-runtime-final.json), [auditoría frontend](auditoria-frontend-final.json) y [plan de calidad](../../11-plan-de-calidad.md).

### 2.7. Archivos de los talleres y flujo automatizado

**Recomendación:** ADR, automatización, plan de calidad y parámetros; después, flujo con 20 casos y su evaluación en CI.

**Implementación:** `docs/09-decisiones.md`, `docs/10-automatizacion.md`, `docs/11-plan-de-calidad.md`, `config/parametros.yaml`, `backend/app/flujo.py`, `eval/casos_flujo.jsonl` y `eval/evaluar_flujo.py`.

**Justificación:** los documentos describen las herramientas realmente implementadas y los 20 casos recorren el flujo compartido con la API. Su evaluación exige 20/20 y está incorporada al workflow. Son implementaciones realizadas para esta entrega; no se presentan como archivos originales del taller que no fueron aportados. Su publicación remota sigue pendiente.

Referencia: [automatización](../../10-automatizacion.md) y [casos del flujo](../../../eval/casos_flujo.jsonl).

## 3. Mejoras adicionales dentro del alcance educativo

Se amplió el prompt para explicar, resumir y consultar fuentes educativas sin exigir una palabra específica de titulación. Se distingue normativa nacional de requisitos internos, se solicita contexto solo si cambia la respuesta y se evita pedir datos personales para resolver una ausencia de fuentes. Se incorporaron caché de embeddings y control de cuota para conservar progreso y reducir llamadas repetidas.

Estas mejoras atienden la necesidad de responder sobre las fuentes que el equipo seguirá incorporando. Mantienen el alcance de orientación académica y no agregan decisiones administrativas ni conexiones con expedientes reales.

## 4. Resultados comprobados

| Verificación | Resultado observado |
|---|---|
| Ingesta desde estado limpio | Cinco fuentes y 961 fragmentos trazables |
| Recuperación léxica | 14/16 preguntas positivas; silencio en 4/4 negativas |
| Recuperación híbrida | 16/16 positivas; silencio en 4/4 negativas |
| Chat con proveedores reales y RAG híbrido | Artículo esperado citado en 16/16; abstención o rechazo en 4/4 negativas; Gemini con respaldo OpenAI |
| Contratos del flujo con modelo doble | 20/20 |
| Backend | 50 pruebas aprobadas; cobertura de sentencias de 88,08% |
| Frontend | 15 pruebas aprobadas, compilación y generación OpenAPI verificadas |
| Navegador | 9/9 escenarios aprobados |
| Auditorías finales | 52 paquetes de ejecución/pruebas sin avisos conocidos; frontend sin vulnerabilidades reportadas |

Los resultados corresponden a esta muestra y a este corte; no garantizan exactitud en preguntas futuras ni sustituyen revisar las respuestas contra los documentos. Inventario de resultados: [resumen de verificación](resumen-verificacion.json).

## 5. Pendientes y alcance del cumplimiento

- Publicar los cambios y comprobar la ejecución remota de GitHub Actions, incluidos los secretos necesarios para la evaluación real.
- Validar humanamente actualidad, procedencia y aplicabilidad de las fuentes; ampliar preguntas y respuestas esperadas al incorporar documentos nuevos.
- Completar el levantamiento real de FAQ y la revisión del equipo. Los integrantes deben poder explicar los casos y las decisiones implementadas.
- Usar el entorno recomendado Python 3.12: la corrección de filelock del tooling del Python 3.10 heredado exige una versión superior. Esta limitación está separada del inventario de ejecución/pruebas auditado.
- Conservar explícitos los límites: checklist orientativo, calendario sin feriados ni vencimientos oficiales y solicitudes de tutor como borradores locales sujetos a confirmación. El despliegue público corresponde a la semana 4.

El cumplimiento técnico local queda sustentado por código, pruebas e informes. La publicación, la validación normativa y la revisión humana se mantienen identificadas como pendientes, sin declararlas completadas por el resultado de las pruebas.

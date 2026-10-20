# 03. Arquitectura propuesta — Semana 1

## Vista de componentes

```mermaid
flowchart TB
  U[Estudiante / evaluador] --> FE[Frontend Next.js + React
Chat / citas / checklist]
  FE -->|HTTPS JSON| API[FastAPI
Validación + límites + auditoría]
  API --> ORC[Servicio RAG / orquestador]
  ORC --> RET[Recuperación híbrida
vector + lexical + filtros]
  RET --> VDB[(ChromaDB
embeddings + metadatos)]
  RET --> LEX[(Índice textual)]
  ORC --> LLM[LLM por SDK en backend
proveedor configurable]
  ORC --> VER[Verificador de citas / abstención]
  ORC --> AG[Agente académico con lista cerrada de herramientas]
  AG --> T1[consultar_requisitos]
  AG --> T2[calcular_plazo]
  AG --> T3[generar_checklist]
  T1 --> RET
  T2 --> CAL[Calendario académico y feriados
verificados]
  T3 --> RULES[Reglas y datos ficticios/autodeclarados]
  PDF[(LOES + RRA/CES + UNIANDES
fuentes oficiales)] --> ING[Ingesta: descargar, validar vigencia, extraer, dividir por artículo]
  ING --> EMB[Modelo de embeddings multilingüe]
  EMB --> VDB
  ING --> LEX
  ING --> DOC[(Registro de documentos
URL, hash, versión, vigencia)]
  VER --> DOC
```

## Flujo completo de una consulta

```mermaid
sequenceDiagram
  actor E as Estudiante
  participant F as Frontend
  participant A as FastAPI
  participant R as Recuperador
  participant D as Índice vectorial/textual
  participant M as LLM
  participant V as Validador
  E->>F: Pregunta + contexto (carrera/modalidad)
  F->>A: POST /api/v1/chat (futuro)
  A->>A: Validación de dominio, privacidad y ambigüedad
  alt Falta un dato relevante
    A-->>F: Solicitar aclaración
  else Consulta académica suficientemente definida
    A->>R: Buscar con filtro de vigencia
    R->>D: Semántica + palabras clave
    D-->>R: Fragmentos + artículos + metadatos
    R-->>A: Evidencia recuperada
    alt No hay evidencia aprobada
      A-->>F: Abstención explícita
    else Hay evidencia
      A->>M: Prompt + evidencia delimitada (datos, NO órdenes)
      M-->>A: Borrador + IDs de evidencias
      A->>V: Verificar que las citas existen y respaldan afirmaciones
      V-->>A: Resultado de validación
      A-->>F: Respuesta citada o abstención
    end
  end
  F-->>E: Respuesta / aclaración / abstención
```

## Herramientas del agente

- `consultar_requisitos(modalidad: str, carrera?: str) -> {items:[{regla, fuente, articulo}]}`: consulta de reglas aprobadas; nunca escribe registros oficiales.
- `calcular_plazo(fecha_inicio: date, dias_habiles: int, calendario_id: str) -> {fecha_fin, fundamento, calendario}`: cálculo determinista con feriados explícitos; si calendario no está aprobado, error controlado.
- `generar_checklist(perfil_estudiante: PerfilDemo) -> {items:[{estado, evidencia, requisito}]}`: sin inventar cumplimientos; estados `cumplido`, `pendiente`, `no_verificable`.

## Modelo de datos mínimo

`Document` (document_id, title, institution, source_url, publication_date, verified_at, effective_from, effective_to, verification_status, sha256, local_path); `Chunk` (chunk_id, document_id, article, section, text, page_start, page_end, embedding_id); `EvaluationCase` (case_id, question, expected_type, expected_answer, expected_document, expected_article); `AuditEvent` (request_id, latency_ms, outcome, source_ids; sin PII).

## Seguridad y decisiones

1. API key solo en variables de entorno backend. `.env` ignorado; `.env.example` sin secretos.
2. Bloqueo de herramientas fuera de allowlist y validación de entradas con Pydantic.
3. Solo documentos aprobados entran al índice de producción; prohíbe respuestas oficiales desde fuentes pendientes.
4. No se implementa integración con expediente académico real en Semana 1.
5. ChromaDB se propone para MVP; PostgreSQL + pgvector es alternativa para despliegue y escala, su migración no altera interfaces de repositorio.
6. `/health` incluido y funcional; endpoints RAG descritos son **futuros**, no implementados todavía.

## Despliegue propuesto

Local: Python virtualenv + FastAPI; frontend y vector DB se añadirán en fase siguiente. Producción: Render/Railway o plataforma aprobada, HTTPS y configuración de secretos en panel. Puntos a revisar: persistencia ChromaDB en volumen duradero, límites de uso y cuotas del proveedor LLM.

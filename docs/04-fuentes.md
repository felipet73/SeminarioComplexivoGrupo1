# 04. Inventario de fuentes — Semana 1

**Fecha de revisión preliminar:** 19-10-2026. **Estado:** localización inicial, NO dictamen de vigencia. Una fuente hallada no está automáticamente aprobada para dar respuestas RAG.

| ID | Documento | Organismo / URL oficial | Vigencia verificada | Formato | Fragmentación prevista |
|---|---|---|---|---|---|
| F-01 | LOES, Ley Orgánica de Educación Superior | Asamblea Nacional / Registro Oficial: https://www.ces.gob.ec/ | Pendiente de confirmar texto consolidado y reformas | PDF/HTML | Por artículo y disposición transitoria |
| F-02 | Reglamento de Régimen Académico (RRA) | Consejo de Educación Superior: https://www.ces.gob.ec/ | Pendiente de confirmar última codificación y reformas | PDF | Por artículo/incisos, conservación de anexos |
| F-03 | Instructivo de titulación y examen complexivo (2017) | UNIANDES: https://www.uniandes.edu.ec/normativa-institucional/ | Publicado en portal; vigencia no confirmada | PDF | Por artículo y modalidad |
| F-04 | Lineamientos complexivo seminario carreras en línea (2024) | UNIANDES: https://www.uniandes.edu.ec/normativa-institucional/ | Publicado en portal; vigencia no confirmada | PDF | Por apartado/numeral y anexos |
| F-05 | Reforma 2023 Reglamento de prácticas | UNIANDES: https://www.uniandes.edu.ec/wp-content/uploads/2024/08/REFORMA-2023-REGLAMENTO-DE-PRACTICAS.pdf | Reforma 2023 localizada; verificar modificaciones posteriores | PDF | Por artículo; conservar transitorios |
| F-06 | Procedimiento prácticas en línea (2024) | UNIANDES: https://www.uniandes.edu.ec/wp-content/uploads/2024/08/V2-PROCEDIMIENTO-PRACTICAS-ON-LINE-2024.pdf | Publicado; confirmar aplicabilidad por modalidad | PDF | Por fase/paso, tablas como unidades |
| F-07 | Reforma al Reglamento de vinculación (2024) | UNIANDES: https://www.uniandes.edu.ec/normativa-institucional/ | Publicado en portal; vigencia no confirmada | PDF | Por artículo y disposición |
| F-08 | Instructivo de reconocimiento/homologación/reingreso (2023) | UNIANDES: https://www.uniandes.edu.ec/normativa-institucional/ | Publicado en portal; vigencia no confirmada | PDF | Por procedimiento y artículo |
| F-09 | Instructivo de becas de grado (2026) | UNIANDES: https://www.uniandes.edu.ec/normativa-institucional/ | Listado 2026, requiere archivo y confirmación | PDF | Por artículo, plazos y anexos |
| F-10 | Guías de Secretaría de Titulación | UNIANDES: https://www.uniandes.edu.ec/secretaria-de-titulacion-y-grados/ | Contenido de trámite sujeto a actualización | HTML/PDF | Por procedimiento, convocatoria y fecha |
| F-11 | Calendario académico / aranceles / trámites | UNIANDES: https://www.uniandes.edu.ec/ | Documento preciso no identificado todavía | HTML/PDF | Por convocatoria, fecha, campus/carrera |

## Política documental

1. Registrar URL directa y URL de página índice, fecha de consulta, SHA-256, emisor, resolución, publicación, reforma, inicio/fin de vigencia, aplicabilidad (carrera, campus, modalidad, período) y verificador.
2. Descargar solo desde entidades oficiales; preservar PDF original en `data/raw/` sin modificaciones.
3. Comparar codificación y reformas antes de activar; donde no se pueda verificar, `pending_review` y excluido del índice activo.
4. Dividir preferentemente por artículo completo. Si es largo, por inciso conservando número de artículo, encabezado, referencias cruzadas y paginación.
5. Extraer tablas y anexos con estructura; comprobar manualmente fragmentos que contienen cifras y fechas.
6. En caso de conflicto entre norma general e institucional, no decidir jerarquía jurídica automáticamente: señalar conflicto y derivar.

## Descarga local

Los documentos descargados automáticamente (cuando el servidor admite acceso) se registran en `data/raw/manifest.json`. Un archivo descargado **todavía no es normativa vigente validada**. Las fuentes pendientes pueden descargarse desde los enlaces oficiales anteriores. Para reintentos y actualización: `python scripts/descargar_fuentes.py`.

## Fuentes aportadas para la consigna

- PDF del caso académico «CASOS_Carrera_de_Software_agosto_2026_IA_Generativa», caso 01 grupo 1 (documento de la actividad; copia en `data/referencias/`).
- DOCX «Fase 1 las 15 preguntas frecuentes» (propuesta de preguntas y arquitectura; copia en `data/referencias/`).

## Brechas de evidencia documental

- LOES y RRA: obtener versión consolidada/codificada con resolución y fecha de reforma verificables.
- Calendario, tasas y plazos: requieren documentos de períodos y programas concretos.
- Sedes/modalidades/carreras: algunos instructivos pueden no ser universalmente aplicables.
- Vigencia de cada instrumento: requiere revisión humana antes de utilizar en el índice RAG.

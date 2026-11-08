# Pasos de cierre después del merge del PR #23

Base analizada: `279580e7276cff1b3cd7b625caabd8e2cd510fcc`. Fecha de trabajo: 8 de noviembre de 2026 UTC (7 de noviembre en Ecuador). Esta revisión aporta un plan y mediciones; no sustituye evidencia de ejecución ni aplica compresión al corpus.

## 1. Guardar la evidencia completa de producción

Con cambios locales preservados, entorno Python instalado y el despliegue del commit de main aprobado en Actions, ejecutar desde la raíz en PowerShell:

```powershell
git switch main
git pull --ff-only
git switch -c docs/evidencias-finales
$revision = git rev-parse HEAD
python scripts/pruebas_funcionales.py --incluir-modelo --expected-revision $revision --output docs/evidencias/semana-4/produccion-verificada.json
$LASTEXITCODE
```

Esperado: exit 0, 35/35, cero omitidos y revisión esperada igual a la publicada. Revisar también cada resultado del JSON. Si falla, conservar el reporte y corregir la causa; no cambiar el SHA para ocultar una discrepancia. Este comando consume las API configuradas en el backend. Alternativa: descargar el JSON completo del artefacto del despliegue exitoso en Actions y conservar la revisión que ese reporte acredita. Una captura o resumen de 35/35 no reemplaza los casos completos.

El entorno de este chat no tiene acceso directo a las URLs de producción ni al host de descarga del artefacto observado; aquí no se presenta una nueva ejecución contra producción como realizada.

## 2. Cerrar la actuación sobre credenciales antiguas

La contraseña y clave JWT de `seguridad.py` eran funcionales históricamente; no corresponden a las seis exclusiones de Gitleaks. Ver [auditoría](15-auditoria-credenciales-historicas.md) y [verificación](18-verificacion-cierre-legacy.md).

El responsable debe revisar Cloud Run → servicio → revisión que recibe tráfico → Variables y Secrets. Registrar referencias y versiones usadas, nunca valores. Revisar también otros entornos y URLs antiguos accesibles. Si no se puede asegurar la no reutilización de los valores legacy, reemplazar las credenciales reutilizadas por valores nuevos, desplegar y volver a validar. No probar de nuevo la contraseña histórica contra servicios.

Crear `docs/evidencias/semana-4/actuacion-credenciales-legacy.md` con fecha, responsable, alcance real revisado, nombres y versiones de configuración, acción realizada, revisión desplegada y resultado de validación. Distinguir una declaración del responsable de una prueba técnica. Cambiar las claves Gemini/OpenAI no acredita rotación de la contraseña admin. El código actual ya no usa la clave JWT ni registra las rutas antiguas; esto limita su utilidad en la revisión comprobada, pero no acredita todos los servicios o copias.

La limpieza del historial es una decisión separada con docente/equipo: respaldo, inventario de ramas/tags/referencias, reescritura coordinada y actualización de clones. No usar `.gitleaksignore` para esconder el hallazgo ni ejecutar force push sin coordinación.

## 3. Ejecutar la evaluación final comparable

En GitHub Settings → Secrets and variables → Actions, configurar `GEMINI_API_KEY` y `OPENAI_API_KEY`. Los secretos de Cloud Run no pasan automáticamente a Actions; `AI_API_KEY` no sustituye esos nombres.

En Actions → **Evaluación final sin despliegue** → Run workflow, seleccionar main. Este workflow consume API pero no despliega. Descargar el artefacto `evaluacion-final-<SHA>` y versionar sus tres reportes `results-final-comparacion.json`, `results-final-chat.json` y `results-final-agente.json`, si fueron producidos. Conservar errores y resultados parciales si falla. Comparar en `docs/07-evaluacion.md` con semana 3: mismo golden set, recuperación léxica/híbrida, citas/abstención y criterio estricto del agente; anotar modelos y diferencias de configuración/corpus.

El último 5/6 estricto del agente no pasa a 6/6 por tener 35/35 HTTP. El instructivo OCR continúa sin aprobación completa humana; revisar normativa con responsable competente o declarar esa limitación. No aprobar fuentes ni rebajar criterios para maquillar el resultado.

## 4. Reducir el paquete: propuesta medida, todavía no aplicada

Medición de la base: **28.727.410 bytes (27,40 MiB)**. El máximo del empaquetador es **20.000.000 bytes**, no 20 MiB. Faltan reducir al menos 8.727.410 bytes. El corpus comprimido por sí solo supera los 20 MB; eliminar únicamente capturas no resuelve el límite.

| Archivo | Original, bytes | Copia experimental, bytes | Tratamiento |
| --- | ---: | ---: | --- |
| Instructivo de seguimiento a graduados | 8.347.923 | 4.527.812 | Ocho imágenes grandes reducidas a 50 % de ancho/alto, JPEG calidad 50; 72 páginas. |
| Instructivo de titulación 2017 | 8.850.203 | 3.121.159 | 29 imágenes reducidas a 50 % de ancho/alto, JPEG calidad 50; 29 páginas. |
| Avatar WebP | 1.695.730 | 232.260 | WebP calidad 85, mismas dimensiones y canal alfa; colores con pérdida. |

Al sustituir esos tres contenidos **solo en una medición temporal**, manteniendo ambas presentaciones y el resto de archivos permitidos, el ZIP resultó **18.909.976 bytes (18,03 MiB)**. Hay aproximadamente 1,09 MB de margen antes de incorporar nuevos reportes. El ZIP experimental fue eliminado: no es un entregable porque su manifiesto todavía correspondía a originales. La evidencia de la propuesta está en [el reporte JSON](evidencias/semana-4/propuesta-compresion-2026-11-08.json).

Se usaron PyMuPDF 1.28.2 y Pillow 13.0.0: extracción de imágenes JPEG/PNG con al menos 300.000 píxeles, conversión RGB, reducción LANCZOS, JPEG optimizado, reemplazo solo si ocupa menos, guardado PDF con limpieza de objetos y DEFLATE. Se conservaron originales en Git y las copias experimentales en `tmp/compresion-revision/`. No son archivos versionados ni se descargan al clonar la rama. El avatar conserva el alfa, pero la igualdad del alfa no significa igualdad de todos los píxeles.

**Qué falta para aplicar:** revisar visualmente todas las páginas, especialmente artículos, tablas, notas y numeración, comparando con originales. La igualdad del texto extraído y del número de páginas es un control parcial: el PDF de titulación tiene texto extraíble vacío tanto antes como después, por lo que esa igualdad no acredita legibilidad. No modificar el PDF con firma detectada `Reglamento-de-Regimen-Academico.pdf`.

Si las copias son aceptables, conservar originales oficiales fuera del ZIP con procedencia verificable y registrar la transformación. Actualizar SHA-256 en `data/raw/manifest.json`. Para el instructivo OCR no basta cambiar el hash: revisar/regenerar y validar su asociación con la copia derivada, conservar la procedencia del original, y actualizar el hash del sidecar en el manifiesto. Mantener `approved=false` hasta revisión humana completa. Repetir ingesta aislada, evaluación y pruebas; revisar diferencias de fragmentos/citas. Una alternativa si la calidad no basta es acordar con el docente fuentes oficiales externas descargables y verificadas por hash, lo que requiere implementar descarga reproducible y revisar Docker/ingesta; no quitar PDFs sin reemplazar ese flujo.

### Qué eliminar y qué conservar

- Dependencias, cachés, `.git`, logs, bases locales y `.env` privados ya quedan excluidos por el empaquetador. Borrarlos del disco no reduce el ZIP de archivos versionados.
- Solo se encontraron tres copias idénticas pequeñas de reportes de flujo de semana 3 (2.538 bytes cada una). Suprimir dos apenas ahorra unos 5 KB antes de compresión; no compensa romper referencias de evidencia histórica.
- Conservar pruebas, reportes fallidos fechados, OCR y fuentes mientras sean requeridos por la ingesta o evaluación. Un reporte antiguo fallido documenta un corte, no implica que producción actual falle.
- `docs/Presentacion.pdf` y `docs/presentacion-entrega4.pdf` tienen contenidos diferentes. El equipo confirmó que utilizó **`docs/Presentacion.pdf` (10 páginas con infografías)** en la sustentación. Conservarlo como presentación final; el PDF de seis diapositivas es material anterior. La propuesta medida no necesita borrar ninguna. El intento de recomprimir la presentación de diez páginas aumentó su tamaño y fue descartado.

Después de aplicar y validar una optimización, con archivos nuevos legítimos añadidos al índice de Git y desde la raíz:

```powershell
python scripts/check_secrets.py
python scripts/empaquetar_entrega.py --medir --report tmp/paquete-informe.json
$LASTEXITCODE
# Solo si la medición devuelve exit 0 y el contenido fue revisado:
python scripts/empaquetar_entrega.py --output tmp/Titulacion_Semana4.zip
$LASTEXITCODE
```

El paquete debe corresponder al contenido final de GitHub. No subir el ZIP a Git. No cambiar el límite del script para hacer pasar la entrega. Volver a medir después de añadir evidencias.

## 5. Completar documentación con hechos reales y abrir el PR

Registrar comentarios reales del tribunal en `docs/evidencias/semana-4/observaciones-sustentacion.md`, con responsable, acción, commit y evidencia. La presentación usada ya está identificada por el equipo: `docs/Presentacion.pdf` (10 páginas con infografías). Añadir el vídeo de respaldo si falta. Las responsabilidades, herramientas de IA y ejecución local/PR/pruebas comunes ya están declaradas en README; quedan ejemplos concretos de tareas revisadas y enlaces de PR por integrante si el equipo los aporta. No inventar observaciones ni autorías.

Revisar `git status` y `git diff`; añadir únicamente reportes y documentos revisados. Crear el commit, publicar `docs/evidencias-finales` y abrir PR a main. Esperar sus comprobaciones. Al fusionarlo, el despliegue automático se vuelve a verificar con el SHA correspondiente; un reporte anterior conserva su alcance fechado.

## ¿Qué pendiente exige código?

Los ejecutores HTTP, empaquetador y workflow de evaluación ya existen. Lo inmediato es ejecutarlos y guardar evidencia. La compresión requiere transformar archivos, ajustar trazabilidad/hashes/OCR y validar ingesta; no exige cambiar la lógica del chatbot si preserva el corpus. Solo la alternativa de sacar fuentes fuera del ZIP exige implementar un flujo de descarga verificable. La rotación/IAM y el acuerdo sobre historial son actuaciones operativas. Ninguna de estas tareas se considera cumplida por fusionar este documento.

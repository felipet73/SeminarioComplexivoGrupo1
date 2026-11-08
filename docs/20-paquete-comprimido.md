# Paquete comprimido para revisión final

Se sustituyen dos PDF por copias derivadas con imágenes reducidas y el avatar por un WebP de menor tamaño. Se conservan ambas presentaciones y todas las fuentes/documentos. La transformación es **con pérdida**, no una mejora de contenido ni una aprobación normativa. Esta rama se prepara para revisión visual del equipo antes del merge.

## Archivos y procedencia

| Archivo | Antes | Después | Transformación |
| --- | ---: | ---: | --- |
| Instructivo seguimiento a graduados | 8.347.923 bytes | 4.527.812 bytes | Ocho imágenes grandes; 72 páginas conservadas |
| Instructivo titulación 2017 | 8.850.203 bytes | 3.121.159 bytes | 29 imágenes; 29 páginas conservadas |
| Avatar del frontend | 1.695.730 bytes | 232.260 bytes | WebP calidad 85, dimensiones y alfa conservados; colores con pérdida |

Los PDF originales siguen recuperables en el commit `16081c8224ba07d1b0b917f89266f6bb562fb0e5`; no se reescribe el historial. Sus SHA-256 y los de los derivados constan en [el reporte de transformación](evidencias/semana-4/compresion-aplicada-2026-11-08.json) y en `data/raw/manifest.json`, campo `derivation`. Los archivos conservan sus nombres para no romper referencias. Son copias derivadas de las fuentes, no nuevos originales oficiales.

El PDF con firma digital detectada `Reglamento-de-Regimen-Academico.pdf` permanece idéntico en bytes. No se retiran fuentes del corpus, no se cambia su aprobación/vigencia y no se modifica la lógica del chatbot.

## Método y OCR

Se usaron PyMuPDF 1.28.2 y Pillow 13.0.0: para imágenes JPEG/PNG de al menos 300.000 píxeles, conversión RGB, reducción LANCZOS al 50 % de ancho/alto y JPEG optimizado de calidad 50. Solo se reemplazaron streams que resultaron menores; se guardó cada PDF con limpieza de objetos y DEFLATE. No se rasterizaron las páginas de texto. El detalle visual disminuye; esta transformación no debe aplicarse a documentos firmados.

Se comprobó igualdad de texto extraído de **todas las páginas** con PyMuPDF y con pypdf, el extractor de la aplicación. En el PDF escaneado el texto extraíble está vacío antes y después: ese control no acredita legibilidad. Se compararon visualmente como muestra las páginas 5, 8 y 20 del instructivo y 11, 31 y 61 del seguimiento: artículos, formularios y tablas legibles en la muestra. Falta la revisión visual completa por el equipo; no se presenta como realizada ni como aprobación humana del OCR.

El OCR **no se regeneró** ni corrigió: su lista de 29 páginas/textos permanece idéntica. El campo `original_sha256`, requerido por la ingesta, se vincula al PDF derivado que ahora se ingiere. Se conserva explícitamente `ocr_source_sha256` con el hash del PDF del que se obtuvo realmente el OCR, más `pdf_derivation` y el commit de origen. No se atribuye al OCR una ejecución sobre el derivado. Se actualiza también el hash del sidecar en el manifiesto. `review_status=pending_full_human_review` y `approved=false` se mantienen.

## Validación local y límites

- Ingesta aislada léxica: 1.047 fragmentos totales, igual al corpus anterior; 86 corresponden al instructivo no aprobado y no quedan habilitados para respuestas por este cambio.
- Golden set léxico: 14/16 positivos, 4/4 negativos, cero errores; igual al baseline.
- Seis pruebas de integridad/ingesta/empaquetado aprobadas.
- Frontend: 18 pruebas y build aprobados.
- Texto OCR íntegro y estado de revisión sin cambios; PDF firmado intacto.
- El empaquetador debe devolver exit 0 con el contenido final. No incluir `.git`, dependencias, cachés, ZIP anteriores ni secretos locales; ya los excluye el script.

No se repitió la evaluación híbrida/generativa con proveedores en esta rama para volver a consumir cuota: el texto extraído y OCR se preservaron, y la evaluación completa previa acredita su propio SHA. Tras el merge, comprobar el despliegue y repetir el smoke público con el nuevo SHA antes de entregar. El CI conserva sus comprobaciones de contenedor/producción.

## Pasos del equipo

1. Revisar la legibilidad de ambos derivados completos, especialmente letra pequeña, artículos, tablas y numeración. La revisión del OCR es una actuación separada; no cambiar `approved` para pasar pruebas.
2. Esta rama integra también la evidencia del PR #29 para medir el paquete con la evaluación aprobada incluida. Puede fusionarse primero #29 y, después de revisar los derivados y CI, este PR de compresión. El paquete final debe contener ambos cambios.
3. Actualizar main local, esperar su despliegue, repetir las pruebas públicas con su SHA y conservar el reporte final con nombre propio.
4. Con archivos legítimos conocidos por Git y secretos revisados, ejecutar desde la raíz:

```powershell
python scripts/check_secrets.py
python scripts/empaquetar_entrega.py --medir --report tmp/paquete-final-informe.json
$LASTEXITCODE
# Si devuelve 0, crear un archivo nuevo:
python scripts/empaquetar_entrega.py --output tmp/Titulacion_Semana4-final.zip
$LASTEXITCODE
```

No subir el ZIP al repositorio. Volver a medir después de agregar evidencias, porque el máximo es **20.000.000 bytes**, no 20 MiB. La medición de esta rama se conserva como reporte temporal local; el ZIP de entrega debe generarse desde el main final limpio.

Para recuperar un original sin alterarlo mediante redirecciones de PowerShell, desde Python usar `subprocess.check_output(['git', 'show', '<commit>:data/raw/<archivo>'])` y escribir esos bytes con `Path(...).write_bytes(...)` en una carpeta fuera del paquete; verificar su SHA con el reporte. Requiere tener disponible aquel objeto Git. No mantener copias originales duplicadas en el ZIP final.

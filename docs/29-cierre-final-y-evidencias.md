# Cierre de entrega: main, evidencia pública y tareas del propietario

Corte documental: 10 de noviembre de 2026, Ecuador. Base revisada: `ab21d853186ba34acfe8359553a8d38a39de1f80`. Las ejecuciones posteriores deben identificarse con su propio SHA; no se modifica la fecha o revisión de reportes antiguos.

## Contraste de pendientes

| Punto | Estado comprobado / siguiente acción |
| --- | --- |
| Último despliegue main | API GitHub: Actions **42494812366**, SHA **ab21d85**, conclusión success; pasos de smoke y casos públicos aprobados. [Metadatos](evidencias/semana-4/cierre-main-ab21d85/actions-metadata.json). |
| JSON público completo | El artefacto `evidencias-despliegue-ab21d853186ba34acfe8359553a8d38a39de1f80` existe, no expirado al consultar; **JSON completo incorporado**, descargado y adjuntado por el propietario tras Forbidden desde este entorno. [35/35, sin omitidos, SHA coincidente](evidencias/semana-4/produccion-ab21d85-run-42494812366.json). Los metadatos se complementan ahora con los casos. |
| Conteo backend y presentación | Corregidos docs/08 y docs/11 a **147**; s4j identifica **docs/Presentacion.pdf**, diez páginas, versión usada según el equipo. No se inventa medición de duración. |
| Historial GitHub | Las 25 refs de la solicitud siguen publicadas y `3e38895` responde en la API. No se recuperaron ni imprimieron sus valores. Solicitud de docs/25 **enviada por el propietario, caso #4985701, abierto y pendiente de actuación** según capturas aportadas posteriormente. JWT retirado, no rotado; forks/clones externos no purgados. |
| Persistencia y despliegue | Comparación Neon entre revisiones aprobada y JSON versionados. CI ahora declara `RAG_DATABASE_URL=rag-database-url:1` con merge y verifica referencia sin consultar el valor. Se aplicará tras merge/despliegue, no antes. Sesiones/métricas/rate limit siguen por proceso. |
| Artículo 24 | Corrección/reindexación remota reportadas por el operador y capturas observadas; 87 fragmentos y fuente artículo 24/página 9/revisión 2. Falta el archivo original de captura o JSON remoto versionado si se exige evidencia autónoma. No se trata como bug todavía sin corregir. |
| Corpus/OCR | Git conserva `approved=false` para el instructivo; panel remoto aprobado según el equipo y sus respuestas. Esa divergencia se documenta, no se igualan políticas sin revisión. **\* Debe analizarse el improvement** de ADR-0005; revisión integral y vigencia no acreditadas. |
| Configuración híbrida | 16/16 acreditado para OpenAI `text-embedding-3-small`/0,55. No se extrapola a Gemini/0,65 ni al estado actual del panel. Nueva configuración requiere su propia evaluación. |
| Evidencia humana | Instalación en diez minutos sin medición; observación de sustentación declarada por equipo, sin acta/fecha exacta aportada. Capturas de rotación/tráfico/chat vistas en conversación no están disponibles como archivos originales en el checkout. No se fabrican fechas ni imágenes. |
| Paquete main revisado | Worktree limpio, empaquetador exit 0: **19.096.731 bytes** (<20.000.000), SHA y hash del ZIP registrados en [reporte](evidencias/semana-4/cierre-main-ab21d85/paquete-main.json). Repetir después de fusionar cambios. |
| Portal | Subida/acuse **no realizados desde este entorno**. El propietario debe subir un solo ZIP del main final, con el código del grupo, máximo 20 MB. Plazo comunicado: miércoles 11 de noviembre de 2026, **23:59 Ecuador**. |

## 1. JSON completo incorporado; procedimiento de descarga para futuras corridas

El propietario ya aportó el reporte de esta ejecución y se incorporó íntegro tras validar SHA y 35 casos. No necesita repetir estos pasos para ab21d85. Se conservan como referencia para recuperar otra ejecución.

En GitHub: [ejecución 42494812366](https://github.com/felipet73/SeminarioComplexivoGrupo1/actions/runs/42494812366) → Summary → Artifacts → `evidencias-despliegue-ab21d853186ba34acfe8359553a8d38a39de1f80`. Extraer `results-produccion-funcional.json`. No guardar el ZIP de artefacto en la entrega.

También se puede usar GitHub CLI desde el computador del propietario:

```powershell
gh run download 42494812366 --repo felipet73/SeminarioComplexivoGrupo1 --name evidencias-despliegue-ab21d853186ba34acfe8359553a8d38a39de1f80 --dir tmp/artefacto-ab21d85
```

Validar el archivo antes de copiarlo (el ejemplo espera que esté en la raíz de ese directorio):

```powershell
$origen = "tmp/artefacto-ab21d85/results-produccion-funcional.json"
$informe = Get-Content -Raw $origen | ConvertFrom-Json
$shaEsperado = "ab21d853186ba34acfe8359553a8d38a39de1f80"
if ($informe.revision_esperada -ne $shaEsperado -or
    $informe.correctos -ne 35 -or $informe.total -ne 35 -or
    $informe.casos.Count -ne 35 -or $informe.omitidos.Count -ne 0 -or
    !$informe.incluye_modelo -or $informe.solo_backend -or
    @($informe.casos | Where-Object { !$_.ok }).Count -ne 0) {
    throw "El archivo no acredita los 35 casos completos del SHA esperado. No versionarlo como aprobado."
}
```

Conservar el archivo completo, no el Select-Object del resumen. Revisarlo por secretos y versionarlo en una rama nueva, por ejemplo `docs/evidencias/semana-4/produccion-ab21d85-run-42494812366.json`, con referencia a ejecución/SHA en docs/08 y README. El JSON de `279580e` se mantiene histórico; su mapa tras la limpieza no lo convierte en una prueba nueva.

Después de fusionar cambios de despliegue/código, comprobar la ejecución del nuevo SHA. Para acreditar literalmente el main final, descargar su artefacto o ejecutar `scripts/pruebas_funcionales.py --expected-revision SHA_FINAL --incluir-modelo --output RUTA_JSON`. El mismo runner puede consumir generación y embeddings según la configuración del panel. No relanzar toda la infraestructura solo para renombrar evidencia anterior ni atribuir reportes de otro SHA al final.

## 2. Solicitud a GitHub Support

El propietario aportó confirmación de envío y listado de tickets: **#4985701**, prioridad Normal, abierto. Dar seguimiento desde su cuenta y registrar respuesta/resultado en [docs/25](25-solicitud-soporte-github.md). La captura no muestra fecha/hora absoluta; completar ese dato desde el correo cuando se disponga. El asistente registró la evidencia, no realizó el envío. No publicar bundle privado ni valores. No marcar purga cerrada hasta respuesta y verificación de refs/commit; copias externas siguen fuera del alcance.

## 3. Corpus y evidencias humanas

No cambiar `approved=false` a true en Git para reflejar mecánicamente una aprobación hecha en el panel sin revisión. Registrar quién aprobó en remoto, con qué alcance y en qué fecha cuando se conozca; si no existe sustento de revisión, el equipo debe decidir retirar/excluir su uso normativo hasta revisarlo. ADR-0005 propone facilitar la revisión futura, no acredita la actual ni crea un bloqueo automático nuevo.

Para evidencia autónoma, aportar imágenes originales ligeras o un JSON de consulta revisado por secretos. No se incorporan capturas reconstruidas ni vídeos pesados. Un ensayo de instalación debe registrar persona, entorno, hora de inicio/fin, comandos y resultado real; no se rellena «10 minutos» sin haberlo medido.

## 4. Generar y subir el único ZIP final

Desde un clon limpio posterior a la limpieza histórica, con main actualizado y sin cambios pendientes:

```powershell
git switch main
git pull --ff-only
git status --short
$archivoZip = "tmp/Titulacion_Grupo1_$(Get-Date -Format yyyyMMdd-HHmmss).zip"
python scripts/empaquetar_entrega.py --output "$archivoZip"
if ($LASTEXITCODE -ne 0) { throw "El paquete no cumple; no subirlo." }
Get-FileHash "$archivoZip" -Algorithm SHA256
explorer.exe tmp
```

El empaquetador usa archivos rastreados y excluye secretos/estados/cachés, `.env`, `.venv`, `node_modules`, `__pycache__`, Terraform privado y respaldos. Evitar bundles privados dentro del proyecto. Revisar tamaño exacto ≤20.000.000 bytes y contenido; subir solo el ZIP generado al portal con el código real del grupo. Conservar acuse, hora Ecuador, SHA y hash del paquete. No hay constancia de entrega hasta recibir ese acuse.

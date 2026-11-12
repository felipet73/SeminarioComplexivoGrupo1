# Cierre de entrega: main, evidencia pública y tareas del propietario

**Corte vigente acreditado: main `2e0bf2d68b7ecf8a4557da3890bd235990010a86`, Actions 42939713143, LISTO PARA SUBIDA**. La API confirma despliegue, prueba pública, empaquetado y publicación. [Estado completo y metadatos](31-estado-verificado-final.md). Los reportes ab21d85 y 8d35347 se conservan como históricos; no son las cifras del ZIP final ni la única evidencia de CI.

## Contraste vigente

| Punto | Estado / evidencia |
| --- | --- |
| Despliegue main acreditado | **2e0bf2d / Actions 42939713143, success**; pasos Neon, smoke, casos públicos, empaquetado y upload aprobados. [JSON de API](evidencias/semana-4/main-2e0bf2d/actions-verificado.json). |
| JSON público | El corte 2e0bf2d se incorpora al ZIP por el mismo job; el archivo original está en Actions, no descargado por este entorno (Forbidden). El JSON completo ab21d85 sí está versionado y conserva su fecha. No se confunden repositorio y artefacto. |
| Paquete final | **Generado en Actions**, artefacto 13820491498 `entrega-final-2e0bf2d…`; límite validado por el paso. Tamaño/digest de API corresponden al contenedor de GitHub, no al ZIP interior; bytes/hash interiores están en `paquete-final.json`. |
| Tests y presentación | **154 tests locales** con XML/procedencia explícitos; además backend/pytest de CI aprobado sobre 2e0bf2d. `docs/Presentacion.pdf` es la versión usada, diez páginas, según equipo. |
| Support | Caso **#4985701 enviado**, acuse visible **10/11/2026 19:42**, zona no mostrada; no respuesta técnica aportada ni retirada certificada. Siguen 25 refs publicadas y commit antiguo accesible. |
| Instalación humana | Los tres integrantes reinstalaron desde copias limpias; aprox. seis minutos estimados, sin cronómetro, según representante. No se inventan fechas/SO/SHA por sesión ni persona ajena. Medición automatizada 51,633 s es otra prueba sobre 8d35347. |
| PDF/OCR | Calidad/fidelidad del insumo a cargo del cliente; OCR no implementado ni dentro del alcance. Improvement asistido por analizar. Semilla Git `approved=false` y aprobación administrativa remota son estados diferentes; no se presenta como revisión integral acreditada. |
| Artículo 24 | Causa corregida y uso remoto correcto confirmado por operador. Falta archivo primario versionado de esa captura/consulta si se exige; no se dice que la corrección siga sin aplicar. |
| Híbrido | 16/16 pertenece a OpenAI/0,55; no se atribuye a Gemini/0,65 ni al panel remoto. Sesiones/métricas/rate limit siguen por proceso. |
| Portal | **Listo para subida**, no ya entregado. Subir únicamente ZIP interior renombrado según docente; no JSON por separado. El acuse se registra después y no es condición previa de este estado. |

Los archivos `paquete-main.json` e `integracion-zip-con-evidencia.json` miden ab21d85, no el ZIP de 2e0bf2d. No se alteran sus bytes/SHA históricos. La ausencia de un binario descargado aquí no significa que el artefacto no exista: los pasos y su ID se verificaron por API.


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

El propietario aportó confirmación de envío y listado de tickets: **#4985701**, prioridad Normal, abierto. Dar seguimiento desde su cuenta y registrar respuesta/resultado en [docs/25](25-solicitud-soporte-github.md). El acuse por correo muestra 10/11/2026 19:42; zona horaria no visible. Esa confirmación no es respuesta técnica. El asistente registró la evidencia, no realizó el envío. No publicar bundle privado ni valores. No marcar purga cerrada hasta respuesta y verificación de refs/commit; copias externas siguen fuera del alcance.

## 3. Corpus y evidencias humanas

No cambiar `approved=false` a true en Git para reflejar mecánicamente una aprobación hecha en el panel sin revisión. Registrar quién aprobó en remoto, con qué alcance y en qué fecha cuando se conozca; si no existe sustento de revisión, el equipo debe decidir retirar/excluir su uso normativo hasta revisarlo. ADR-0005 propone facilitar la revisión futura, no acredita la actual ni crea un bloqueo automático nuevo.

Para evidencia autónoma, aportar imágenes originales ligeras o un JSON de consulta revisado por secretos. No se incorporan capturas reconstruidas ni vídeos pesados. La instalación del equipo ya está [confirmada](evidencias/semana-4/instalacion-equipo.md): aprox. seis minutos estimados, sin cronómetro. No se rellenan horas de inicio/fin ni un tiempo exacto no medidos.

## 4. Obtener y subir el único ZIP final

**Opción acreditada:** descargar el artefacto `entrega-final-SHA` de Actions, extraerlo, cotejar `paquete-final.json`, renombrar únicamente el ZIP interior como exige el docente y subir ese archivo. [Pasos y límites](31-estado-verificado-final.md). No subir JSON por separado ni el contenedor de Actions.

**Alternativa de empaquetado local, no la fuente del artefacto ya generado:**

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

El empaquetador usa archivos rastreados y excluye secretos/estados/cachés, `.env`, `.venv`, `node_modules`, `__pycache__`, Terraform privado y respaldos. Evitar bundles privados dentro del proyecto. Revisar tamaño exacto ≤20.000.000 bytes y contenido; subir solo el ZIP generado al portal con el código real del grupo. Conservar acuse, hora Ecuador, SHA y hash del paquete. El estado listo para subida se acredita antes del acuse; el acuse solo confirma la entrega posterior.

## Ampliación de cierre automatizable

Main 8d35347 aprobó Actions 42934948121, incluida la referencia declarada Neon. La instalación limpia automatizada pasó en 51,633 s, sin atribuir ensayo a una persona. La ampliación del empaquetador produce tras CI un ZIP con JSON de los 35 casos del mismo SHA, evitando otro commit que vuelva a cambiar la revisión. [Guía vigente para obtener el entregable y pendientes humanos](30-paquete-final-e-instalacion.md).

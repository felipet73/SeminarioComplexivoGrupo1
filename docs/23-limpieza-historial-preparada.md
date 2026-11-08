# Limpieza de credenciales históricas: preparación y publicación

**Actualización del 8/11/2026 (Ecuador):** la preparación descrita abajo se completó y se publicaron 27 ramas con autorización y respaldo previo. Main `2482401` pasó detectores, CI y despliegue. Las refs de PR y cachés siguen pendientes; ver [constancia vigente](24-cierre-historial-publicado.md). El resto de este documento conserva el procedimiento previo, no afirma que la publicación siga sin realizarse.

Se preparó una simulación en dos copias espejo locales privadas, fuera del repositorio y del ZIP. Se aplicó `git filter-repo --path backend/app/seguridad.py --invert-paths` **solo a la copia filtrada**. No se imprimieron valores, no se modificó el checkout y no se publicó un force push.

[Reporte de simulación](evidencias/semana-4/simulacion-historial-legacy-2026-11-08.json): base remota `f653a71`, refs disponibles localmente; el archivo desaparece de todas las referencias de esa copia. La herramienta normaliza referencias remotas a ramas locales y cambia identificadores. El conteo es de refs locales disponibles, no un inventario completo del servidor GitHub. La copia privada de respaldo conserva el historial sensible y no se adjunta como evidencia pública.

Esto **no cierra el requisito de historial limpio** de GitHub. Antes de publicarlo:

1. Finalizar/coordinar PR abiertos y acordar el momento con todos los integrantes/docente. Registrar ramas, tags y refs de PR accesibles. Realizar una copia espejo **nueva desde GitHub**, no publicar esta simulación parcial ni una copia anterior a los últimos cambios.
2. Conservar un respaldo privado recuperable fuera del equipo efímero de este chat. Revocación/rotación y retirada de endpoints se mantienen como actuaciones independientes: una reescritura no las sustituye.
3. Filtrar la ruta en una copia, revisar qué referencias/cambios se eliminarán y verificar que no quedan valores en otros archivos. No añadir exclusiones de Gitleaks para ocultarlos.
4. Preparar mapa de SHA antes/después y revisar referencias documentales/evidencias: los reportes antiguos siguen acreditando sus SHA originales, pero algunos enlaces pueden dejar de resolver. No reetiquetar reportes de ejecuciones que nunca probaron el SHA nuevo.
5. Solicitar autorización explícita para publicar el conjunto concreto de ramas/tags y coordinar protecciones de rama. Usar comprobaciones de leases contra los SHA remotos inventariados para no pisar trabajo nuevo. **No ejecutar `push --mirror` indiscriminado**, que puede intentar borrar o modificar referencias ajenas/read-only.
6. Tratar refs de PR, caches y vistas de objetos antiguos con el procedimiento de GitHub y, si corresponde, soporte. Indicar a cada integrante cómo reemplazar su clon sin reintroducir commits antiguos.
7. Repetir detector histórico/activo, CI, despliegue, SHA y pruebas públicas. Conservar constancia de lo eliminado, respaldo privado y limitaciones sobre forks/copias de terceros.

En el momento de la preparación, el repositorio aún contenía los valores en las ramas históricas señaladas. Las copias externas no se borran por modificar main. La publicación coordinada ya se completó después de esa simulación; queda la gestión de referencias internas/cachés y copias externas.

Guía oficial: [Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

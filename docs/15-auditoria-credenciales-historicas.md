# Auditoría de credenciales históricas y exclusiones de Gitleaks

Fecha: 7 de noviembre de 2026. Código operativo comprobado: main `0dab82d`; despliegue aprobado en Actions 42378740379, intento 2. Análisis de objetos Git realizado sin imprimir, copiar ni probar valores secretos. La fuente del dictamen y posiciones se conserva en [JSON](evidencias/semana-4/auditoria-secretos-y-comite-2026-11-07.json).

## Respuesta: eran dos problemas diferentes

**Sí existieron falsos positivos y las seis exclusiones actuales son coherentes con ellos. Pero no son las credenciales de `seguridad.py`.** La contraseña y la clave de firma legacy fueron credenciales funcionales del código antiguo. No se confunden con claves Gemini/OpenAI ni con los tokens aleatorios del aviso de vulnerabilidad.

### 1. Los falsos positivos de .gitleaksignore

| Commit | Archivo y ubicación | Clasificación y motivo |
| --- | --- | --- |
| `869404be3b80e970866a0a3f969f3f67c2a40974` | `docs/evidencias/semana-3/auditoria-python.json`, línea 1; JSON `dependencies[17].vulns[8].description` | Un token de ejemplo de un PoC de `filelock 4.1.0`, advisory `CVE-2026-112934`, fue detectado como generic-api-key. Es texto técnico de terceros, no una clave operativa del proyecto. |
| `8f3369c90302695099ddeaf959ba706c3c9e90e2` | Mismo archivo y ruta JSON | El mismo ejemplo vuelve a aparecer al versionar el informe de pip-audit. |
| `a6b12a7e6d9d86d8776f1c115611b8d0ff9beb32` | `gitleaks-local.json`, líneas 9, 10, 30 y 31 | Los campos Match/Secret del reporte copian el texto detectado por los dos hallazgos anteriores. Son cuatro coincidencias derivadas del mismo advisory. |

Se comprobó por igualdad interna del texto que los cuatro registros derivados son las copias de esos ejemplos. No se reproduce el token aquí. Las exclusiones se introdujeron al incorporar Gitleaks y se ampliaron al versionar su propio informe (`a6b12a7` y `5221596`). La justificación se basa en el contenido observado, no solo en que alguien lo hubiera añadido a una lista de exclusión.

Ninguno de los seis fingerprints actuales de `.gitleaksignore` apunta a `backend/app/seguridad.py`, `1348b06` o `3e38895`. No se cambió esa lista para ocultar la credencial legacy. Gitleaks verde y detector AST histórico rojo no se contradicen: el primero puede no detectar contraseñas débiles de baja entropía que el segundo reconoce por uso en código.

### 2. Credenciales funcionales del módulo antiguo

| Commit | Fecha de Ecuador | Qué quedó versionado |
| --- | --- | --- |
| `1348b065feaba46b6dfea20bf26b1f7d8b455dc8` | 5 de noviembre, 15:25:44 | `SECRET_KEY` literal en línea 10; contraseña literal entregada a `pwd_context.hash(...)` en línea 20. Se incorpora autenticación JWT y registro de rutas administrativas. |
| `3e38895fff1e60d983b7bf43206e86d69c1be2c2` | 5 de noviembre, 16:17:16 | Los mismos usos en líneas 9 y 19; se corrige el import a `app.seguridad` y se mantienen las rutas. |

La clave se entregaba a `jwt.encode` y `jwt.decode`; la contraseña se usaba para construir el hash que validaba el login. Que una contraseña se transforme con bcrypt durante el arranque no elimina el literal que quedó en el archivo. El código registraba `/admin/login` y `/admin/recargar-reglamentos` y usaba esos valores para autenticar. Por ello no eran un comentario, un fixture aislado ni un simple token sin uso.

La evidencia remota anterior al despliegue (`credencial-antigua.json`) registró que la credencial histórica fue aceptada con HTTP 200. No se guardó el token ni se ejecutó una operación administrativa. Este dato contradice la hipótesis de que todo fuera un falso positivo. La cuenta y el mecanismo legacy no demuestran acceso al panel actual `/api/admin`.

### 3. Por qué estuvo y cómo se retiró

El mensaje de `1348b06` y la lógica del módulo muestran que se añadió para implementar autenticación JWT de dos rutas administrativas. Se emplearon valores fijos de configuración/demo dentro del código, en lugar de inyectarlos desde el servidor. No se atribuye intención, responsable humano o decisión no registrada.

En `9434e2d` (6 de noviembre, 16:19 Ecuador), `main.py` dejó de importar y registrar ese mecanismo, pero el archivo seguía versionado. En `08ef882` (6 de noviembre, 17:02 Ecuador) se eliminó el módulo. En `0dab82d` no existe el archivo ni el registro de las rutas antiguas.

### 4. Riesgo actual: explicación precisa

**Ya no autentican en la revisión y URL comprobadas:** el módulo no se importa, las rutas antiguas responden 404 en las pruebas públicas y la administración actual usa `ADMIN_PASSWORD` inyectada, cookie opaca y otro flujo; no consume el JWT antiguo. El despliegue probado es de SHA conocido. Por tanto la mera posesión de esos valores no permite usar aquel mecanismo en esa revisión.

**No se acredita riesgo cero en todos los lugares:** siguen accesibles en el historial. No se verificó si fueron reutilizados en otra aplicación, revisión etiquetada o secreto actual. Tampoco se reescribieron todas las referencias Git ni las copias de terceros. No son necesariamente claves de proveedor que puedan revocarse en Gemini/OpenAI: son una contraseña y una clave de firma del mecanismo antiguo.

Para cerrar la exposición residual: comprobar no reutilización (o cambiar los valores donde se reutilizaron), retirar URLs/revisiones antiguas aún accesibles y conservar constancia sin mostrar secretos. Para cumplir literalmente s4b del comité (“ninguna clave ... en el historial”) además hace falta coordinar limpieza de todas las referencias afectadas. Añadir estos valores a `.gitleaksignore` no cumpliría el requisito.

Una reescritura requiere inventario de ramas/tags, respaldo seguro, coordinación del equipo, tratamiento de referencias de PR/cachés y publicación forzada expresamente autorizada. No se ha ejecutado: cambia identificadores de commits y afecta clones, PR y evidencias. La documentación registra el pendiente en lugar de simular que ya está limpio.

## Conclusión para el comité

Las exclusiones del advisory son falsos positivos justificados; las credenciales legacy fueron reales en su contexto operativo y se retiraron del código y servicio comprobados. El aviso rojo debe actualizarse para distinguir la corrección desplegada del historial pendiente. Se puede acreditar la retirada del mecanismo, pero no la frase absoluta “nunca hubo credenciales” ni “historial limpio” hasta completar la remediación coordinada.

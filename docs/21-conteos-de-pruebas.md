# Conteos de pruebas: corte actual y evidencias históricas

## Último corte: TLS Neon

La preparación TLS añade dos instancias de prueba sin eliminar casos: **132 aprobadas, cobertura de app 89,11 %**, cero fallos/errores/omitidos. [XML y resumen](evidencias/semana-4/tls-neon/). Se simula el driver para verificar CA predeterminada y respeto a CA explícita; no se afirma haber conectado al Neon del equipo. El corte de 130 y su cobertura se conservan abajo como resultado histórico anterior.

## Corte anterior: preparación PostgreSQL

En la rama de preparación PostgreSQL sobre main **`f653a71`**, se ejecutó la suite completa: **130 aprobadas, cero fallos, errores u omitidas**, cobertura de **`app` 89,09 %**, superior al umbral 85 %. [XML, resumen y pruebas de persistencia](evidencias/semana-4/preparacion-postgres/). Son cambios de aplicación preparados, sin activar Cloud SQL, no un nuevo job remoto. Las claves y proveedores se aíslan.

El corte anterior sobre `7b19cf3` acreditó 112 aprobadas y 88,84 %; se conserva en [su XML y resumen originales](evidencias/semana-4/2026-11-08-conteo-pruebas/). La evolución es **99 → 104 → 105 → 110 → 112 → 130 → 132**.

```bash
python -m pytest -q backend/tests --cov=app --cov-fail-under=85 --cov-report=json:tmp/cobertura-conteo.json --junitxml=eval/tests-backend.xml
```

Este es un resultado local nuevo, no un job remoto ni prueba de carga. El porcentaje se refiere a `app`, como exige CI; no mezclarlo con el 87,44 % de una ejecución anterior con `--cov` sin limitar el ámbito, que incluyó tests/scripts/evaluadores.

## Por qué aparecen 99, 104 y 105

| Corte | Evidencia | Cambios que explican el siguiente conteo |
| --- | --- | --- |
| 99 | `evidencias/semana-4/pytest-linux.xml`; timestamp 7/11/2026 04:02:10 UTC; incorporado a Git en `c7e2422` | +4 casos de contratos HTTP y +1 del lector SSE en `5ce60b9` → 104 |
| 104 | `evidencias/semana-4/complemento-revision-2026-11-07.json`, 7/11/2026 12:38:50 UTC; declara cambios locales sobre base `7476e3f` | +1 prueba del empaquetador en `4fd7ade` → 105 |
| 105 | `evidencias/semana-4/metricas-permisos-2026-11-07.json`, reporte fechado 7/11/2026 | +5 instancias parametrizadas de diagnóstico seguro en `4d90eaf` → 110 |
| 110 | Incremento verificable en el código; no se inventa un reporte histórico de 110 | +2 controles de ritmo/reintentos en `d5cca81` → 112 |
| 112 | XML y resumen locales sobre `7b19cf3` | Corte anterior: se agregan 18 instancias para adaptador PostgreSQL, backup, transporte/error seguro y detector de DSN → 130 |
| 130 | XML y resumen de preparación PostgreSQL sobre `f653a71` | Corte anterior local; cero casos eliminados respecto a 112 |
| 132 | XML y resumen de rama TLS Neon | Último corte local: dos instancias nuevas de CA predeterminada/explícita, sin eliminar casos |

Al comparar los XML históricos de 99 y 112 mediante `(classname, name)`, **ninguno de los 99 casos antiguos desapareció**, y aquel corte añadió exactamente **13 casos**. El nuevo corte 130 añade otros **18 respecto a 112**, sin eliminar ninguno; la lista está en el resumen de preparación PostgreSQL. El resumen contiene sus nombres. Los tests parametrizados cuentan como varias instancias ejecutadas, no como una única función Python.

No se edita un XML histórico de 99 para decir 112, ni se cambia el reporte de métricas de 105: ambos documentan lo observado en su momento. Las referencias actuales de README/checklist apuntan al nuevo corte; los documentos históricos conservan su fecha. Que una evidencia se incorpore en un commit no demuestra por sí solo que su ejecución probara ese mismo SHA; se distingue commit de incorporación de commit base declarado.

## Conjuntos que no deben sumarse

- Backend: 132 instancias pytest; los tests automatizados de contratos HTTP dentro de pytest usan dobles y forman parte de ese conteo.
- Frontend: 18 tests Vitest según su evidencia; conjunto independiente.
- Navegador: 10 escenarios Playwright según su evidencia; conjunto independiente.
- Producción: 35 casos públicos ejecutados contra URLs; no son 35 tests adicionales de la suite pytest.
- Evaluación: 20 preguntas, comparación de recuperadores y seis casos reales de agente; conjunto de calidad/IA independiente, sin equivalencia con cobertura de código.

El resultado de una suite no acredita por sí solo los otros conjuntos. Conservar sus SHA, fechas, entornos y reportes separados.

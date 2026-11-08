# Conteos de pruebas: corte actual y evidencias históricas

## Resultado vigente

Sobre el código de main **`7b19cf3`**, en una rama con cambios documentales, se ejecutó localmente la suite completa: **112 aprobadas, cero fallos, errores u omitidas**, cobertura de **`app` 88,84 %**, superior al umbral 85 %. [XML completo y resumen verificable](evidencias/semana-4/2026-11-08-conteo-pruebas/). La fecha exacta, commit base, comando y hash del XML están en `resumen.json`. No se hicieron llamadas reales a proveedores; los fixtures aíslan claves y simulan esos clientes.

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
| 112 | Nuevo XML y resumen locales sobre `7b19cf3` | Corte actual acreditado |

Se compararon identificadores `(classname, name)` de ambos XML completos: **ninguno de los 99 casos antiguos desapareció**, y hay exactamente **13 casos adicionales**. El resumen contiene sus nombres. Los tests parametrizados cuentan como varias instancias ejecutadas, no como una única función Python.

No se edita un XML histórico de 99 para decir 112, ni se cambia el reporte de métricas de 105: ambos documentan lo observado en su momento. Las referencias actuales de README/checklist apuntan al nuevo corte; los documentos históricos conservan su fecha. Que una evidencia se incorpore en un commit no demuestra por sí solo que su ejecución probara ese mismo SHA; se distingue commit de incorporación de commit base declarado.

## Conjuntos que no deben sumarse

- Backend: 112 instancias pytest; los tests automatizados de contratos HTTP dentro de pytest usan dobles y forman parte de ese conteo.
- Frontend: 18 tests Vitest según su evidencia; conjunto independiente.
- Navegador: 10 escenarios Playwright según su evidencia; conjunto independiente.
- Producción: 35 casos públicos ejecutados contra URLs; no son 35 tests adicionales de la suite pytest.
- Evaluación: 20 preguntas, comparación de recuperadores y seis casos reales de agente; conjunto de calidad/IA independiente, sin equivalencia con cobertura de código.

El resultado de una suite no acredita por sí solo los otros conjuntos. Conservar sus SHA, fechas, entornos y reportes separados.

"""Casos HTTP reales con contratos estrictos, reporte y exit 1 ante fallos."""
import argparse
import json
import math
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verificar_produccion import consultar


def normalizar(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.casefold()) if not unicodedata.combining(c))


def cumple(caso, row, frontend, revision=None):
    if row.get('status') != caso['status']:
        return False
    if caso.get('content_type') and caso['content_type'] not in row.get('content_type', ''):
        return False
    if caso.get('cors') == 'permitido' and (row.get('allow_origin') != frontend or row.get('allow_credentials') == 'true'):
        return False
    if caso.get('cors') == 'denegado' and row.get('allow_origin') is not None:
        return False
    data = row.get('json', {})
    if not isinstance(data, dict):
        return False
    if any(data.get(k) != v for k, v in caso.get('json_igual', {}).items()):
        return False
    contrato = caso.get('contrato')
    if contrato == 'salud':
        return data.get('status') == 'ok' and bool(data.get('revision')) and (not revision or data['revision'] == revision)
    if contrato == 'ready':
        return data.get('status') == 'ready' and data.get('fragmentos_elegibles', 0) > 0
    if contrato == 'rechazo':
        return data.get('estado') == 'rechazo' and data.get('fuentes') == [] and bool(data.get('respuesta'))
    if contrato == 'rechazo_sse':
        return bool(row.get('sse_valido') and row.get('sse_estado') == 'rechazo' and row.get('sse_sin_fuentes'))
    if contrato == 'herramientas':
        return (set(data.get('permitidas', {})) == {'buscar_fragmentos','consultar_requisitos','calcular_plazo','generar_checklist','registrar_solicitud_tutor'}
                and 1 <= data.get('max_iteraciones', 0) <= 10 and data.get('requieren_ok') == ['registrar_solicitud_tutor'])
    if contrato == 'pasajes':
        items = data.get('pasajes', [])
        return bool(items) and all(p.get('fragmento_id') and p.get('seccion') and p.get('texto') and p.get('pagina', 0)>0 for p in items)
    if contrato == 'checklist':
        items = data.get('items', [])
        return (data.get('completo') is False and bool(items)
                and all(p.get('fragmento_id') and p.get('documento') and p.get('seccion') and p.get('pagina', 0)>0
                        and p.get('estado') == 'pendiente_de_verificar' for p in items))
    if contrato == 'respuesta_citada':
        if caso.get('content_type') == 'text/event-stream' and not row.get('sse_valido'):
            return False
        return bool(data.get('respuesta', '').strip() and data.get('modelo_utilizado')) and data.get('estado') == 'respuesta' and any(
            normalizar(f.get('titulo','')) == normalizar(caso['documento'])
            and re.search(r'\b'+re.escape(caso['articulo'])+r'\b', f.get('seccion',''))
            and f.get('fragmento_id') for f in data.get('fuentes', []))
    if contrato is not None:
        raise ValueError(f'Contrato desconocido: {contrato}')
    return True


def ejecutar(backend, frontend, *, casos=None, incluir_modelo=False, solo_backend=False, revision=None):
    if casos is None:
        casos = json.loads((ROOT / 'eval/casos_http.json').read_text('utf-8'))
    if len(casos) < 15 or len({c['id'] for c in casos}) != len(casos):
        raise ValueError('Se requieren al menos 15 casos con IDs únicos')
    results, omitted = [], []
    for case in casos:
        if (case.get('requiere_modelo') and not incluir_modelo) or (solo_backend and case.get('destino') == 'frontend'):
            omitted.append(case['id'])
            continue
        base = frontend if case.get('destino') == 'frontend' else backend
        headers = {k:(frontend if v == '$FRONTEND' else v) for k,v in case.get('headers', {}).items()}
        started = time.perf_counter()
        row = consultar(base+case['ruta'], method=case.get('metodo','GET'), headers=headers, payload=case.get('cuerpo'))
        try:
            ok = bool(cumple(case, row, frontend, revision))
        except (TypeError, ValueError, AttributeError):
            ok = False
        metadata = row.get('json', {})
        if not isinstance(metadata, dict):
            metadata = {}
        results.append({'id':case['id'], 'esperado':{'status':case['status'], 'contrato':case.get('contrato'),
                        'json_igual':case.get('json_igual'), 'documento':case.get('documento'), 'articulo':case.get('articulo')},
                        'obtenido':{k:v for k,v in row.items() if k != 'json'},
                        'estado_obtenido':metadata.get('estado'),
                        'revision_obtenida':metadata.get('revision'),
                        'segundos':round(time.perf_counter()-started, 3), 'ok':ok})
    times = sorted(r['segundos'] for r in results)
    return {'fecha_utc':datetime.now(timezone.utc).isoformat(), 'backend':backend, 'frontend':frontend,
            'revision_esperada':revision, 'incluye_modelo':incluir_modelo, 'solo_backend':solo_backend,
            'correctos':sum(r['ok'] for r in results), 'total':len(results), 'omitidos':omitted,
            'p95_segundos':times[max(0, math.ceil(len(times)*.95)-1)] if times else None, 'casos':results,
            'limite':'Las citas estructurales no prueban implicación semántica. Persistencia y revisión humana del corpus no se certifican aquí.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', default='https://titulacion-rag-386902880383.us-central1.run.app')
    parser.add_argument('--frontend', default='https://seminario-complexivo-grupo1.vercel.app')
    parser.add_argument('--incluir-modelo', action='store_true', help='Agrega consultas generativas directas y por proxy SSE; consume el proveedor del backend')
    parser.add_argument('--solo-backend', action='store_true')
    parser.add_argument('--expected-revision')
    parser.add_argument('--output', type=Path, default=ROOT / 'eval/results-funcionales.json')
    args = parser.parse_args()
    report = ejecutar(args.backend.rstrip('/'), args.frontend.rstrip('/'), incluir_modelo=args.incluir_modelo,
                      solo_backend=args.solo_backend, revision=args.expected_revision)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k != 'casos'}, ensure_ascii=False))
    return 0 if report['total'] >= 15 and report['correctos'] == report['total'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Smoke público Vercel/Cloud Run: solo GET/OPTIONS, sin credenciales ni modelos."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def origin(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:
        raise ValueError('Usa un origen HTTPS sin ruta, credenciales ni parámetros')
    return url.rstrip('/')


def consultar(url, *, method='GET', headers=None):
    try:
        try:
            response = urlopen(Request(url, method=method, headers=headers or {}), timeout=20)
        except HTTPError as error:
            response = error
        with response:
            body = response.read(8192).decode('utf-8', errors='replace')
            row = {'url':url, 'metodo':method, 'status':response.status,
                   'content_type':response.headers.get('Content-Type',''),
                   'allow_origin':response.headers.get('Access-Control-Allow-Origin'),
                   'allow_credentials':response.headers.get('Access-Control-Allow-Credentials')}
            if 'application/json' in row['content_type']:
                row['json'] = json.loads(body)
            return row
    except (URLError, TimeoutError, ValueError) as error:
        return {'url':url, 'metodo':method, 'status':None, 'error':type(error).__name__}


def verificar(frontend, backend):
    cases = []
    def registrar(nombre, row, ok):
        cases.append({'comprobacion':nombre, 'cumple':bool(ok), **row})
    for path in ('/', '/admin', '/metricas'):
        row = consultar(frontend+path)
        registrar('ruta_frontend'+path, row, row['status']==200 and 'text/html' in row.get('content_type',''))
    row = consultar(backend+'/health')
    registrar('backend_health', row, row['status']==200 and row.get('json',{}).get('status')=='ok')
    row = consultar(backend+'/api/chat/stream', method='OPTIONS', headers={
        'Origin':frontend, 'Access-Control-Request-Method':'POST', 'Access-Control-Request-Headers':'content-type'})
    registrar('cors_publico', row, row['status']==200 and row.get('allow_origin')==frontend
              and row.get('allow_credentials')!='true')
    row = consultar(frontend+'/api/admin/session')
    registrar('proxy_admin_sin_sesion', row, row['status']==401 and 'application/json' in row.get('content_type',''))
    return {'fecha_utc':datetime.now(timezone.utc).isoformat(), 'frontend':frontend, 'backend':backend,
            'correctos':sum(c['cumple'] for c in cases), 'total':len(cases), 'comprobaciones':cases,
            'limite':'No valida login real, persistencia, modelos ni despliegue de código nuevo.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frontend', default='https://seminario-complexivo-grupo1.vercel.app')
    parser.add_argument('--backend', default='https://titulacion-rag-386902880383.us-central1.run.app')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        report = verificar(origin(args.frontend), origin(args.backend))
    except ValueError as error:
        parser.exit(2, str(error)+'\n')
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['correctos']==report['total'] else 1)

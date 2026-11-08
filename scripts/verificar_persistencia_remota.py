"""Captura/compara estado remoto sin modificar documentos ni consumir modelos.

Login explícito por entrada oculta. No conserva cookies, contraseña ni textos.
Las etiquetas Cloud Run son declaradas por el operador: no prueba por sí solo
que se haya recreado una instancia. Adjuntar evidencia de tráfico/revisiones.
"""
import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
import warnings
from pathlib import Path
from urllib.parse import quote, urlsplit

import requests


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()


def compare(before, after):
    if before['url'] != after['url']:
        raise ValueError('Las capturas corresponden a servicios diferentes')
    if before['revision_cloud_run_declarada'] == after['revision_cloud_run_declarada']:
        raise ValueError('Se necesitan revisiones Cloud Run diferentes, verificadas por el operador')
    checks = {key: before[key] == after[key] for key in ('documents', 'prompts_sha256', 'config_sha256')}
    if not before['documents']:
        raise ValueError('No hay documentos para acreditar persistencia')
    return {'resultado': 'aprobado' if all(checks.values()) else 'diferencias',
            'comprobaciones': checks,
            'revision_cloud_run_antes': before['revision_cloud_run_declarada'],
            'revision_cloud_run_despues': after['revision_cloud_run_declarada'],
            'alcance': 'Igualdad de metadatos, originales descargados, historial y muestras de hasta 512 fragmentos por documento; prompts y configuración. Revisión Cloud Run declarada por operador. No verifica vectores completos, reinicio de Neon, generación ni métricas.'}


def read_password(from_env=False):
    if from_env:
        password = os.environ.pop('PERSISTENCE_ADMIN_PASSWORD', '')
        if not password:
            raise ValueError('Falta la contraseña temporal del proceso')
        return password
    # getpass puede recurrir a input() si no controla el eco: impedir ese fallback.
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        try:
            return getpass.getpass('Contraseña administrativa (entrada oculta): ')
        except getpass.GetPassWarning:
            raise ValueError('La terminal no permite ocultar la entrada; usar Read-Host -AsSecureString y --password-env') from None


def capture(url, deployment, username, password_env=False):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise ValueError('Usar origen HTTPS sin credenciales, ruta ni parámetros')
    url = url.rstrip('/')
    with requests.Session() as session:
        def get(path, binary=False):
            response = session.get(url+path, timeout=60, allow_redirects=False)
            if response.status_code != 200:
                raise ValueError(f'GET {path.split("?")[0]} devolvió HTTP {response.status_code}')
            return response.content if binary else response.json()

        password = read_password(password_env)
        try:
            login = session.post(url+'/api/admin/login', headers={'X-Admin-Request':'1'},
                                 json={'username':username,'password':password}, timeout=60, allow_redirects=False)
        finally:
            password = None
        if login.status_code != 200:
            raise ValueError(f'Login devolvió HTTP {login.status_code}; no repetir hasta revisar la causa')
        try:
            health = get('/health')
            get('/ready')
            bootstrap = get('/api/admin/bootstrap')
            documents = []
            for doc in sorted(bootstrap['documents'], key=lambda d: d['id']):
                identifier = quote(doc['id'], safe='')
                content = get(f'/api/admin/documents/{identifier}/file', binary=True)
                actual = hashlib.sha256(content).hexdigest()
                if actual != doc['sha256']:
                    raise ValueError('Un archivo descargado no coincide con su SHA registrado')
                history = get(f'/api/admin/history?resource={identifier}')
                chunks = get(f'/api/admin/rag/chunks?doc_id={identifier}')
                documents.append({'id':doc['id'], 'revision':doc['revision'],
                                  'metadata_sha256':digest(doc), 'archivo_sha256':actual,
                                  'historial_sha256':digest(history), 'fragmentos_muestra':len(chunks),
                                  'fragmentos_muestra_sha256':digest(chunks)})
            return {'fecha_utc':datetime.now(timezone.utc).isoformat(), 'url':url,
                    'revision_codigo':health.get('revision'),
                    'revision_cloud_run_declarada':deployment, 'documents':documents,
                    'prompts_sha256':digest(bootstrap['prompts']), 'config_sha256':digest(bootstrap['config']),
                    'credenciales_publicadas':False}
        finally:
            session.post(url+'/api/admin/logout', headers={'X-Admin-Request':'1'}, timeout=60, allow_redirects=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    cap = modes.add_parser('capturar')
    cap.add_argument('--url', required=True)
    cap.add_argument('--revision-cloud-run', required=True)
    cap.add_argument('--username', default='admin')
    cap.add_argument('--password-env', action='store_true', help='Lee y elimina PERSISTENCE_ADMIN_PASSWORD del entorno temporal del proceso')
    cap.add_argument('--output', type=Path, required=True)
    comp = modes.add_parser('comparar')
    comp.add_argument('--antes', type=Path, required=True)
    comp.add_argument('--despues', type=Path, required=True)
    comp.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = capture(args.url,args.revision_cloud_run,args.username,args.password_env) if args.mode == 'capturar' else compare(
            json.loads(args.antes.read_text()),json.loads(args.despues.read_text()))
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Reporte guardado; no contiene contraseñas ni cookies.')
        return 0 if result.get('resultado','aprobado') == 'aprobado' else 1
    except (ValueError, requests.RequestException):
        # Las excepciones de red pueden incorporar direcciones y cabeceras privadas.
        print('No se completó la verificación. Revisar URL, acceso, credenciales y estado del servicio; no publicar secretos.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

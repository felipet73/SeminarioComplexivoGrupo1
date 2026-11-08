"""Prepara un archivo privado para Secret Manager; nunca imprime la contraseña."""
import argparse
import getpass
import os
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def crear(project, region, instance, database, username, output, local_proxy_port=None):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT) and not output.is_relative_to(ROOT/'tmp'):
        raise ValueError('Dentro del repositorio solo se permite tmp/, excluido del paquete')
    password = getpass.getpass('Contraseña del usuario SQL (entrada oculta): ')
    if not password:
        raise ValueError('La contraseña no puede estar vacía')
    if local_proxy_port is not None and not 1 <= local_proxy_port <= 65535:
        raise ValueError('Puerto local inválido')
    authority = f'127.0.0.1:{local_proxy_port}' if local_proxy_port else ''
    value = f'postgresql://{quote(username, safe="")}:{quote(password, safe="")}@{authority}/{quote(database, safe="")}'
    if not local_proxy_port:
        value += f'?host=/cloudsql/{quote(project, safe="")}:{quote(region, safe="")}:{quote(instance, safe="")}'

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(value)
    print(f'Archivo privado creado: {output}. No subirlo a Git; eliminar después de guardar en Secret Manager.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='us-central1')
    parser.add_argument('--instance', default='titulacion-postgres')
    parser.add_argument('--database', default='titulacion')
    parser.add_argument('--user', default='rag_app')
    parser.add_argument('--output', type=Path, default=ROOT/'tmp/cloudsql-dsn.txt')
    parser.add_argument('--local-proxy-port', type=int, help='Solo para Cloud SQL Auth Proxy local; no IP remota directa')
    args = parser.parse_args()
    crear(args.project, args.region, args.instance, args.database, args.user, args.output, args.local_proxy_port)

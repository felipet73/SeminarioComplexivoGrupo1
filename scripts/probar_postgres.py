"""Ensayo aislado PostgreSQL: nuevo proceso sin disco local conserva datos e índice.

Solo crea/elimina un contenedor local de prueba. No recibe DSN de producción.
La contraseña temporal y cookies no se incluyen en el reporte.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CONTENT = 'Artículo 1. La constancia de persistencia conserva documentos e índices entre procesos sin datos personales.'.encode()
PROMPT = 'Prompt sintético para verificar persistencia después de reiniciar el proceso.'


def worker(stage, state_file):
    sys.path.insert(0, str(ROOT/'backend'))
    from app.services import admin_store as store, rag
    from app import admin_routes
    from app.admin_schemas import PromptInput
    from app.main import app
    from fastapi.testclient import TestClient
    if os.environ.get('TEST_PROMPT_DIR'):
        store.PROMPT_DIR = Path(os.environ['TEST_PROMPT_DIR'])
    client = TestClient(app)
    headers = {'X-Admin-Request': '1'}
    if stage == 'write':
        with store.db() as conn:
            config = store.get(conn, 'config', 'rag')
            config.update(strategy='lexical', top_k=2, revision=config['revision']+1)
            store.put(conn, 'config', 'rag', config)
        doc = rag.save_document('persistencia.txt', CONTENT,
                                dict(title='Normativa de persistencia', kind='normativa', source_url='',
                                     valid_from='2020-01-01', valid_to=None, approved=True, enabled=True, notes='Datos ficticios'), 'ensayo')
        rag.index_document(doc['id'], 'ensayo')
        original = store.prompt(3)
        admin_routes.edit_prompt(3, PromptInput(content=PROMPT, description='Prueba sintética de reinicio',
                                               expected_revision=original['revision']), actor='ensayo')
        with store.db() as conn:
            store.put(conn, 'embedding_cache', 'synthetic', [1.0]+[0.0]*767)
            conn.execute('UPDATE chunks SET vector=?,embedding_model=? WHERE doc_id=?',
                         (json.dumps([1.0]+[0.0]*767), 'synthetic', doc['id']))
        login = client.post('/api/admin/login', headers=headers,
                            json={'username':'admin', 'password':os.environ['ADMIN_PASSWORD']})
        assert login.status_code == 200
        state_file.write_text(json.dumps({'doc_id':doc['id'], 'cookie':client.cookies.get('uniandes_admin')}))
        if not store.is_postgres():
            exported = client.get('/api/admin/backup')
            assert exported.status_code == 200 and exported.headers['cache-control'] == 'no-store'
            (state_file.parent/'respaldo-privado.zip').write_bytes(exported.content)
        print(json.dumps({'escritura':'ok'}))
        return
    state = json.loads(state_file.read_text())
    with store.db() as conn:
        doc = store.get(conn, 'document', state['doc_id'])
        assert store.get(conn, 'embedding_cache', 'synthetic')[0] == 1.0
        assert json.loads(conn.execute('SELECT vector FROM chunks WHERE doc_id=?', (doc['id'],)).fetchone()['vector'])[0] == 1.0
        assert conn.execute('SELECT COUNT(*) FROM audit WHERE resource=?', (doc['id'],)).fetchone()[0] >= 2
    assert not (store.DATA_DIR/doc['path']).exists(), 'El ensayo debe leer el archivo desde PostgreSQL, no caché local'
    assert store.settings()['top_k'] == 2
    assert store.prompt(3)['content'] == PROMPT, 'Los archivos de la imagen no deben reemplazar el prompt guardado'
    found = rag.retrieve('constancia de persistencia')['chunks']
    assert found and any(c['doc_id'] == doc['id'] and c['section'] == 'Artículo 1' for c in found)
    response = client.get(f"/api/sources/{doc['id']}/1")
    assert response.status_code == 200 and response.content == CONTENT
    assert hashlib.sha256(response.content).hexdigest() == doc['sha256']
    client.cookies.set('uniandes_admin', state['cookie'])
    assert client.get('/api/admin/session').status_code == 401  # Reautenticación esperada.
    assert client.post('/api/admin/login', headers=headers,
                       json={'username':'admin', 'password':os.environ['ADMIN_PASSWORD']}).status_code == 200
    try:
        with store.db() as conn:
            store.put(conn, 'probe', 'rollback', {'unexpected':'must not persist'})
            raise RuntimeError('Rollback sintético')
    except RuntimeError:
        pass
    with store.db() as conn:
        assert store.get(conn, 'probe', 'rollback') is None
    print(json.dumps({'documento':'ok','archivo':'ok','indice_y_cita':'ok','prompts':'ok',
                      'configuracion':'ok','auditoria':'ok','vectores_y_cache':'ok',
                      'rollback':'ok','sesion_anterior':'invalidada','nuevo_login':'ok'}))


def run(output, with_corpus=False):
    for selector in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):
        os.environ.pop(selector, None)
    name = 'rag-postgres-'+secrets.token_hex(5)
    docker = ['docker', '--host=unix:///var/run/docker.sock']
    with tempfile.TemporaryDirectory(prefix='rag-pg-') as directory:
        temp = Path(directory)
        password = secrets.token_urlsafe(32)
        env_file = temp/'postgres.env'
        env_file.write_text('POSTGRES_DB=rag_test\nPOSTGRES_USER=rag_test\nPOSTGRES_PASSWORD='+password+'\n')
        env_file.chmod(0o600)
        try:
            subprocess.run(docker+['run','--rm','-d','--name',name,'--env-file',str(env_file),
                                  '-p','127.0.0.1::5432','postgres:17-alpine'], check=True, capture_output=True)
            for attempt in range(60):
                if subprocess.run(docker+['exec',name,'pg_isready','-h','127.0.0.1','-U','rag_test','-d','rag_test'], capture_output=True).returncode == 0:
                    break
                time.sleep(1)
            else:
                raise RuntimeError('PostgreSQL local no inició')
            info = json.loads(subprocess.check_output(docker+['inspect',name]))[0]
            port = info['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']
            env = dict(os.environ, RAG_DATABASE_URL=f'postgresql://rag_test:{password}@127.0.0.1:{port}/rag_test',
                       GEMINI_API_KEY='', OPENAI_API_KEY='', AI_API_KEY='', ADMIN_PASSWORD=secrets.token_urlsafe(32),
                       ADMIN_COOKIE_SECURE='false', APP_REVISION='ensayo-local-postgres')
            state = temp/'estado-privado.json'
            stages = []
            for stage in ('write','read'):
                env['RAG_DATA_DIR'] = str(temp/('disco-'+stage))
                completed = subprocess.run([sys.executable, __file__, '--worker',stage,'--state',str(state)],
                                           cwd=ROOT, env=env, text=True, capture_output=True)
                if completed.returncode:
                    # No volcar stderr completo: un driver podría incluir metadatos privados.
                    diagnostic = completed.stderr.replace(password,'[redactado]').replace(env['ADMIN_PASSWORD'],'[redactado]')
                    log = ROOT/'tmp/postgres-diagnostico.log'
                    log.parent.mkdir(parents=True, exist_ok=True)
                    log.write_text(diagnostic)
                    log.chmod(0o600)
                    raise RuntimeError(f'Falló fase {stage}; revisar tmp/postgres-diagnostico.log')
                stages.append(json.loads(completed.stdout.strip().splitlines()[-1]))
            # Reinicio real del servidor de prueba: no basta con renovar el cliente.
            subprocess.run(docker+['restart',name],check=True,capture_output=True)
            for attempt in range(60):
                if subprocess.run(docker+['exec',name,'pg_isready','-h','127.0.0.1','-U','rag_test','-d','rag_test'],capture_output=True).returncode == 0:
                    break
                time.sleep(1)
            else:
                raise RuntimeError('PostgreSQL no volvió después del reinicio')
            # Docker puede reasignar un puerto efímero al reiniciar el contenedor.
            restarted_info = json.loads(subprocess.check_output(docker+['inspect',name]))[0]
            port = restarted_info['NetworkSettings']['Ports']['5432/tcp'][0]['HostPort']
            env['RAG_DATABASE_URL'] = f'postgresql://rag_test:{password}@127.0.0.1:{port}/rag_test'
            env['RAG_DATA_DIR'] = str(temp/'disco-despues-reinicio-pg')
            restarted = subprocess.run([sys.executable,__file__,'--worker','read','--state',str(state)],
                                       cwd=ROOT,env=env,text=True,capture_output=True)
            if restarted.returncode:
                log = ROOT/'tmp/postgres-diagnostico.log'
                log.parent.mkdir(parents=True,exist_ok=True)
                log.write_text(restarted.stderr.replace(password,'[redactado]').replace(env['ADMIN_PASSWORD'],'[redactado]'))
                log.chmod(0o600)
                raise RuntimeError('Falló lectura después de reiniciar PostgreSQL; revisar tmp/postgres-diagnostico.log')
            restart_checks = json.loads(restarted.stdout.strip().splitlines()[-1])
            report = {'fecha_utc':datetime.now(timezone.utc).isoformat(),
                      'commit_base':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                      'alcance':'PostgreSQL 17 local, procesos nuevos con directorios locales diferentes y reinicio del servidor PostgreSQL; no prueba remota de Neon/Cloud Run.',
                      'reinicio_servidor_postgres':restart_checks,
                      'resultado':'aprobado','postgres_image_id':info['Image'],'fases':stages,'proveedores_consumidos':False,
                      'datos':'Documento y configuración sintéticos; sin DSN, contraseña o cookie en el reporte.'}
            # Importación real desde SQLite y rechazo de un destino ya ocupado.
            source_dir = temp/'sqlite-source'
            prompts = temp/'prompts'
            shutil.copytree(ROOT/'backend/app/prompts',prompts)
            local = dict(env, RAG_DATABASE_URL='', RAG_DATA_DIR=str(source_dir), TEST_PROMPT_DIR=str(prompts))
            subprocess.run([sys.executable,__file__,'--worker','write','--state',str(state)],
                           cwd=ROOT,env=local,check=True,capture_output=True)
            subprocess.run(docker+['exec',name,'createdb','-U','rag_test','rag_migration'],check=True,capture_output=True)
            migrated = dict(env,RAG_DATABASE_URL=env['RAG_DATABASE_URL'].rsplit('/',1)[0]+'/rag_migration',
                            RAG_DATA_DIR=str(temp/'disco-migrado'))
            migration_report = temp/'migration.json'
            exported_dir = temp/'sqlite-exportado'
            with zipfile.ZipFile(temp/'respaldo-privado.zip') as archive:
                assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in archive.namelist())
                archive.extractall(exported_dir)
            command = [sys.executable,'scripts/migrar_sqlite_postgres.py','--source-dir',str(exported_dir),
                       '--report',str(migration_report)]
            # Simula instalaciones SQLite que no exponen Connection.serialize.
            portable = (
                'import sqlite3,runpy,sys\n'
                'original=sqlite3.connect\n'
                'class Portable(sqlite3.Connection):\n'
                ' def __getattribute__(self,name):\n'
                '  if name=="serialize": raise AttributeError("serialize no disponible")\n'
                '  return super().__getattribute__(name)\n'
                'sqlite3.connect=lambda *a,**kw: original(*a,factory=Portable,**kw)\n'
                'sys.argv=sys.argv[1:]\n'
                'runpy.run_path(sys.argv[0],run_name="__main__")\n'
            )
            subprocess.run([sys.executable,'-c',portable]+command[1:],cwd=ROOT,env=migrated,check=True,capture_output=True)
            subprocess.run([sys.executable,__file__,'--worker','read','--state',str(state)],
                           cwd=ROOT,env=migrated,check=True,capture_output=True)
            refused = subprocess.run(command,cwd=ROOT,env=migrated,capture_output=True)
            assert refused.returncode == 2, 'No sobrescribir un destino ocupado'
            report['migracion_sqlite'] = json.loads(migration_report.read_text())
            report['migracion_sqlite']['destino_ocupado_rechazado'] = True
            assert report['migracion_sqlite']['sqlite_source_sha256'] == hashlib.sha256((exported_dir/'admin.sqlite3').read_bytes()).hexdigest()
            report['migracion_sqlite']['sin_serialize_y_hash_origen'] = True
            if with_corpus:
                # Se usa un DB distinto: el documento sintético no altera el golden set.
                subprocess.run(docker+['exec',name,'createdb','-U','rag_test','rag_corpus'], check=True, capture_output=True)
                env['RAG_DATABASE_URL'] = env['RAG_DATABASE_URL'].rsplit('/',1)[0]+'/rag_corpus'
                subprocess.run([sys.executable,'scripts/ingest.py','--strategy','lexical'],cwd=ROOT,env=env,check=True,capture_output=True)
                path = temp/'corpus.json'
                result = subprocess.run([sys.executable,'eval/evaluar.py','--output',str(path)],cwd=ROOT,env=env,capture_output=True)
                evaluation = json.loads(path.read_text())
                report['golden_set_postgres'] = {k:evaluation[k] for k in ('positivos','negativos','acierto_top_k','silencio','errores')}
                if result.returncode:
                    raise RuntimeError('La recuperación PostgreSQL no cumplió los umbrales')
            output.parent.mkdir(parents=True,exist_ok=True)
            output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps(report,ensure_ascii=False))
        finally:
            subprocess.run(docker+['rm','-f',name],capture_output=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,default=ROOT/'tmp/persistencia-postgres.json')
    parser.add_argument('--with-corpus',action='store_true')
    parser.add_argument('--worker',choices=['write','read'],help=argparse.SUPPRESS)
    parser.add_argument('--state',type=Path,help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        worker(args.worker,args.state)
    else:
        run(args.report,args.with_corpus)

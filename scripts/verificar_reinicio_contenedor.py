"""Recrea dos contenedores locales sin volumen y compara recuperación citada de semilla."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]


def comprobar(image, revision, report):
    for selector in ('DOCKER_HOST','DOCKER_CONTEXT','DOCKER_TLS','DOCKER_TLS_VERIFY','DOCKER_CERT_PATH'):
        os.environ.pop(selector,None)
    docker = ['docker','--host=unix:///var/run/docker.sock']
    snapshots = []
    for _ in range(2):
        name = 'rag-reinicio-'+secrets.token_hex(5)
        try:
            subprocess.run(docker+['run','--rm','-d','--name',name,'-p','127.0.0.1::8080',image],check=True,capture_output=True)
            info = json.loads(subprocess.check_output(docker+['inspect',name]))[0]
            port = info['NetworkSettings']['Ports']['8080/tcp'][0]['HostPort']
            url = 'http://127.0.0.1:'+port
            for attempt in range(30):
                try:
                    with urlopen(url+'/health', timeout=3) as response:
                        health = json.load(response)
                    break
                except (URLError, TimeoutError, ConnectionError):
                    if attempt == 29:
                        raise
                    time.sleep(1)
            assert health['status']=='ok' and health['revision']==revision
            with urlopen(url+'/ready',timeout=5) as response:
                ready = json.load(response)
            request = Request(url+'/api/herramientas/consultar-requisitos',
                              data=json.dumps({'modalidad':'titulación'}).encode(),
                              headers={'Content-Type':'application/json'})
            with urlopen(request,timeout=10) as response:
                result = json.load(response)
            assert ready['fragmentos_elegibles']>0 and result['pasajes']
            assert all(p['fragmento_id'] and p['seccion'] and p['pagina']>0 and p['texto'] for p in result['pasajes'])
            snapshots.append({'container_id':info['Id'],'image_id':info['Image'], 'health':health, 'ready':ready,
                              'citas':[{'fragmento_id':p['fragmento_id'],'seccion':p['seccion'],'pagina':p['pagina']} for p in result['pasajes']],
                              'respuesta_sha256':hashlib.sha256(json.dumps(result,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
        finally:
            subprocess.run(docker+['rm','-f',name],capture_output=True)
    assert snapshots[0]['container_id']!=snapshots[1]['container_id']
    assert snapshots[0]['image_id']==snapshots[1]['image_id']
    assert snapshots[0]['respuesta_sha256']==snapshots[1]['respuesta_sha256']
    assert snapshots[0]['ready']==snapshots[1]['ready']
    result = {'fecha_utc':datetime.now(timezone.utc).isoformat(),'resultado':'aprobado', 'imagen':image,
              'revision_declarada':revision,'antes_despues':snapshots,
              'alcance':'Dos contenedores locales nuevos sin volumen recuperan la semilla y devuelven los mismos pasajes citados. No acredita retención de cargas administrativas ni reinicio remoto de Cloud Run.',
              'proveedores_consumidos':False,'generacion_llm_evaluada':False}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'resultado':result['resultado'],'fragmentos':snapshots[1]['ready']['fragmentos_elegibles'],'reporte':str(report)},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',required=True)
    parser.add_argument('--expected-revision',required=True)
    parser.add_argument('--report',type=Path,default=ROOT/'tmp/reinicio-contenedor.json')
    args=parser.parse_args()
    comprobar(args.image,args.expected_revision,args.report)

import json
from dataclasses import asdict
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from app.main import app, obtener_llm
from app import admin_auth, admin_routes
from app.config import Settings
from app.prompts import cargar_prompt
from app.services import admin_store as store, rag, analysis
from app.services.llm import ResultadoLLM

HEADERS={'X-Admin-Request':'1'}
TEXT='Artículo 1. Titulación. El proceso de titulación requiere consultar la modalidad con Secretaría Académica.\nArtículo 2. Prácticas. Las prácticas se revisan con la coordinación académica de cada carrera.'

@pytest.fixture
def client(monkeypatch):
    config=Settings(_env_file=None,admin_password='clave-de-prueba',gemini_api_key=None,openai_api_key=None)
    monkeypatch.setattr(admin_auth,'get_settings',lambda:config)
    monkeypatch.setattr(admin_routes,'get_settings',lambda:config)
    with TestClient(app) as c:
        yield c

def signin(client):
    r=client.post('/api/admin/login',headers=HEADERS,json={'username':'admin','password':'clave-de-prueba'})
    assert r.status_code==200
    return r

def upload(client,**changes):
    meta={'title':'Normativa de prueba','kind':'normativa','source_url':'https://example.edu/norma','valid_from':'2020-01-01','approved':True,'enabled':True,**changes}
    r=client.post('/api/admin/documents',headers=HEADERS,data={'metadata':json.dumps(meta)},files={'file':('reglamento.txt',TEXT.encode(),'text/plain')})
    assert r.status_code==200,r.text
    return r.json()

def test_login_proteccion_csrf_y_logout(client):
    assert client.get('/api/admin/bootstrap').status_code==401
    assert client.post('/api/admin/login',json={'username':'admin','password':'clave-de-prueba'}).status_code==403
    assert client.post('/api/admin/login',headers=HEADERS|{'Origin':'https://intruso.example'},json={'username':'admin','password':'clave-de-prueba'}).status_code==403
    response=signin(client)
    cookie=response.headers['set-cookie'].lower()
    assert 'httponly' in cookie and 'samesite=strict' in cookie
    assert 'clave-de-prueba' not in response.text
    assert client.get('/api/admin/bootstrap').status_code==200
    assert client.post('/api/admin/logout',headers=HEADERS,json={}).status_code==200
    assert client.get('/api/admin/bootstrap').status_code==401

def test_limite_de_intentos_y_sesion_expirada(client):
    for _ in range(5):
        assert client.post('/api/admin/login',headers=HEADERS,json={'username':'admin','password':'incorrecta'}).status_code==401
    assert client.post('/api/admin/login',headers=HEADERS,json={'username':'admin','password':'incorrecta'}).status_code==429
    admin_auth.FAILURES.clear()
    signin(client)
    for session in admin_auth.SESSIONS.values():
        session['expires']=0
    assert client.get('/api/admin/bootstrap').status_code==401

def test_prompts_archivo_historial_y_version_activa(client):
    signin(client)
    content='Rol: orientador de prueba. Tarea: orientar. Restricciones: no inventar normas. Abstención: acudir a Secretaría.'
    p=client.post('/api/admin/prompts',headers=HEADERS,json={'content':content,'description':'Nueva variante experimental'}).json()
    assert p['version']==4
    assert (store.PROMPT_DIR/'system_v4.md').read_text(encoding='utf-8')==content
    cfg=client.get('/api/admin/bootstrap').json()['config']
    assert client.post('/api/admin/config',headers=HEADERS,json=cfg|{'active_prompt':4}).status_code==200
    assert cargar_prompt()==content
    updated=client.post('/api/admin/prompts/4',headers=HEADERS,json={'content':content+' Ejemplo: titulación.','description':'Con ejemplo','expected_revision':1})
    assert updated.json()['revision']==2
    assert client.post('/api/admin/prompts/4',headers=HEADERS,json={'content':content,'description':'Antigua','expected_revision':1}).status_code==409
    assert len(client.get('/api/admin/history?resource=prompt:4').json())==2

def test_documentos_indexacion_vigencia_exclusion_y_reemplazo(client):
    signin(client)
    d=upload(client)
    assert client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()['chunks']==[]
    r=client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={})
    assert r.status_code==200,r.text
    assert [c['section'] for c in r.json()['chunks']]==['Artículo 1','Artículo 2']
    chunks=client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()['chunks']
    assert chunks and chunks[0]['revision']==1
    assert client.get(f'/api/sources/{d["id"]}/1').status_code==200
    off=client.post(f'/api/admin/documents/{d["id"]}',headers=HEADERS,json=d|{'enabled':False,'expected_revision':1}).json()
    assert client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()['chunks']==[]
    assert client.get(f'/api/sources/{d["id"]}/1').status_code==404
    meta={k:off[k] for k in ('title','kind','source_url','valid_from','valid_to','approved','enabled','notes')}
    meta['enabled']=True
    replace=client.post(f'/api/admin/documents/{d["id"]}/replace',headers=HEADERS,data={'metadata':json.dumps(meta),'expected_revision':'2'},files={'file':('nuevo.txt',(TEXT+' Texto actualizado.').encode(),'text/plain')})
    assert replace.status_code==200,replace.text
    assert replace.json()['sha256']!=d['sha256']
    assert replace.json()['indexed_revision'] is None
    assert replace.json()['approved'] is False
    assert client.get(f'/api/admin/documents/{d["id"]}/file?revision=1').content==TEXT.encode()
    assert len(client.get(f'/api/admin/history?resource={d["id"]}').json())==4

@pytest.mark.parametrize('changes',[{'approved':False},{'enabled':False},{'valid_from':'2099-01-01'},{'valid_to':'2020-12-31'}])
def test_no_recupera_fuentes_no_elegibles(client,changes):
    signin(client)
    d=upload(client,**changes)
    client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={})
    assert client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()['chunks']==[]

def test_upload_invalido_y_config_solapamiento(client):
    signin(client)
    bad=client.post('/api/admin/documents',headers=HEADERS,data={'metadata':json.dumps({'title':'Prueba','valid_from':'2020-01-01'})},files={'file':('prueba.exe',b'contenido que no debe aceptarse')})
    assert bad.status_code==422
    cfg=client.get('/api/admin/bootstrap').json()['config']
    assert client.post('/api/admin/config',headers=HEADERS,json=cfg|{'chunk_size':300,'overlap':200}).status_code==422

def test_chat_cita_solo_ids_recuperados_y_abstiene_en_ids_inventados(client):
    signin(client)
    d=upload(client)
    chunk=client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={}).json()['chunks'][0]
    def fake(*args,**kwargs):
        assert kwargs['contexto']['evidencia']
        return ResultadoLLM(json.dumps({'respuesta':'Consulta tu modalidad con Secretaría.','estado':'respuesta','fragmentos':[chunk['id']]}),'doble',False,.1)
    app.dependency_overrides[obtener_llm]=lambda:SimpleNamespace(generar_texto=fake)
    try:
        response=client.post('/api/chat',json={'pregunta':'Consulta de titulación'}).json()
        assert response['estado']=='respuesta'
        assert response['fuentes'][0]['fragmento_id']==chunk['id']
        def fabricated(*a,**kw):
            return ResultadoLLM('{"respuesta":"Inventado","estado":"respuesta","fragmentos":["falso"]}','doble',False,.1)
        app.dependency_overrides[obtener_llm]=lambda:SimpleNamespace(generar_texto=fabricated)
        assert client.post('/api/chat',json={'pregunta':'Consulta de titulación'}).json()['estado']=='abstencion'
    finally:
        app.dependency_overrides.clear()

def test_hibrido_persistente_y_fallback_lexico(client,monkeypatch):
    signin(client)
    cfg=client.get('/api/admin/bootstrap').json()['config']
    client.post('/api/admin/config',headers=HEADERS,json=cfg|{'strategy':'hybrid'})
    monkeypatch.setattr(rag,'embed',lambda texts,model,task:[[1.,0.] for _ in texts])
    d=upload(client)
    assert client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={}).status_code==200
    r=client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()
    assert r['strategy']=='hybrid'
    monkeypatch.setattr(rag,'embed',lambda *a:(_ for _ in ()).throw(RuntimeError('offline')))
    r=client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()
    assert r['strategy']=='lexical' and r['warning']
    assert r['chunks']

def test_simulacion_versiones_metricas_y_evaluador(client,monkeypatch):
    signin(client)
    calls=[]
    def generate(prompt,question,model,**kwargs):
        assert kwargs['permitir_fallback'] is False
        calls.append((prompt,question))
        return ResultadoLLM('Orientación evaluada','modelo-doble',False,.2,10,15,25)
    app.dependency_overrides[admin_routes.admin_llm]=lambda:SimpleNamespace(generar_texto=generate)
    class ImmediateThread:
        def __init__(self,target,args,**kwargs):self.target,self.args=target,args
        def start(self):self.target(*self.args)
    monkeypatch.setattr(analysis,'Thread',ImmediateThread)
    try:
        r=client.post('/api/admin/analysis',headers=HEADERS,json={'versions':[1,2,3],'model':'gemini','cases':[{'question':'Consulta de titulación','expected':'Debe abstenerse sin fuente.'}],'use_rag':False})
        assert r.status_code==202,r.text
        job=client.get('/api/admin/analysis/'+r.json()['id']).json()
        assert job['status']=='completed'
        assert len(job['results'])==3 and len(calls)==4
        assert job['results'][0]['tokens_total']==25
        assert job['review']['texto']=='Orientación evaluada'
        assert job['prompts'][0]['revision']==1
        assert job['rag_config']['top_k']==4
        assert job['evidence']==[{'chunks':[]}]
        assert job['duration_seconds']>=0
    finally:
        app.dependency_overrides.clear()

def test_edicion_externa_del_prompt_genera_revision(client):
    signin(client)
    original=store.prompt(1)
    (store.PROMPT_DIR/'system_v1.md').write_text(original['content']+'\nEjemplo adicional de orientación.',encoding='utf-8')
    updated=store.prompt(1)
    assert updated['revision']==2
    history=client.get('/api/admin/history?resource=prompt:1').json()
    assert history[0]['action']=='sync_prompt_file'

@pytest.mark.parametrize('contexto,pendientes',[({},['carrera']),({'carrera':'Software'},[])])
def test_simulacion_comparte_contrato_y_contexto_del_chat(client,monkeypatch,contexto,pendientes):
    signin(client)
    seen=[]
    def generate(prompt,question,model,**kwargs):
        assert kwargs['permitir_fallback'] is False
        if 'Eres evaluador' in prompt:
            return ResultadoLLM('Comparación de prueba','test',False,.1,1,2,3)
        assert 'campos_necesarios' in prompt
        seen.append(kwargs['contexto'])
        return ResultadoLLM(json.dumps({'respuesta':'Indica tu carrera.','estado':'aclaracion','campos_necesarios':['carrera']}),'test',False,.1,1,2,3)
    class ImmediateThread:
        def __init__(self,target,args,**kwargs):self.target,self.args=target,args
        def start(self):self.target(*self.args)
    monkeypatch.setattr(analysis,'Thread',ImmediateThread)
    app.dependency_overrides[admin_routes.admin_llm]=lambda:SimpleNamespace(generar_texto=generate)
    try:
        r=client.post('/api/admin/analysis',headers=HEADERS,json={'versions':[1,2],'model':'gemini','cases':[{'question':'Consulta de titulación','contexto':contexto}],'use_rag':False})
        assert r.status_code==202,r.text
        job=client.get('/api/admin/analysis/'+r.json()['id']).json()
        assert job['status']=='completed' and len(seen)==2
        for row in job['results']:
            assert row['texto']=='Indica tu carrera.'
            assert row['contrato']['estado']=='aclaracion'
            assert [c['campo'] for c in row['contrato']['campos_necesarios']]==pendientes
            assert row['tokens_total']==3 and row['salida_modelo']
        assert all(c.get('carrera')==contexto.get('carrera') for c in seen)
        assert job['cases'][0]['contexto']==contexto
    finally:
        app.dependency_overrides.clear()

def test_fallo_de_embeddings_conserva_indice_anterior(client,monkeypatch):
    signin(client)
    d=upload(client)
    first=client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={}).json()['chunks']
    cfg=client.get('/api/admin/bootstrap').json()['config']
    client.post('/api/admin/config',headers=HEADERS,json=cfg|{'strategy':'hybrid'})
    monkeypatch.setattr(rag,'embed',lambda *a:(_ for _ in ()).throw(RuntimeError('offline')))
    r=client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={})
    assert r.status_code==503
    assert client.get(f'/api/admin/rag/chunks?doc_id={d["id"]}').json()==first

def test_cambiar_top_k_no_obliga_reindexar(client):
    signin(client)
    d=upload(client)
    client.post(f'/api/admin/rag/index/{d["id"]}',headers=HEADERS,json={})
    cfg=client.get('/api/admin/bootstrap').json()['config']
    client.post('/api/admin/config',headers=HEADERS,json=cfg|{'top_k':2})
    assert client.post('/api/admin/rag/search',headers=HEADERS,json={'query':'titulación'}).json()['chunks']

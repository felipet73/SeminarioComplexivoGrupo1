import json
import re
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from app.admin_auth import COOKIE, LOCK, SESSIONS, digest, login, require_admin
from app.admin_schemas import Login, PromptInput, DocMeta, DocUpdate, RAGConfig, Search, AnalysisInput
from app.config import get_settings
from app.services import admin_store as store, rag, analysis
from app.services.llm import ClienteLLM
from app.eval_cases import CASES

router = APIRouter(prefix='/api/admin', tags=['Administración'])
protected = APIRouter(dependencies=[Depends(require_admin)])

def admin_llm():
    return ClienteLLM(get_settings())

@router.post('/login')
def signin(payload: Login, request: Request, response: Response):
    token=login(request,payload.username,payload.password)
    settings=get_settings()
    response.set_cookie(COOKIE,token,httponly=True,samesite='strict',secure=settings.admin_cookie_secure,
                        max_age=settings.admin_session_minutes*60,path='/api/admin')
    return {'username':settings.admin_username}

@protected.get('/session')
def session(actor=Depends(require_admin)):
    return {'username':actor}

@protected.post('/logout')
def signout(request: Request,response: Response):
    with LOCK:
        SESSIONS.pop(digest(request.cookies.get(COOKIE,'')),None)
    response.delete_cookie(COOKIE,path='/api/admin')
    return {'ok':True}

@protected.get('/bootstrap')
def bootstrap():
    s=get_settings()
    with store.db() as conn:
        return {'prompts':sorted(store.all_records(conn,'prompt'),key=lambda p:p['version']),
                'documents':[rag.public_doc(d) | {'eligible':rag.eligible(d),'index_current':d.get('index_signature')==rag.signature(store.get(conn,'config','rag')) and d['indexed_revision']==d['revision']} for d in store.all_records(conn,'document')],
                'config':store.get(conn,'config','rag'),
                'reference_cases':CASES,
                'models':[{'id':'gemini','name':s.ai_model,'configured':bool(s.gemini_api_key)},
                          {'id':'openai','name':s.fallback_model,'configured':bool(s.openai_api_key)}]}

@protected.post('/prompts')
def create_prompt(payload: PromptInput, actor=Depends(require_admin)):
    with store.db() as conn:
        version=max([p['version'] for p in store.all_records(conn,'prompt')]+[0])+1
        if version > 999:
            raise HTTPException(409,'Se alcanzó el límite de versiones.')
        value={'version':version,'content':payload.content,'description':payload.description,'revision':1,'updated':store.now()}
        write_prompt(version,payload.content)
        store.put(conn,'prompt',version,value)
        store.audit(conn,actor,'create_prompt',f'prompt:{version}',None,value)
    return value

def write_prompt(version, content):
    store.PROMPT_DIR.mkdir(parents=True,exist_ok=True)
    path=store.PROMPT_DIR/f'system_v{version}.md'
    temp=path.with_suffix('.tmp')
    temp.write_text(content,encoding='utf-8')
    temp.replace(path)

@protected.post('/prompts/{version}')
def edit_prompt(version: int,payload: PromptInput,actor=Depends(require_admin)):
    with store.db() as conn:
        old=store.get(conn,'prompt',version)
        if not old:
            raise HTTPException(404,'Versión no encontrada.')
        if old['revision'] != payload.expected_revision:
            raise HTTPException(409,'El prompt cambió. Recarga antes de guardarlo.')
        value=dict(old,content=payload.content,description=payload.description,revision=old['revision']+1,updated=store.now())
        write_prompt(version,payload.content)
        store.put(conn,'prompt',version,value)
        store.audit(conn,actor,'edit_prompt',f'prompt:{version}',old,value)
    return value

@protected.post('/config')
def save_config(payload: RAGConfig,actor=Depends(require_admin)):
    with store.db() as conn:
        old=store.get(conn,'config','rag')
        if old['revision']!=payload.revision:
            raise HTTPException(409,'La configuración cambió; recarga la página.')
        if not store.get(conn,'prompt',payload.active_prompt):
            raise HTTPException(422,'No existe la versión seleccionada.')
        value=payload.model_dump() | {'revision':old['revision']+1}
        store.put(conn,'config','rag',value)
        store.audit(conn,actor,'configure_rag','config',old,value)
    return value

@protected.post('/documents')
async def upload_document(metadata: str=Form(...), file:UploadFile=File(...), actor=Depends(require_admin)):
    try:
        meta=DocMeta.model_validate_json(metadata).model_dump(mode='json')
        content=await file.read(rag.MAX_BYTES+1)
        with store.db() as conn:
            if len(store.all_records(conn,'document'))>=100:
                raise HTTPException(409,'Límite local de 100 documentos alcanzado.')
        return await run_in_threadpool(rag.save_document,file.filename or '',content,meta,actor)
    except (ValueError,ValidationError):
        raise HTTPException(422,'Revisa el formato del archivo, el texto extraíble y las fechas de vigencia.')
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422,'No se pudo leer el archivo. Revisa que no esté dañado y tenga texto extraíble.')
    finally:
        await file.close()

@protected.post('/documents/{doc_id}')
def edit_document(doc_id:str, payload:DocUpdate,actor=Depends(require_admin)):
    try:
        return rag.update_document(doc_id,payload.model_dump(mode='json',exclude={'expected_revision'}),actor,payload.expected_revision)
    except LookupError:
        raise HTTPException(404,'Documento no encontrado.')
    except rag.RevisionConflict as e:
        raise HTTPException(409,str(e))

@protected.post('/documents/{doc_id}/replace')
async def replace_document(doc_id:str,metadata:str=Form(...),expected_revision:int=Form(...),file:UploadFile=File(...),actor=Depends(require_admin)):
    try:
        meta=DocMeta.model_validate_json(metadata).model_dump(mode='json')
        meta['approved']=False  # Un archivo distinto necesita revisión humana nueva.
        content=await file.read(rag.MAX_BYTES+1)
        return await run_in_threadpool(rag.save_document,file.filename or '',content,meta,actor,doc_id,expected_revision)
    except LookupError:
        raise HTTPException(404,'Documento no encontrado.')
    except rag.RevisionConflict as e:
        raise HTTPException(409,str(e))
    except (ValueError,ValidationError):
        raise HTTPException(422,'Revisa formato, texto y fechas del nuevo archivo.')
    except Exception:
        raise HTTPException(422,'No se pudo leer el nuevo archivo.')
    finally:
        await file.close()

def file_response(doc):
    target=(store.DATA_DIR/doc['path']).resolve()
    if not target.is_relative_to(store.DATA_DIR.resolve()) or not target.is_file():
        raise HTTPException(404,'Archivo no encontrado.')
    return FileResponse(target,filename=doc['name'],headers={'X-Content-Type-Options':'nosniff','Cache-Control':'no-store'})

@protected.get('/documents/{doc_id}/file')
def download_document(doc_id:str, revision:int|None=None):
    with store.db() as conn:
        doc=store.get(conn,'document',doc_id)
        if revision and doc and revision!=doc['revision']:
            snapshots=conn.execute('SELECT after_json FROM audit WHERE resource=? ORDER BY id DESC',(doc_id,)).fetchall()
            doc=next((json.loads(r['after_json']) for r in snapshots if json.loads(r['after_json']).get('revision')==revision and 'path' in json.loads(r['after_json'])),None)
    if not doc:
        raise HTTPException(404,'Revisión no encontrada.')
    return file_response(doc)

@protected.get('/history')
def history(resource:str):
    with store.db() as conn:
        rows=conn.execute('SELECT * FROM audit WHERE resource=? ORDER BY id DESC LIMIT 100',(resource,)).fetchall()
    result=[]
    for row in rows:
        value=dict(row)
        for key in ('before_json','after_json'):
            parsed=json.loads(value.pop(key))
            value[key.removesuffix('_json')]=rag.public_doc(parsed) if isinstance(parsed,dict) and 'pages' in parsed else parsed
        result.append(value)
    return result

@protected.get('/rag/chunks')
def chunks(doc_id:str):
    with store.db() as conn:
        return [dict(r) for r in conn.execute('SELECT id,doc_id,revision,title,section,page,text FROM chunks WHERE doc_id=? ORDER BY rowid LIMIT 512',(doc_id,))]

@protected.post('/rag/index/{doc_id}')
def index_document(doc_id:str,actor=Depends(require_admin)):
    try:
        return rag.index_document(doc_id,actor)
    except LookupError:
        raise HTTPException(404,'Documento no encontrado.')
    except rag.RevisionConflict as e:
        raise HTTPException(409,str(e))
    except ValueError as e:
        raise HTTPException(422,str(e))
    except Exception:
        raise HTTPException(503,'No se pudo generar el índice; revisa la clave o disponibilidad de embeddings. El índice anterior se conserva.')

@protected.post('/rag/search')
def search(payload:Search):
    return rag.retrieve(payload.query)

@protected.post('/analysis',status_code=202)
def start_analysis(payload:AnalysisInput,actor=Depends(require_admin),llm=Depends(admin_llm)):
    try:
        job=analysis.launch(payload,actor,llm)
        return {'id':job['id'],'status':job['status']}
    except ValueError:
        raise HTTPException(422,'Una versión seleccionada ya no existe.')
    except RuntimeError as e:
        raise HTTPException(409,str(e))

@protected.get('/analysis')
def analyses():
    with store.db() as conn:
        jobs=store.all_records(conn,'analysis')
    return [{'id':j['id'],'created':j['created'],'status':j['status'],'model':j['model'],'versions':j['versions']} for j in sorted(jobs,key=lambda j:j['created'],reverse=True)[:30]]

@protected.get('/analysis/{job_id}')
def get_analysis(job_id:str):
    with store.db() as conn:
        job=store.get(conn,'analysis',job_id)
    if not job:
        raise HTTPException(404,'Simulación no encontrada.')
    return job

router.include_router(protected)

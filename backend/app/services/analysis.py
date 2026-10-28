"""Comparación reproducible en segundo plano; no mezcla proveedores silenciosamente."""
import hashlib
import time
from dataclasses import asdict
from threading import BoundedSemaphore, Thread
from app.services import admin_store as store
from app.services.rag import retrieve
from app.services.chat_flow import generar_respuesta, respuesta_local, app_admin_prompt
from app.schemas import ConsultaChat
from app.services.tracing import step

BUSY = BoundedSemaphore(1)

def update(job):
    with store.db() as conn:
        store.put(conn,'analysis',job['id'],job)

def execute(job, llm):
    started=time.perf_counter()
    try:
        job['status']='running'
        job['trace'][1]['status']='running'
        update(job)
        # Misma recuperación para todas las variantes de una pregunta.
        evidence = [retrieve(c['question'],job['rag_config']) if job['use_rag'] and not respuesta_local(c['question']) else {'chunks':[]} for c in job['cases']]
        searches=sum(bool(job['use_rag'] and not respuesta_local(c['question'])) for c in job['cases'])
        job['trace'][1].update(status='completed' if searches else 'skipped',details={'busquedas':searches,'casos':len(evidence),'fragmentos':sum(len(e['chunks']) for e in evidence)})
        job['trace'][2]['status']='running'
        job['evidence']=evidence
        update(job)
        for prompt in job['prompts']:
            for i,case in enumerate(job['cases']):
                start=time.perf_counter()
                row={'version':prompt['version'],'prompt_revision':prompt['revision'],
                     'prompt_sha256':hashlib.sha256(prompt['content'].encode()).hexdigest(),'case':i+1,'question':case['question'],
                     'evidence_ids':[c['id'] for c in evidence[i]['chunks']]}
                try:
                    contrato,r=generar_respuesta(ConsultaChat(pregunta=case['question'],modelo_preferido=job['model'],**case.get('contexto',{})),
                        llm,system_prompt=prompt['content'],evidencia=evidence[i]['chunks'],permitir_fallback=False)
                    metricas=asdict(r) if r else {'modelo':'validación local','fallback':False,'segundos':0,'tokens_entrada':0,'tokens_salida':0,'tokens_total':0}
                    row.update(metricas,status='ok',texto=contrato.respuesta,contrato=contrato.model_dump())
                    row['salida_modelo']=r.texto if r else None
                except Exception as error:
                    category=getattr(error,'category','fallo_general')
                    status=getattr(error,'status',None) or getattr(error,'status_code',None)
                    row.update(status='error',error=f'El proveedor no respondió ({category}; código {status or "N/D"}).',
                               segundos=round(time.perf_counter()-start,3),tokens_total=None)
                job['results'].append(row)
                update(job)
        job['trace'][2].update(status='completed',details={'resultados':len(job['results'])})
        job['trace'][3].update(status='completed',details={'con_contrato':sum('contrato' in r for r in job['results'])})
        job['trace'][4].update(status='completed',details={'tokens_reportados':sum(r.get('tokens_total') or 0 for r in job['results']),'sin_reporte':sum(r.get('tokens_total') is None for r in job['results']),'errores':sum(r['status']=='error' for r in job['results'])})
        job['trace'][5].update(status='completed',details={'evaluaciones_ia':0})
        job.update(status='completed',finished=store.now(),duration_seconds=round(time.perf_counter()-started,3))
        update(job)
    except Exception:
        for item in job['trace']:
            if item['status']=='running':item['status']='error'
        job.update(status='error',error='No se pudo completar la simulación. Los resultados parciales están conservados.')
        update(job)
    finally:
        BUSY.release()

def launch(payload, actor, llm):
    # Captura exacta de prompts; una edición posterior no cambia el experimento.
    prompts = [store.prompt(v) for v in payload.versions]
    if not BUSY.acquire(blocking=False):
        raise RuntimeError('Ya hay una simulación ejecutándose. Espera su finalización.')
    job={'id':store.new_id(),'status':'queued','created':store.now(),'actor':actor,**payload.model_dump(),
         'prompts':prompts,'chat_rules':app_admin_prompt,'rag_config':store.settings(),'results':[],'review':None,'evaluation_mode':'measurements_only',
         'trace':[step('snapshot','Capturar experimento','Se conservan prompts, revisiones, reglas del chat y configuración para trazabilidad.',versiones=len(prompts),casos=len(payload.cases)),
                  step('retrieve','Recuperar evidencia','Se recupera una vez por caso y se comparte entre versiones. Sin RAG o ante rechazo local no se ejecuta búsqueda.','pending'),
                  step('generate','Ejecutar variantes','Cada versión usa el mismo proveedor sin fallback. Un rechazo local no llama al modelo; un fallo de una variante no detiene las demás.','pending'),
                  step('validate','Validar respuestas','El mismo flujo del chat valida JSON, citas y campos necesarios. Las salidas inválidas se convierten en abstención segura.','pending'),
                  step('measure','Reunir mediciones','Se recopilan latencia, tokens reportados y errores. No se calcula exactitud ni se elige un ganador por estos números.','pending'),
                  step('save','Guardar resultados','Se persiste el experimento exportable. No se solicita evaluación, resumen ni comparación adicional a la IA.','pending')]}
    try:
        update(job)
        Thread(target=execute,args=(job,llm),daemon=True).start()
    except Exception:
        BUSY.release()
        raise
    return job

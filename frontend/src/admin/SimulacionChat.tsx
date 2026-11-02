import { useState } from 'react';
import { API } from '../api';
import type { Contexto } from '../ContextoAcademico';
import CamposNecesarios from '../CamposNecesarios';
import { adminAPI, type Job, type Result } from './api';
import '../simulacion.css';

export default function SimulacionChat({job,cambiar}:{job:Job;cambiar:(job:Job)=>void}){
  const [solicitud,setSolicitud]=useState<Result|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const running=job.status==='queued'||job.status==='running';
  async function reconsultar(contexto:Contexto){
    if(!solicitud||running||busy)return;
    setBusy(true);setError('');
    try{
      const caso=job.cases[solicitud.case-1];
      const nuevo=await adminAPI<{id:string}>('/analysis',{versions:job.versions,model:job.model,use_rag:job.use_rag??true,cases:[{...caso,contexto:{...caso.contexto,...contexto}}]});
      const actualizado=await adminAPI<Job>(`/analysis/${nuevo.id}`);
      setSolicitud(null);cambiar(actualizado);
    }catch(e){setError((e as Error).message)}finally{setBusy(false)}
  }
  return <>
    {solicitud?.contrato?.campos_necesarios?.length?<CamposNecesarios respuesta={solicitud.contrato.respuesta} campos={solicitud.contrato.campos_necesarios} ocupado={busy} error={error} consultar={valores=>void reconsultar(valores)} salir={()=>{setSolicitud(null);setError('')}}/>:null}
    <p className="admin-hint">Mismo comportamiento de aclaración, citas y seguridad que el chat principal. Completar datos crea una nueva comparación de ese caso, en todas las versiones seleccionadas y sus revisiones vigentes; la ejecución anterior se conserva.</p>
    <div className="analysis-results">{job.cases.map((caso,i)=><section className="simulation-chat" key={i} aria-label={`Conversación del caso ${i+1}`}>
      <header className="simulation-chat__header"><div className="simulation-avatar">IA</div><div><h3>Asistente Académico UNIANDES</h3><small>Caso {i+1} · {job.model} · {job.versions.length} versiones en comparación</small></div></header>
      <div className="simulation-chat__messages">
        <p className="simulation-question"><span>TÚ · CASO {i+1}</span>{caso.question}</p>
        {Object.keys(caso.contexto??{}).length>0&&<p className="simulation-context">Datos de la consulta: {Object.entries(caso.contexto??{}).map(([k,v])=>`${k}: ${v}`).join(' · ')}</p>}
        <div className="simulation-answers">{job.versions.map(version=>{
          const row=job.results.find(r=>r.case===i+1&&r.version===version);
          const revision=row?.prompt_revision??job.prompts?.find(p=>p.version===version)?.revision;
          return <article className="simulation-answer" key={version}>
            <div className="simulation-answer__tag"><h4>ASISTENTE · V{version}{revision?` · r${revision}`:''}</h4><small>{row?.contrato?.estado??row?.status??(running?'pendiente':'sin resultado')}</small></div>
            {row?<>
              <p className={row.status==='error'?'admin-error':'analysis-answer'}>{row.texto||row.error}</p>
              {!!row.contrato?.campos_necesarios?.length&&<button type="button" className="mensaje__completar" disabled={running||busy} onClick={()=>{setError('');setSolicitud(row)}}>Completar datos y repetir comparación</button>}
              {!!row.contrato?.fuentes.length&&<ul>{row.contrato.fuentes.map((f,n)=><li key={n}><a target="_blank" rel="noopener noreferrer" href={f.url.startsWith('/api/sources/')?`${API}${f.url}`:/^https?:\/\//.test(f.url)?f.url:undefined}>{f.titulo} · {f.seccion}</a></li>)}</ul>}
              {row.contrato?.requiere_revision_humana&&<p className="admin-hint">Confirma esta orientación con Secretaría Académica.</p>}
              <div className="analysis-stats"><span>{row.modelo||job.model}</span><span>{row.segundos.toFixed(2)} s</span><span>Entrada: {row.tokens_entrada??'N/D'}</span><span>Salida: {row.tokens_salida??'N/D'}</span><span>Total: {row.tokens_total??'N/D'}</span></div>
              <details><summary>Huella del prompt</summary><code>{row.prompt_sha256}</code></details>
              {row.salida_modelo&&<details><summary>Salida original del modelo</summary><pre>{row.salida_modelo}</pre></details>}
            </>:<div className="simulation-thinking">{running?<><i/><i/><i/> Esperando orientación…</>:'No se generó una respuesta para esta versión.'}</div>}
          </article>;
        })}</div>
        {caso.expected&&<details><summary>Referencia esperada para la evaluación</summary><p>{caso.expected}</p></details>}
      </div>
    </section>)}</div>
  </>;
}

import { useState } from 'react';
import type { Paso } from './api';
import './ayuda-proceso.css';
const estados:Record<string,string>={completed:'Realizado',skipped:'Omitido',error:'Error / respaldo',pending:'Pendiente',running:'En curso'};

export default function Proceso({titulo,pasos}:{titulo:string;pasos:Paso[]}){
  const [seleccion,setSeleccion]=useState(0);
  const indice=Math.min(seleccion,Math.max(0,pasos.length-1));
  const actual=pasos[indice];
  if(!actual)return null;
  return <section className="process" aria-label={titulo}><h3>{titulo}</h3><p>Selecciona un nodo o un paso para explorar la misma etapa. Los estados y cifras proceden del backend; no representan razonamiento privado del modelo.</p>
    <div className="process__graph" role="group" aria-label={`Diagrama: ${titulo}`}>
      {pasos.map((paso,i)=><div className="process__branch" key={paso.id}>
        <button type="button" className={`process__node process__node--${paso.status}`} aria-label={`Nodo ${i+1}: ${paso.title}`} aria-pressed={indice===i} onClick={()=>setSeleccion(i)}><span>{i+1}</span><b>{paso.title}</b><small>{estados[paso.status]??paso.status}</small></button>
        {i<pasos.length-1&&<svg className="process__edge" aria-hidden="true" viewBox="0 0 40 16"><path d="M0 8h36m-7-6 7 6-7 6"/></svg>}
      </div>)}
    </div>
    <div className="process__body"><ol className="process__steps">{pasos.map((paso,i)=><li key={paso.id}><button type="button" aria-label={`${i+1} ${paso.title}`} aria-current={indice===i?'step':undefined} onClick={()=>setSeleccion(i)}><span>{i+1}</span>{paso.title}</button></li>)}</ol>
      <article className="process__detail" aria-live="polite"><p className="admin-eyebrow">PASO {indice+1} · {estados[actual.status]??actual.status}</p><h4>{actual.title}</h4><p>{actual.description}</p>{Object.keys(actual.details??{}).length>0&&<dl>{Object.entries(actual.details??{}).map(([k,v])=><div key={k}><dt>{k.replaceAll('_',' ')}</dt><dd>{v===null?'N/D':String(v)}</dd></div>)}</dl>}</article>
    </div>
  </section>;
}

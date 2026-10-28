import { useEffect, useId, useRef, useState, type ReactNode } from 'react';
import './ayuda-proceso.css';

export function Ayuda({titulo,que,configurar,resultado}:{titulo:string;que:string;configurar:string;resultado:string}){
  const [abierta,setAbierta]=useState(false);
  const [position,setPosition]=useState<{top?:number;bottom?:number;maxHeight?:number}>({top:80});
  const boton=useRef<HTMLButtonElement>(null);
  const cierre=useRef<ReturnType<typeof setTimeout>|null>(null);
  useEffect(()=>()=>{if(cierre.current)clearTimeout(cierre.current)},[]);
  const id=useId();
  function abrir(){if(cierre.current)clearTimeout(cierre.current);const rect=boton.current?.getBoundingClientRect();if(rect){const bajo=window.innerHeight-rect.bottom-24,arriba=rect.top-24;setPosition(bajo>=340||bajo>=arriba?{top:Math.max(16,rect.bottom+8),maxHeight:Math.max(80,bajo)}:{bottom:Math.max(16,window.innerHeight-rect.top+8),maxHeight:Math.max(80,arriba)})}setAbierta(true)}
  return <span className="admin-help" onMouseEnter={abrir} onMouseLeave={()=>{cierre.current=setTimeout(()=>{if(document.activeElement!==boton.current)setAbierta(false)},180)}} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget as Node))setAbierta(false)}} onKeyDown={e=>{if(e.key==='Escape'){setAbierta(false);e.stopPropagation()}}}>
    <button ref={boton} type="button" className="admin-help__boton" aria-label={`Ayuda: ${titulo}`} aria-expanded={abierta} aria-controls={id} aria-describedby={abierta?id:undefined} onFocus={abrir} onClick={abrir}>?</button>
    {abierta&&<span id={id} role="tooltip" style={position} className="admin-help__panel"><strong>{titulo}</strong><span><b>¿Para qué sirve?</b>{que}</span><span><b>Cómo configurarlo</b>{configurar}</span><span><b>Qué obtendrás</b>{resultado}</span></span>}
  </span>;
}

export function Explicacion({titulo,children}:{titulo:string;children:ReactNode}){
  return <aside className="admin-explanation" aria-label={titulo}><div className="admin-explanation__icono" aria-hidden="true">i</div><div><h3>{titulo}</h3>{children}</div></aside>;
}

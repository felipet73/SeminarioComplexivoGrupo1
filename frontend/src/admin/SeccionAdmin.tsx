import { useId, useState, type ReactNode } from 'react';
import './secciones.css';

export default function SeccionAdmin({titulo,subtitulo,acciones,children,abierta,cambiarAbierta,className=''}:{
  titulo:string;subtitulo?:string;acciones?:ReactNode;children:ReactNode;
  abierta?:boolean;cambiarAbierta?:(valor:boolean)=>void;className?:string;
}){
  const [local,setLocal]=useState(true);
  const open=abierta??local;
  const id=useId();
  return <section className={`admin-card admin-fold ${className}`} aria-labelledby={`${id}-titulo`}>
    <div className="admin-card__heading admin-fold__heading">
      <div>{subtitulo&&<p className="admin-eyebrow">{subtitulo}</p>}<h2 id={`${id}-titulo`}>{titulo}</h2></div>
      <div className="admin-fold__acciones">{acciones}<button type="button" className="admin-fold__toggle" aria-expanded={open} aria-controls={id} aria-label={`${open?'Contraer':'Expandir'} ${titulo}`} onClick={()=>{setLocal(!open);cambiarAbierta?.(!open)}}><span>{open?'Contraer':'Expandir'}</span><svg aria-hidden="true" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg></button></div>
    </div>
    <div id={id} className={`admin-fold__panel${open?' admin-fold__panel--abierto':''}`} aria-hidden={!open} inert={!open}><div className="admin-fold__interior"><div className="admin-fold__contenido">{children}</div></div></div>
  </section>;
}

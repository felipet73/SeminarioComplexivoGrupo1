import { useEffect, useRef } from 'react';
import type { CampoNecesario } from './api';
import type { Contexto } from './ContextoAcademico';
import './campos-necesarios.css';

export default function CamposNecesarios({respuesta,campos,ocupado,error,consultar,salir}:{
  respuesta:string;campos:CampoNecesario[];ocupado:boolean;error:string;
  consultar:(valores:Contexto)=>void;salir:()=>void;
}) {
  const dialogo=useRef<HTMLDialogElement>(null);
  const procesando=useRef(ocupado);
  procesando.current=ocupado;
  useEffect(()=>{
    const anterior=document.activeElement as HTMLElement|null;
    const dialog=dialogo.current!;
    const overflow=document.body.style.overflow;
    dialog.showModal();
    document.body.style.overflow='hidden';
    return ()=>{dialog.close();document.body.style.overflow=overflow;anterior?.focus();};
  },[]);
  return <dialog ref={dialogo} className="datos-dialogo" aria-labelledby="datos-titulo" aria-describedby="datos-respuesta" onCancel={e=>{e.preventDefault();if(!procesando.current)salir();}}>
    <p className="eyebrow">UNA ORIENTACIÓN MÁS PRECISA</p>
    <h2 id="datos-titulo">Completemos tu consulta</h2>
    <p id="datos-respuesta" className="datos-dialogo__respuesta">{respuesta}</p>
    <p className="datos-dialogo__nota">Campos necesarios para volver a consultar. No incluyas datos personales sensibles. Las opciones son orientativas.</p>
    <form onSubmit={e=>{
      e.preventDefault();
      if(ocupado)return;
      const form=e.currentTarget;
      const datos=new FormData(form), valores:Contexto={};
      for(const campo of campos){
        const control=form.elements.namedItem(campo.campo) as HTMLInputElement|HTMLSelectElement;
        const valor=String(datos.get(campo.campo)??'').trim();
        const valido=valor.length>=2 && valor.length<=campo.max_length && (campo.tipo!=='select'||campo.opciones.includes(valor));
        control.setCustomValidity(valido?'':'Completa este campo con un valor válido.');
        valores[campo.campo]=valor;
      }
      if(form.reportValidity())consultar(valores);
    }}>
      <fieldset disabled={ocupado} className="datos-dialogo__campos"><legend>Campos necesarios</legend>
        {campos.map(campo=><label key={campo.campo} htmlFor={`dato-${campo.campo}`}>{campo.etiqueta}<span aria-hidden="true"> *</span>
          {campo.tipo==='select'?<select id={`dato-${campo.campo}`} name={campo.campo} required defaultValue="" onChange={e=>e.currentTarget.setCustomValidity('')}><option value="" disabled>Selecciona una opción</option>{campo.opciones.map(opcion=><option key={opcion}>{opcion}</option>)}</select>:<input id={`dato-${campo.campo}`} name={campo.campo} required minLength={2} maxLength={campo.max_length} autoComplete="off" onChange={e=>e.currentTarget.setCustomValidity('')}/>}
        </label>)}
      </fieldset>
      {error&&!ocupado&&<p role="alert" className="error-consulta">{error} Tus datos se conservan; puedes volver a intentar.</p>}
      {ocupado&&<p role="status" className="datos-dialogo__espera">Preparando tu orientación con los datos ingresados…</p>}
      <div className="datos-dialogo__acciones"><button type="button" disabled={ocupado} onClick={salir}>Salir sin consultar</button><button type="submit" disabled={ocupado}>{ocupado?'Consultando…':'Volver a consultar'}</button></div>
    </form>
  </dialog>;
}

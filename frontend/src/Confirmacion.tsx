import { useState } from 'react';
import { API, type AccionPendiente } from './api';

export default function Confirmacion({accion}:{accion:AccionPendiente}) {
  const [busy,setBusy]=useState(false);
  const [result,setResult]=useState('');
  const [error,setError]=useState('');
  async function decidir(aprobar:boolean) {
    setBusy(true);setError('');
    try {
      const response=await fetch(`${API}/api/herramientas/agente/confirmar/${encodeURIComponent(accion.id)}`, {
        method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:accion.token,aprobar}),
      });
      const data=await response.json();
      if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'No se pudo procesar la decisión.');
      setResult(data.mensaje);
    } catch(e) {setError((e as Error).message)} finally {setBusy(false)}
  }
  return <section aria-label="Confirmar borrador de solicitud" className="confirmacion">
    <b>Borrador de solicitud de tutor</b>
    <p>{accion.alcance}</p>
    <dl>{Object.entries(accion.argumentos).map(([campo,valor])=><div key={campo}><dt>{campo}</dt><dd>{valor}</dd></div>)}</dl>
    <small>Disponible hasta {new Date(accion.vence).toLocaleString('es-EC')}</small>
    {result?<p role="status">{result}</p>:<div>
      <button type="button" disabled={busy} onClick={()=>void decidir(true)}>Confirmar y guardar borrador</button>{' '}
      <button type="button" disabled={busy} onClick={()=>void decidir(false)}>Cancelar propuesta</button>
    </div>}
    {error&&<p role="alert">{error}</p>}
  </section>;
}

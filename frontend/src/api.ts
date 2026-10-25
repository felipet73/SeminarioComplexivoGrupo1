export type Estado = 'respuesta'|'abstencion'|'aclaracion'|'rechazo';
export type CampoNecesario = {campo:keyof import('./ContextoAcademico').Contexto;etiqueta:string;tipo:'texto'|'select';opciones:string[];max_length:number};
export type Fuente = {titulo:string;seccion:string;url:string;version?:string;pagina?:number;fragmento_id?:string};
export type Respuesta = {respuesta:string;estado:Estado;requiere_revision_humana:boolean;fuentes:Fuente[];campos_necesarios?:CampoNecesario[];modelo_utilizado:string|null;fallback_activado:boolean;tiempo_segundos:number};
export const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';
export class ApiError extends Error { constructor(public status:number, message:string, public retryAfter?:number){super(message)} }
export type ModeloPreferido = 'gemini' | 'openai';
export async function enviarConsulta(pregunta:string, modeloPreferido:ModeloPreferido, onToken:(token:string)=>void, contexto: import('./ContextoAcademico').Contexto = {}):Promise<Respuesta>{
 const response=await fetch(`${API}/api/chat/stream`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...contexto,pregunta,modelo_preferido:modeloPreferido})});
 if(!response.ok){const body=await response.json().catch(()=>({}));throw new ApiError(response.status,body.detail??'No se pudo procesar la consulta.',Number(response.headers.get('Retry-After')??0)||undefined)}
 if(!response.body) throw new ApiError(503,'La respuesta no tiene flujo disponible.');
 const reader=response.body.getReader(), decoder=new TextDecoder(); let buffer='', done:Respuesta|undefined;
 for(;;){const item=await reader.read(); if(item.done) break; buffer+=decoder.decode(item.value,{stream:true}); const events=buffer.split('\n\n'); buffer=events.pop()??''; for(const event of events){const data=event.split('\n').find(line=>line.startsWith('data:'))?.slice(5).trim(); if(!data)continue; if(event.includes('event: token'))onToken(JSON.parse(data).texto); if(event.includes('event: done'))done=JSON.parse(data)}}
 if(!done) throw new ApiError(503,'El flujo terminó sin una respuesta válida.'); return done;
}

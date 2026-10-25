export type Prompt={version:number;content:string;description:string;revision:number;updated:string};
export type Doc={id:string;name:string;title:string;kind:'normativa'|'informativo';source_url:string;valid_from:string;valid_to:string|null;approved:boolean;enabled:boolean;notes:string;revision:number;indexed_revision:number|null;chunks:number;sha256:string;updated:string;eligible?:boolean;index_current?:boolean};
export type Config={active_prompt:number;chunk_size:number;overlap:number;top_k:number;strategy:'lexical'|'hybrid';embedding_model:string;min_similarity:number;revision:number};
export type Bootstrap={prompts:Prompt[];documents:Doc[];config:Config;reference_cases:Case[];models:{id:string;name:string;configured:boolean}[]};
export type Chunk={id:string;title:string;section:string;page:number;text:string;revision:number;score?:number};
export type Case={question:string;expected:string;contexto?:import('../ContextoAcademico').Contexto};
export type Result={version:number;prompt_revision:number;case:number;question:string;status:string;texto?:string;modelo?:string;fallback?:boolean;segundos:number;tokens_entrada?:number|null;tokens_salida?:number|null;tokens_total?:number|null;error?:string;prompt_sha256?:string;contrato?:import('../api').Respuesta;salida_modelo?:string|null};
export type Job={id:string;status:string;created:string;model:string;versions:number[];use_rag?:boolean;prompts?:Prompt[];cases:Case[];results:Result[];review?:{texto:string;modelo:string;segundos:number;tokens_total:number|null};review_error?:string;error?:string};

export async function adminAPI<T>(path:string,body?:unknown):Promise<T>{
  const isForm=body instanceof FormData;
  const response=await fetch(`/api/admin${path}`,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:{'X-Admin-Request':'1',...(!isForm&&body!==undefined?{'Content-Type':'application/json'}:{})},body:body===undefined?undefined:isForm?body:JSON.stringify(body)});
  const data=await response.json().catch(()=>({detail:'Respuesta inesperada del servidor.'}));
  if(!response.ok){
    if(response.status===401&&path!=='/login'&&path!=='/session')window.dispatchEvent(new Event('admin-session-expired'));
    throw new Error(typeof data.detail==='string'?data.detail:'Revisa los campos enviados.');
  }
  return data;
}

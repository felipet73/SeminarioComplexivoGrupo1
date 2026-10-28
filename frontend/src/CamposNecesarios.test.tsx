import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { afterEach, beforeAll, describe, expect, it, vi } from 'vitest';
import App from './App';
import { enviarConsulta, type Respuesta } from './api';

vi.mock('./api',async importOriginal=>({...await importOriginal<typeof import('./api')>(),enviarConsulta:vi.fn()}));
const enviar=vi.mocked(enviarConsulta);
const aclaracion:Respuesta={respuesta:'Para orientarte, indica tu carrera y nivel.',estado:'aclaracion',requiere_revision_humana:true,fuentes:[],modelo_utilizado:'test',fallback_activado:false,tiempo_segundos:.1,
  campos_necesarios:[{campo:'carrera',etiqueta:'Carrera',tipo:'texto',opciones:[],max_length:120},{campo:'curso',etiqueta:'Nivel / curso',tipo:'select',opciones:['Primer nivel','Noveno nivel'],max_length:80}]};
beforeAll(()=>{
  HTMLDialogElement.prototype.showModal=function(){this.setAttribute('open','');};
  HTMLDialogElement.prototype.close=function(){this.removeAttribute('open');};
});
afterEach(()=>{cleanup();vi.resetAllMocks();});
async function preguntar(){
  enviar.mockResolvedValueOnce(aclaracion);
  render(<App/>);
  fireEvent.change(screen.getByLabelText('Tu consulta'),{target:{value:'¿Cómo consultar mi titulación?'}});
  fireEvent.submit(screen.getByLabelText('Tu consulta').closest('form')!);
  const dialog=await screen.findByRole('dialog',{}, {timeout:5000});
  await waitFor(()=>expect(within(dialog).getByRole('button',{name:'Volver a consultar'})).toBeEnabled(),{timeout:5000});
  return dialog;
}
describe('datos faltantes de la consulta',()=>{
  it('muestra la respuesta en chat y popup, valida y reenvía la pregunta con contexto',async()=>{
    const dialog=await preguntar();
    expect(screen.getAllByText(aclaracion.respuesta)).toHaveLength(2);
    const form=within(dialog).getByRole('button',{name:'Volver a consultar'}).closest('form')!;
    fireEvent.submit(form);
    expect(enviar).toHaveBeenCalledTimes(1);
    fireEvent.change(within(dialog).getByLabelText(/Carrera/),{target:{value:'   '}});
    fireEvent.change(within(dialog).getByLabelText(/Nivel \/ curso/),{target:{value:'Noveno nivel'}});
    fireEvent.submit(form);
    expect(enviar).toHaveBeenCalledTimes(1);
    fireEvent.change(within(dialog).getByLabelText(/Carrera/),{target:{value:' Software '}});
    enviar.mockResolvedValueOnce({...aclaracion,respuesta:'Gracias por los datos. Consulta Secretaría.',estado:'abstencion',campos_necesarios:[]});
    fireEvent.submit(form);
    await waitFor(()=>expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    expect(enviar.mock.calls[1][0]).toBe('¿Cómo consultar mi titulación?');
    expect(enviar.mock.calls[1][1]).toBe('gemini');
    expect(enviar.mock.calls[1][3]).toMatchObject({carrera:'Software',curso:'Noveno nivel'});
    expect(screen.queryByRole('button',{name:/Completar datos necesarios/})).not.toBeInTheDocument();
  });
  it('salir no consulta ni borra la respuesta del chat',async()=>{
    const dialog=await preguntar();
    fireEvent.click(within(dialog).getByRole('button',{name:'Salir sin consultar'}));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByText(aclaracion.respuesta)).toBeInTheDocument();
    expect(enviar).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole('button',{name:/Completar datos necesarios/}));
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    expect(enviar).toHaveBeenCalledTimes(1);
  });
  it('conserva los campos y permite reintentar si falla el proveedor',async()=>{
    const dialog=await preguntar();
    fireEvent.change(within(dialog).getByLabelText(/Carrera/),{target:{value:'Software'}});
    fireEvent.change(within(dialog).getByLabelText(/Nivel \/ curso/),{target:{value:'Noveno nivel'}});
    enviar.mockRejectedValueOnce(new Error('Servicio no disponible'));
    fireEvent.submit(within(dialog).getByRole('button',{name:'Volver a consultar'}).closest('form')!);
    expect(await within(dialog).findByRole('alert')).toHaveTextContent('Servicio no disponible');
    expect(within(dialog).getByLabelText(/Carrera/)).toHaveValue('Software');
  });
});

import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import Metricas from './Metricas';
import ContextoAcademico from './ContextoAcademico';

afterEach(()=>{cleanup();vi.unstubAllGlobals()});

it('permite elegir nivel y comunica el cambio del contexto',()=>{
  const cambiar=vi.fn();
  render(<ContextoAcademico valor={{carrera:'Software'}} cambiar={cambiar} disabled={false}/>);
  fireEvent.click(screen.getByRole('button', {name:/Personaliza tu orientación/}));
  fireEvent.change(screen.getByLabelText('Nivel / curso'),{target:{value:'Octavo nivel'}});
  expect(cambiar).toHaveBeenCalledWith({carrera:'Software',curso:'Octavo nivel'});
});

it('carga el dashboard vacío sin inventar valores',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({
    ventana:'Últimos eventos',consultas:0,llamadas:0,errores:0,fallbacks:0,latencia_media:0,latencia_p95:0,
    tokens_entrada:0,tokens_salida:0,tokens_total:0,sin_uso_reportado:0,tipos_respuesta:{},por_modelo:{},por_error:{},recientes:[],
  }),{status:200})));
  render(<Metricas/>);
  expect(await screen.findByText('Actividad reciente')).toBeInTheDocument();
  expect(screen.getByText(/Aún no hay eventos/)).toBeInTheDocument();
});

it('muestra el error de conexión del dashboard',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('Backend sin conexión')));
  render(<Metricas/>);
  expect(await screen.findByRole('alert')).toHaveTextContent('Backend sin conexión');
});

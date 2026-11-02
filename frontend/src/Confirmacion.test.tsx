import { afterEach, expect, test, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import Confirmacion from './Confirmacion';

afterEach(()=>{cleanup();vi.unstubAllGlobals()});
test('muestra argumentos exactos y solo decide al pulsar confirmar',async()=>{
  const fetcher=vi.fn().mockResolvedValue({ok:true,json:async()=>({mensaje:'Borrador guardado localmente.'})});
  vi.stubGlobal('fetch',fetcher);
  render(<Confirmacion accion={{id:'accion',token:'capacidad-secreta',herramienta:'registrar_solicitud_tutor',argumentos:{carrera:'Software',modalidad:'Proyecto',tema:'RAG educativo'},vence:'2026-11-01T00:00:00Z',alcance:'Solo demostración local'}}/>);
  expect(screen.getByText('RAG educativo')).toBeInTheDocument();
  expect(fetcher).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Confirmar y guardar borrador'}));
  expect(await screen.findByRole('status')).toHaveTextContent('Borrador guardado localmente.');
  expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual({token:'capacidad-secreta',aprobar:true});
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});

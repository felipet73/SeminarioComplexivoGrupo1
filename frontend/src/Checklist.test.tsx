import { afterEach, expect, test } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import Checklist from './Checklist';
import type { ChecklistAcademico } from './api';

afterEach(cleanup);
test('las marcas personales no cambian el estado de cumplimiento del requisito', () => {
  const lista: ChecklistAcademico = {perfil_declarado:'grado', perfil_interpretado:{nivel:'grado'}, datos_por_confirmar:['modalidad_titulacion'],
    completo:false, advertencia:'No acredita cumplimiento.', items:[{requisito:'Aprobar integración curricular.', documento:'RRA',
    fragmento_id:'rra-1', seccion:'Artículo 26', pagina:8, estado:'pendiente_de_verificar'}]};
  render(<Checklist lista={lista}/>);
  expect(screen.getByText(/RRA · Artículo 26 · pág. 8/)).toBeInTheDocument();
  expect(screen.getByText(/modalidad de titulación/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('checkbox'));
  expect(screen.getByRole('checkbox')).toBeChecked();
  expect(screen.getByText(/Pendiente de verificar/)).toBeInTheDocument();
  expect(lista.completo).toBe(false);
});

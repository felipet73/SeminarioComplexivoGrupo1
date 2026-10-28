import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import SeccionAdmin from './SeccionAdmin';

afterEach(cleanup);
it('contrae sin desmontar ni perder campos y expone el estado accesible',()=>{
  render(<SeccionAdmin titulo="Sección de prueba"><label>Contenido<input defaultValue="Original"/></label></SeccionAdmin>);
  const campo=screen.getByLabelText('Contenido');
  fireEvent.change(campo,{target:{value:'Borrador sin guardar'}});
  const toggle=screen.getByRole('button',{name:'Contraer Sección de prueba'});
  const panel=document.getElementById(toggle.getAttribute('aria-controls')!)!;
  expect(toggle).toHaveAttribute('aria-expanded','true');
  fireEvent.click(toggle);
  expect(panel).toHaveAttribute('aria-hidden','true');
  expect(panel).toHaveAttribute('inert');
  expect(campo).toHaveValue('Borrador sin guardar');
  fireEvent.click(screen.getByRole('button',{name:'Expandir Sección de prueba'}));
  expect(panel).toHaveAttribute('aria-hidden','false');
  expect(panel).not.toHaveAttribute('inert');
  expect(screen.getByLabelText('Contenido')).toHaveValue('Borrador sin guardar');
});

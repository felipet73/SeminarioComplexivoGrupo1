import { cleanup, fireEvent, render, screen, within } from '@testing-library/react';
import { afterEach, expect, it } from 'vitest';
import Proceso from './Proceso';
import { Ayuda } from './Ayuda';
afterEach(cleanup);
it('sincroniza nodos, pasos y explicación con cifras reales',()=>{
  render(<Proceso titulo="Prueba" pasos={[{id:'a',title:'Filtrar',description:'Solo fuentes vigentes.',status:'completed',details:{fuentes:2}},{id:'b',title:'Vectores',description:'Ruta no ejecutada.',status:'skipped',details:{vectores:0}}]}/>);
  fireEvent.click(screen.getByRole('button',{name:'Nodo 2: Vectores'}));
  expect(screen.getByRole('button',{name:'Nodo 2: Vectores'})).toHaveAttribute('aria-pressed','true');
  expect(screen.getByText('Ruta no ejecutada.')).toBeInTheDocument();
  expect(screen.getByRole('button',{name:'2 Vectores'})).toHaveAttribute('aria-current','step');
  fireEvent.click(screen.getByRole('button',{name:'1 Filtrar'}));
  expect(screen.getByRole('button',{name:'Nodo 1: Filtrar'})).toHaveAttribute('aria-pressed','true');
  expect(screen.getByText('Solo fuentes vigentes.')).toBeInTheDocument();
});
it('abre ayuda con teclado o clic y cierra con Escape',()=>{
  render(<Ayuda titulo="Top-k" que="Limita evidencia." configurar="De 1 a 10." resultado="Fragmentos pertinentes."/>);
  const button=screen.getByRole('button',{name:'Ayuda: Top-k'});
  fireEvent.focus(button);
  expect(within(screen.getByRole('tooltip')).getByText('De 1 a 10.')).toBeInTheDocument();
  fireEvent.keyDown(button,{key:'Escape'});
  expect(screen.queryByRole('tooltip')).not.toBeInTheDocument();
  fireEvent.click(button);
  expect(screen.getByRole('tooltip')).toBeInTheDocument();
});

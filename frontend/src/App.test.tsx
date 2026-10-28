import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import App from './App';

it('muestra el encabezado del asistente', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: 'Tu próximo paso académico empieza con una buena orientación.' })).toBeInTheDocument();
  expect(screen.getByLabelText('Preguntas sugeridas')).toBeInTheDocument();
  expect(screen.queryByText('Pruebas rápidas:')).not.toBeInTheDocument();
  expect(screen.queryByRole('button',{name:/Jailbreak/})).not.toBeInTheDocument();
});

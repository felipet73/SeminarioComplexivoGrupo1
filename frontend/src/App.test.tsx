import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import App from './App';

it('muestra el encabezado del asistente', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: 'Tu próximo paso académico empieza con una buena orientación.' })).toBeInTheDocument();
});

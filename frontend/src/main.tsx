import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import Metricas from './Metricas';
import Admin from './admin/Admin';

const route = window.location.pathname.replace(/\/+$/, '').toLowerCase();
const Pagina = route === '/admin' ? Admin : route === '/metricas' ? Metricas : App;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Pagina />
  </StrictMode>
);
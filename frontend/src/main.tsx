import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import Metricas from './Metricas';
const Pagina = window.location.pathname.replace(/\/$/, '') === '/metricas' ? Metricas : App;
createRoot(document.getElementById('root')!).render(<StrictMode><Pagina/></StrictMode>);

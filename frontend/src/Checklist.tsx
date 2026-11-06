import { useState } from 'react';
import type { ChecklistAcademico } from './api';
import './checklist.css';

export default function Checklist({ lista }: { lista: ChecklistAcademico }) {
  const [revisados, setRevisados] = useState<Set<number>>(new Set());
  return <section aria-label="Lista de verificación académica" className="checklist-academico">
    <h3>Lista de verificación</h3>
    <p>Perfil declarado: {lista.perfil_declarado}</p>
    <p>{lista.advertencia}</p>
    {lista.datos_por_confirmar?.length > 0 && <p>Por confirmar: {lista.datos_por_confirmar.map(c => c === 'nivel' ? 'nivel de estudios' : 'modalidad de titulación').join(', ')}.</p>}
    {!lista.items.length && <p>No se recuperaron requisitos suficientes para elaborar la lista de este perfil.</p>}
    <ul>{lista.items.map((item, i) => <li key={`${item.fragmento_id}-${i}`}>
      <label><input type="checkbox" checked={revisados.has(i)} onChange={() => setRevisados(prev => {
        const next = new Set(prev); if (next.has(i)) next.delete(i); else next.add(i); return next;
      })}/> Revisé este pasaje</label>
      <blockquote>{item.requisito}</blockquote>
      <small>{item.documento} · {item.seccion} · pág. {item.pagina} · Pendiente de verificar</small>
    </li>)}</ul>
    <small>Las marcas son personales y se pierden al cerrar la página. No certifican requisitos cumplidos.</small>
  </section>;
}

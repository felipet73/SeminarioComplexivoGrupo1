import { useId, useState } from 'react';
import './contexto.css';

export type Contexto = Partial<Record<'carrera'|'curso'|'modalidad'|'periodo'|'jornada'|'tema'|'objetivo'|'sede'|'modalidad_titulacion', string>>;

const opciones = {
  curso: ['Primer nivel', 'Segundo nivel', 'Tercer nivel', 'Cuarto nivel', 'Quinto nivel', 'Sexto nivel', 'Séptimo nivel', 'Octavo nivel', 'Noveno nivel', 'Décimo nivel', 'Egresado/a'],
  modalidad: ['Presencial', 'En línea', 'Semipresencial', 'A distancia'],
  jornada: ['Matutina', 'Vespertina', 'Nocturna', 'Fin de semana'],
  tema: ['Titulación', 'Matrícula', 'Prácticas preprofesionales', 'Vinculación', 'Homologación', 'Certificados', 'Normativa académica'],
  objetivo: ['Entender el proceso', 'Preparar preguntas para Secretaría', 'Organizar mis próximos pasos', 'Identificar información que me falta', 'Explicar términos académicos'],
};

export default function ContextoAcademico({valor, cambiar, disabled}: {valor: Contexto; cambiar:(v:Contexto)=>void; disabled:boolean}) {
  const [abierto, setAbierto] = useState(false);
  const panelId = useId();
  const cantidad = Object.values(valor).filter(v => v?.trim()).length;
  const actualizar = (campo: keyof Contexto, texto: string) => cambiar({...valor, [campo]:texto});
  return <section className="contexto" aria-label="Contexto académico">
    <h3 className="contexto__encabezado"><button type="button" className="contexto__titulo contexto__toggle" aria-expanded={abierto} aria-controls={panelId} onClick={() => setAbierto(actual => !actual)}>
      <span className="paso" aria-hidden="true">01</span>
      <span className="contexto__introduccion"><span className="contexto__nombre">Personaliza tu orientación</span><span className="contexto__subtitulo">Añade detalles para una ayuda más cercana a ti.</span></span>
      <span className="etiqueta">{cantidad ? `${cantidad} ${cantidad === 1 ? 'dato' : 'datos'}` : 'Opcional'}</span>
      <svg className="contexto__flecha" aria-hidden="true" viewBox="0 0 24 24"><path d="m7 10 5 5 5-5"/></svg>
    </button></h3>
    <div id={panelId} className={`contexto__panel${abierto ? ' contexto__panel--abierto' : ''}`} aria-hidden={!abierto} inert={!abierto}><div className="contexto__interior"><div className="contexto__contenido">
    <fieldset disabled={disabled} className="contexto__campos"><legend className="sr-only">Detalles académicos</legend>
      <label>Carrera<input list="carreras" value={valor.carrera || ''} onChange={e=>actualizar('carrera',e.target.value)} maxLength={120} placeholder="Escribe o selecciona"/><datalist id="carreras"><option value="Software"/><option value="Otra carrera"/></datalist></label>
      <label>Nivel / curso<select value={valor.curso || ''} onChange={e=>actualizar('curso',e.target.value)}><option value="">Sin especificar</option>{opciones.curso.map(o=><option key={o}>{o}</option>)}</select></label>
      <label>Modalidad de estudios<select value={valor.modalidad || ''} onChange={e=>actualizar('modalidad',e.target.value)}><option value="">Sin especificar</option>{opciones.modalidad.map(o=><option key={o}>{o}</option>)}</select></label>
      <label>Período académico<input value={valor.periodo || ''} onChange={e=>actualizar('periodo',e.target.value)} maxLength={80} placeholder="Ej.: 2026–2027"/></label>
      <label>Sede / extensión<input value={valor.sede || ''} onChange={e=>actualizar('sede',e.target.value)} maxLength={120} placeholder="Indica tu sede si aplica"/></label>
      <label>Modalidad de titulación<select value={valor.modalidad_titulacion || ''} onChange={e=>actualizar('modalidad_titulacion',e.target.value)}><option value="">Por definir / no aplica</option><option>Examen complexivo</option><option>Trabajo de integración curricular</option><option>Otra modalidad (precisar en la consulta)</option></select></label>
      <label>Jornada<select value={valor.jornada || ''} onChange={e=>actualizar('jornada',e.target.value)}><option value="">Sin especificar</option>{opciones.jornada.map(o=><option key={o}>{o}</option>)}</select></label>
      <label>Tema de consulta<select value={valor.tema || ''} onChange={e=>actualizar('tema',e.target.value)}><option value="">Sin especificar</option>{opciones.tema.map(o=><option key={o}>{o}</option>)}</select></label>
      <label className="campo-amplio">¿Qué ayuda necesitas?<select value={valor.objetivo || ''} onChange={e=>actualizar('objetivo',e.target.value)}><option value="">Selecciona una opción</option>{opciones.objetivo.map(o=><option key={o}>{o}</option>)}</select></label>
    </fieldset><p className="contexto__nota">Las opciones son orientativas. Usa el nombre de carrera y período de tu matrícula; evita incluir nombres, cédulas o notas.</p>
    </div></div></div>
  </section>;
}

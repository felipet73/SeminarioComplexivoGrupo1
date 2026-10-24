import { Activity, useActionState, useEffect, useEffectEvent, useOptimistic, useRef, useState } from 'react';
import assistantImage from '../assets/AsistenteIAUNIANDES.png';
import { ApiError, enviarConsulta, type ModeloPreferido, type Respuesta } from './api';
import './styles.css';
import './enhancements.css';
import './thinking.css';
import ContextoAcademico, { type Contexto } from './ContextoAcademico';

type Mensaje = { id: string; rol: 'usuario' | 'asistente'; texto: string; meta?: Respuesta };
type EstadoFormulario = { error: string };

const sugerencias = [
  'Quiero orientarme sobre mi modalidad de titulación',
  '¿Qué debo consultar sobre prácticas preprofesionales?',
  'Necesito saber qué información llevar a Secretaría',
];

function IconoEnviar() {
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m21 3-7.3 18-2.9-7.8L3 10.3 21 3Zm-9.4 8.5 2 5.3 4.1-10.2-10.2 4.1 4.1 1.7Z" /></svg>;
}

export default function App() {
  const [mensajes, setMensajes] = useState<Mensaje[]>([
    { id: 'bienvenida', rol: 'asistente', texto: 'Hola, estoy aquí para orientarte. Cuéntame qué trámite académico deseas consultar y te ayudaré a preparar tus siguientes pasos.' },
  ]);
  const [optimistas, agregarOptimista] = useOptimistic(mensajes, (estado, mensaje: Mensaje) => estado.some(actual => actual.id === mensaje.id) ? estado : [...estado, mensaje]);
  const [progreso, setProgreso] = useState('');
  const [modelo, setModelo] = useState<ModeloPreferido>('gemini');
  const [contexto, setContexto] = useState<Contexto>({});
  const fin = useRef<HTMLDivElement>(null);

  const desplazar = useEffectEvent(() => {
    if (typeof fin.current?.scrollIntoView === 'function') fin.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  });
  useEffect(() => { desplazar(); }, [optimistas, desplazar]);

  async function enviar(_anterior: EstadoFormulario, formData: FormData): Promise<EstadoFormulario> {
    const pregunta = String(formData.get('pregunta') ?? '').trim();
    if (!pregunta) return { error: 'Escribe una consulta para poder orientarte.' };

    const id = crypto.randomUUID();
    agregarOptimista({ id, rol: 'usuario', texto: pregunta });
    setProgreso('');
    let parcial = '';

    try {
      const final = await enviarConsulta(pregunta, modelo, (token) => { parcial += token; setProgreso(parcial); }, contexto);
      setMensajes((actual) => [...actual, { id, rol: 'usuario', texto: pregunta }, { id: crypto.randomUUID(), rol: 'asistente', texto: final.respuesta, meta: final }]);
      setProgreso('');
      return { error: '' };
    } catch (error) {
      const apiError = error as ApiError;
      return { error: apiError.status === 429 && apiError.retryAfter ? `Demasiadas solicitudes. Intenta de nuevo en ${apiError.retryAfter} segundos.` : apiError.message };
    }
  }

  const [formState, formAction, isPending] = useActionState(enviar, { error: '' });

  return <main className="pagina">
    <header className="barra"><a className="marca" href="#inicio" aria-label="UNIANDES, inicio"><span className="marca__punto" /> UNIANDES <em>·</em> Asistente Académico</a><span className="barra__estado"><i /> Disponible para orientarte</span></header>

    <section id="inicio" className="hero">
      <div className="hero__texto">
        <p className="eyebrow">ORIENTACIÓN ACADÉMICA INTELIGENTE</p>
        <h1>Tu próximo paso académico empieza con una buena orientación.</h1>
        <p className="hero__descripcion">Consulta sobre titulación, matrícula, prácticas, vinculación y otros trámites. Ahora tienes una ayuda clara y cercana al alcance de tu mano.</p>
        <div className="hero__acciones"><a href="#consulta" className="boton boton--primario">Hacer una consulta <span>↓</span></a><p><b>Orientación responsable</b><br />Te acompañamos a verificar cada paso.</p></div>
      </div>
      <div className="hero__imagen"><div className="hero__halo" /><img src={assistantImage} alt="Asistente Académico IA de UNIANDES" /><span className="insignia">UNIANDES<br /><b>Asistente IA</b></span></div>
    </section>

    <section className="beneficios" aria-label="Alcance del asistente">
      <article><span>01</span><h2>Resuelve tus dudas</h2><p>Obtén una guía inicial para entender el trámite que necesitas realizar.</p></article>
      <article><span>02</span><h2>Organiza tu consulta</h2><p>Identifica carrera, modalidad y período que conviene confirmar.</p></article>
      <article><span>03</span><h2>Decide con respaldo</h2><p>Te recomendamos validar requisitos específicos con Secretaría Académica.</p></article>
    </section>

    <section id="consulta" className="zona-chat">
      <aside className="panel-ayuda"><p className="eyebrow">A TU ALCANCE</p><h2>Una consulta hoy puede darte claridad para avanzar mañana.</h2><p>El asistente ofrece orientación general. Para decisiones, plazos, requisitos o documentos oficiales, verifica siempre con los canales institucionales.</p><div className="ayudas"><h3>¿En qué más puedo ayudarte?</h3><ul><li>Explicar términos académicos con ejemplos.</li><li>Preparar preguntas para tu visita a Secretaría.</li><li>Ordenar tus dudas y próximos pasos.</li><li>Identificar qué información necesitas confirmar.</li></ul></div><div className="aviso"><b>Recomendación</b><span>No compartas contraseñas, datos sensibles ni información de terceros.</span></div></aside>

      <div className={`chat${isPending ? ' chat--procesando' : ''}`} aria-label="Asistente Académico UNIANDES" aria-busy={isPending}>
        <ContextoAcademico valor={contexto} cambiar={setContexto} disabled={isPending}/>
        <div className="chat__cabecera"><div className="avatar">IA</div><div><b>Asistente Académico UNIANDES</b><span><i /> En línea · orientación general</span></div><div className="selector-modelo"><label htmlFor="modelo">Modelo</label><select id="modelo" value={modelo} onChange={(event) => setModelo(event.target.value as ModeloPreferido)} disabled={isPending}><option value="gemini">Gemini 3.5 Flash-Lite</option><option value="openai">OpenAI GPT-4.1 mini</option></select></div></div>
        <div className="conversacion" aria-live="polite" aria-label="Conversación">
          {optimistas.map((mensaje) => <article className={`mensaje mensaje--${mensaje.rol}`} key={mensaje.id}><span>{mensaje.rol === 'usuario' ? 'TÚ' : 'ASISTENTE'}</span><p>{mensaje.texto}</p>{mensaje.meta?.modelo_utilizado && <small>Modelo: {mensaje.meta.modelo_utilizado}{mensaje.meta.fallback_activado ? ' · respaldo activado' : ''}</small>}{mensaje.meta?.requiere_revision_humana && <small>Recomendación: confirma esta orientación con Secretaría Académica.</small>}</article>)}
          <Activity mode={isPending ? 'visible' : 'hidden'}>
            <article className="mensaje mensaje--asistente mensaje--pensando">
              <div className="pensando" role="status" aria-live="polite">
                <div className="pensando__emblema" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4L12 3Z"/></svg></div>
                <div className="pensando__texto"><span>ASISTENTE UNIANDES</span><b>Preparando tu orientación<span className="pensando__puntos" aria-hidden="true"><i/><i/><i/></span></b><p>Una respuesta clara merece un momento.</p></div>
              </div>
              <div className="pensando__rastro" aria-hidden="true"><i/><i/><i/></div>
              {progreso && <p className="pensando__respuesta">{progreso}</p>}
            </article>
          </Activity>
          <div ref={fin} />
        </div>
        {formState.error && !isPending && <p role="alert" className="error-consulta">{formState.error} Puedes volver a intentar con el otro modelo.</p>}
        <div className="sugerencias"><span>Prueba con:</span>{sugerencias.map((texto) => <button key={texto} type="button" onClick={() => { const entrada = document.querySelector<HTMLTextAreaElement>('#pregunta'); if (entrada) { entrada.value = texto; entrada.focus(); } }}>{texto}</button>)}</div>
        <form className="formulario" action={formAction}><label className="sr-only" htmlFor="pregunta">Tu consulta</label><textarea id="pregunta" name="pregunta" minLength={3} maxLength={2000} required placeholder="Escribe tu consulta académica…" /><button aria-label="Enviar consulta" disabled={isPending} type="submit"><IconoEnviar /></button></form>
        <p className="chat__nota">Al enviar, aceptas usar este servicio únicamente para orientación académica.</p>
      </div>
    </section>

    <footer>UNIANDES · Universidad Regional Autónoma de Los Andes <span>Información orientativa; no constituye una resolución administrativa.</span></footer>
  </main>;
}

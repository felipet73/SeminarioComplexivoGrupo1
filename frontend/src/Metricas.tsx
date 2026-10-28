import { useEffect, useState } from 'react';
import { API } from './api';
import './styles.css';
import './enhancements.css';

type Evento = { fecha: string; evento: string; request_id?: string; modelo?: string; estado?: string; segundos?: number; error?: string; status?: number; tokens_total?: number; fallback?: boolean };
type Datos = { ventana: string; consultas: number; llamadas: number; errores: number; fallbacks: number; latencia_media: number; latencia_p95: number; tokens_entrada: number; tokens_salida: number; tokens_total: number; sin_uso_reportado: number; tipos_respuesta: Record<string, number>; por_modelo: Record<string, number>; por_error: Record<string, number>; recientes: Evento[] };

function Distribucion({ titulo, valores }: { titulo: string; valores: Record<string, number> }) {
  const max = Math.max(1, ...Object.values(valores));
  return (
    <section className="metrica-panel">
      <h2>{titulo}</h2>
      {Object.entries(valores).length === 0 ? (
        <p className="vacio">Todavía no hay datos.</p>
      ) : (
        Object.entries(valores).map(([nombre, valor]) => (
          <div className="distribucion" key={nombre}>
            <div>
              <span>{nombre}</span>
              <b>{valor}</b>
            </div>
            <meter min={0} max={max} value={valor}>{valor}</meter>
          </div>
        ))
      )}
    </section>
  );
}

export default function Metricas() {
  const [datos, setDatos] = useState<Datos | null>(null);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(true);
  const [filtro, setFiltro] = useState('todos');
  const [actualizado, setActualizado] = useState('');

  const cargar = async (signal?: AbortSignal) => {
    setCargando(true);
    setError('');
    try {
      const r = await fetch(`${API}/api/metricas`, { signal });
      if (!r.ok) throw new Error('No se pudieron cargar las métricas. Verifica el backend.');
      setDatos(await r.json());
      setActualizado(new Date().toLocaleTimeString('es-EC'));
    } catch (e) {
      if (!(e instanceof DOMException && e.name === 'AbortError')) {
        setError(e instanceof Error ? e.message : 'Error de conexión');
      }
    } finally {
      if (!signal?.aborted) setCargando(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    void cargar(controller.signal);
    return () => controller.abort();
  }, []);

  const eventos = datos?.recientes.filter(e => filtro === 'todos' || (filtro === 'errores' ? Boolean(e.error) : e.evento === filtro)) ?? [];

  return (
    <main className="dashboard">
      <header className="dashboard__barra">
        <a className="marca" href="/">UNIANDES <em>·</em> Asistente Académico</a>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <a
            href="/"
            style={{
              textDecoration: 'none',
              color: '#0f3a63',
              fontWeight: 600,
              fontSize: '13px',
              padding: '6px 12px',
              borderRadius: '6px',
              background: '#eef3f8',
              display: 'inline-flex',
              alignItems: 'center',
            }}
          >
            ← Volver al Asistente
          </a>
          <span className="etiqueta">Observabilidad</span>
        </div>
      </header>

      <div className="dashboard__titulo">
        <div>
          <p className="eyebrow">OPERACIÓN DEL ASISTENTE</p>
          <h1>Métricas de uso</h1>
          <p>Consultas, disponibilidad y consumo reportado por los proveedores.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="boton boton--primario" onClick={() => void cargar()} disabled={cargando}>
            {cargando ? 'Cargando…' : 'Actualizar datos'}
          </button>
        </div>
      </div>

      <p className="nota-dashboard">
        Ruta pública, sin autenticación. Solo se muestran metadatos técnicos; no se registran preguntas, respuestas ni datos académicos.{' '}
        {actualizado && `Actualizado a las ${actualizado}.`}
      </p>

      {error && <p className="error-consulta" role="alert">{error}</p>}

      {datos && (
        <>
          <div className="kpis">
            {[
              ['Consultas', datos.consultas, 'Incluye validaciones y rechazos'],
              ['Intentos LLM', datos.llamadas, 'Incluye reintentos y respaldo'],
              ['Errores de llamada', datos.errores, 'No equivalen a consultas fallidas'],
              ['Respaldo exitoso', datos.fallbacks, 'Consultas resueltas por el alternativo'],
              ['Latencia media', `${datos.latencia_media.toFixed(2)} s`, 'Procesamiento del backend'],
              ['Latencia p95', `${datos.latencia_p95.toFixed(2)} s`, '95 % de consultas bajo este valor'],
              ['Tokens reportados', datos.tokens_total.toLocaleString(), 'Suma del total declarado por el SDK'],
              ['Tokens entrada / salida', `${datos.tokens_entrada} / ${datos.tokens_salida}`, 'Sin estimaciones ni costos inferidos'],
            ].map(([titulo, valor, nota]) => (
              <article className="kpi" key={titulo}>
                <span>{titulo}</span>
                <strong>{valor}</strong>
                <small>{nota}</small>
              </article>
            ))}
          </div>

          <p className="nota-dashboard">
            {datos.ventana}. {datos.sin_uso_reportado} intentos sin uso reportado; sus tokens son desconocidos, no cero. El total puede incluir tokens internos del proveedor.
          </p>

          <div className="distribuciones">
            <Distribucion titulo="Tipos de respuesta" valores={datos.tipos_respuesta} />
            <Distribucion titulo="Intentos por modelo" valores={datos.por_modelo} />
            <Distribucion titulo="Categorías de error" valores={datos.por_error} />
          </div>

          <section className="metrica-panel">
            <div className="tabla-titulo">
              <h2>Actividad reciente</h2>
              <label>
                Mostrar{' '}
                <select value={filtro} onChange={e => setFiltro(e.target.value)}>
                  <option value="todos">Todos los eventos</option>
                  <option value="consulta">Consultas</option>
                  <option value="llm">Llamadas LLM</option>
                  <option value="errores">Errores</option>
                </select>
              </label>
            </div>
            <div className="tabla-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Evento</th>
                    <th>Modelo / resultado</th>
                    <th>Duración</th>
                    <th>Tokens</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {eventos.map((e, i) => (
                    <tr key={`${e.request_id}-${i}`}>
                      <td>{new Date(e.fecha).toLocaleString('es-EC')}</td>
                      <td>{e.evento}</td>
                      <td>{e.modelo || e.estado || '—'}{e.fallback ? ' · respaldo' : ''}</td>
                      <td>{e.segundos ?? 0} s</td>
                      <td>{e.tokens_total ?? '—'}</td>
                      <td>{e.error || '—'}{e.status ? ` (${e.status})` : ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!eventos.length && (
                <p className="vacio">Aún no hay eventos para este filtro. Las próximas consultas aparecerán aquí.</p>
              )}
            </div>
          </section>
        </>
      )}
    </main>
  );
}
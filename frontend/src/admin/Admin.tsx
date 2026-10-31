import { useEffect, useState } from 'react';
import { adminAPI, type Bootstrap } from './api';
import Configuracion from './Configuracion';
import RAG from './RAG';
import Analisis from './Analisis';
import '../styles.css';
import './admin.css';

export default function Admin(){
  const [user, setUser] = useState('');
  const [checking, setChecking] = useState(true);
  const [data, setData] = useState<Bootstrap|null>(null);
  const [tab, setTab] = useState('Configuración');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const r = await adminAPI<Bootstrap>('/bootstrap');
    setData(r);
    return r;
  };

  useEffect(() => {
    let mounted = true;
    void adminAPI<{ username: string }>('/session')
      .then(async r => {
        if (mounted) {
          setUser(r.username);
          await load();
        }
      })
      .catch(() => {})
      .finally(() => {
        if (mounted) setChecking(false);
      });

    const expire = () => {
      setUser('');
      setData(null);
      setError('Tu sesión terminó. Inicia sesión de nuevo.');
    };

    window.addEventListener('admin-session-expired', expire);
    return () => {
      mounted = false;
      window.removeEventListener('admin-session-expired', expire);
    };
  }, []);

  async function signin(form: FormData) {
    setBusy(true);
    setError('');
    try {
      const r = await adminAPI<{ username: string }>('/login', {
        username: form.get('username'),
        password: form.get('password')
      });
      setUser(r.username);
      await load();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    try {
      await adminAPI('/logout', {});
      setUser('');
      setData(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (checking) {
    return (
      <main className="admin-login">
        <p role="status">Comprobando sesión…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="admin-login">
        <section className="admin-login__card">
          <a href="/" className="admin-brand">UNIANDES <span>·</span> Asistente IA</a>
          <p className="admin-eyebrow">ACCESO ADMINISTRATIVO</p>
          <h1>Tu centro de conocimiento.</h1>
          <p>Gestiona la orientación, sus fuentes y la calidad de cada respuesta.</p>
          <form action={signin}>
            <label>
              Usuario
              <input name="username" defaultValue="admin" autoComplete="username" required maxLength={80} />
            </label>
            <label>
              Contraseña
              <input name="password" type="password" autoComplete="current-password" required maxLength={200} />
            </label>
            {error && <p className="admin-error" role="alert">{error}</p>}
            <button className="admin-primary" disabled={busy}>
              {busy ? 'Verificando…' : 'Ingresar al administrador'}
            </button>
          </form>
          <small>
            Sesión privada · La contraseña se valida en el servidor. · <a href="/" style={{ color: '#0f3a63', textDecoration: 'none', fontWeight: 600 }}>Volver al chat</a>
          </small>
        </section>
      </main>
    );
  }

  return (
    <main className="admin-shell">
      <header className="admin-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <a href="/" className="admin-brand">UNIANDES <span>·</span> Asistente IA</a>
          <a 
            href="/" 
            style={{
              fontSize: '12px',
              color: '#0f3a63',
              background: '#eef3f8',
              padding: '4px 10px',
              borderRadius: '6px',
              textDecoration: 'none',
              fontWeight: 600
            }}
          >
            ← Volver al Asistente
          </a>
        </div>
        <div>
          <span>{user}</span>
          <button onClick={() => void logout()}>Cerrar sesión</button>
        </div>
      </header>

      <div className="admin-heading">
        <p className="admin-eyebrow">GESTIÓN DEL ASISTENTE</p>
        <h1>Conocimiento con trazabilidad.</h1>
        <p>Prompts versionados, fuentes vigentes y evaluación reproducible.</p>
      </div>

      <nav className="admin-tabs" aria-label="Secciones de administración">
        {['Configuración', 'RAG', 'Análisis'].map((name, i) => (
          <button 
            key={name} 
            aria-current={tab === name ? 'page' : undefined} 
            onClick={() => { setTab(name); setError(''); }}
          >
            <span>0{i + 1}</span>{name}
          </button>
        ))}
      </nav>

      {error && <p role="alert" className="admin-error">{error}</p>}

      {!data ? (
        <button onClick={() => void load().catch(e => setError(e.message))}>
          Cargar configuración
        </button>
      ) : tab === 'Configuración' ? (
        <Configuracion data={data} reload={load} />
      ) : tab === 'RAG' ? (
        <RAG data={data} reload={load} />
      ) : (
        <Analisis data={data} />
      )}
    </main>
  );
}
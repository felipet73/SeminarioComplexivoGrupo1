import { useState, useEffect } from 'react';

type Fragmento = {
  id: string;
  articulo: string;
  titulo: string;
  longitud_caracteres: number;
  texto: string;
};

interface Props {
  abierto: boolean;
  alCerrar: () => void;
}

export default function PanelAdminRAG({ abierto, alCerrar }: Props) {
  const [fragmentos, setFragmentos] = useState<Fragmento[]>([]);
  const [archivo, setArchivo] = useState<File | null>(null);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState<string | null>(null);

  const cargarLista = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/fragmentos');
      if (res.ok) {
        const json = await res.json();
        setFragmentos(json.fragmentos || []);
      }
    } catch {
      // Si el backend aún no tiene el endpoint levantado, maneja la excepción silenciosamente
    }
  };

  useEffect(() => {
    if (abierto) {
      cargarLista();
    }
  }, [abierto]);

  const subirDocumento = async () => {
    if (!archivo) return;
    setCargando(true);
    setMensaje(null);
    const data = new FormData();
    data.append('archivo', archivo);

    try {
      const res = await fetch('http://localhost:8000/api/admin/cargar-documento', {
        method: 'POST',
        body: data,
      });
      const json = await res.json();
      if (res.ok) {
        setMensaje(`Éxito: Se indexaron ${json.total_articulos_indexados} artículos.`);
        cargarLista();
      } else {
        setMensaje(`Error: ${json.detail || 'No se pudo procesar el archivo'}`);
      }
    } catch (err) {
      setMensaje('Error de conexión con el backend (puerto 8000).');
    } finally {
      setCargando(false);
    }
  };

  if (!abierto) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      backdropFilter: 'blur(3px)'
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        width: '90%',
        maxWidth: '900px',
        maxHeight: '85vh',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        color: '#1e293b',
        fontFamily: 'inherit'
      }}>
        {/* Cabecera del modal */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e2e8f0', paddingBottom: '12px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#0f172a' }}>Panel Administrativo RAG</h2>
            <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#64748b' }}>
              Segmentación semántica de reglamentos por Artículos
            </p>
          </div>
          <button
            onClick={alCerrar}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#64748b'
            }}
          >
            ✕
          </button>
        </div>

        {/* Zona de Carga de Archivo */}
        <div style={{ background: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: '8px', padding: '16px', margin: '16px 0' }}>
          <b style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Cargar Reglamento Institucional (PDF):</b>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setArchivo(e.target.files?.[0] || null)}
              style={{ fontSize: '0.85rem' }}
            />
            <button
              type="button"
              onClick={subirDocumento}
              disabled={cargando || !archivo}
              style={{
                backgroundColor: cargando || !archivo ? '#94a3b8' : '#0284c7',
                color: '#fff',
                border: 'none',
                padding: '6px 14px',
                borderRadius: '6px',
                cursor: cargando || !archivo ? 'not-allowed' : 'pointer',
                fontWeight: 500,
                fontSize: '0.85rem'
              }}
            >
              {cargando ? 'Segmentando e Indexando...' : 'Procesar PDF por Artículos'}
            </button>
          </div>
          {mensaje && (
            <p style={{ margin: '8px 0 0', fontSize: '0.85rem', color: mensaje.startsWith('Error') ? '#dc2626' : '#16a34a' }}>
              {mensaje}
            </p>
          )}
        </div>

        {/* Tabla de Artículos Fragmentados */}
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <h3 style={{ fontSize: '1rem', margin: '0 0 10px', color: '#334155' }}>
            Artículos Extraídos ({fragmentos.length})
          </h3>
          {fragmentos.length === 0 ? (
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', textAlign: 'center', padding: '24px 0' }}>
              No hay fragmentos cargados en memoria. Sube un archivo PDF oficial para procesarlo.
            </p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: '#f1f5f9', textAlign: 'left', position: 'sticky', top: 0 }}>
                  <th style={{ padding: '8px', borderBottom: '1px solid #cbd5e1' }}>Artículo</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #cbd5e1' }}>Título / Tema</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #cbd5e1' }}>Caracteres</th>
                  <th style={{ padding: '8px', borderBottom: '1px solid #cbd5e1' }}>Vista Previa</th>
                </tr>
              </thead>
              <tbody>
                {fragmentos.map((f) => (
                  <tr key={f.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '8px', fontWeight: 600, color: '#0369a1' }}>{f.articulo}</td>
                    <td style={{ padding: '8px', color: '#334155' }}>{f.titulo}</td>
                    <td style={{ padding: '8px', color: '#64748b' }}>{f.longitud_caracteres}</td>
                    <td style={{ padding: '8px', color: '#475569' }}>{f.texto.slice(0, 100)}...</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pie del modal */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '12px', marginTop: '12px', textAlign: 'right' }}>
          <button
            type="button"
            onClick={alCerrar}
            style={{
              padding: '6px 16px',
              backgroundColor: '#f1f5f9',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              cursor: 'pointer',
              color: '#475569'
            }}
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
import { describe, expect, it, vi } from 'vitest';
import { ApiError, enviarConsulta } from './api';

function stream(text: string) { return new ReadableStream({ start(controller) { controller.enqueue(new TextEncoder().encode(text)); controller.close(); } }); }

describe('cliente SSE', () => {
  it('envía el modelo preferido, lee tokens y contrato final', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(stream('event: token\ndata: {"texto":"Hola "}\n\nevent: done\ndata: {"respuesta":"Hola","estado":"abstencion","requiere_revision_humana":true,"fuentes":[],"modelo_utilizado":"test","fallback_activado":false,"tiempo_segundos":0.1}\n\n'), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
    const tokens: string[] = [];
    const respuesta = await enviarConsulta('consulta', 'gemini', (token) => tokens.push(token));
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toMatchObject({ modelo_preferido: 'gemini' });
    expect(tokens).toEqual(['Hola ']);
    expect(respuesta.respuesta).toBe('Hola');
  });
  it.each([422, 429, 503])('expone error %i', async (status) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'falló' }), { status, headers: { 'Content-Type': 'application/json', 'Retry-After': '6' } })));
    await expect(enviarConsulta('consulta', 'openai', () => {})).rejects.toBeInstanceOf(ApiError);
  });
});

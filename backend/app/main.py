import os
import time
from typing import Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Asistente Academico UNIANDES", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Asistente Academico UNIANDES</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen flex flex-col items-center p-4">
  <div class="w-full max-w-3xl bg-white rounded-xl shadow-md border flex flex-col h-[90vh]">
    <header class="p-4 bg-blue-900 text-white rounded-t-xl flex justify-between items-center">
      <div>
        <h1 class="text-lg font-bold">Asistente de Orientacion Academica UNIANDES</h1>
        <p class="text-xs text-blue-200">Semana 2 — Conexion con IA Generativa</p>
      </div>
    </header>
    <main id="chatBox" class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
      <div class="bg-blue-100 text-blue-950 p-3 rounded-lg text-sm max-w-[85%] border border-blue-200">
        Hola, soy el Orientador Academico de UNIANDES. Puedes consultarme sobre requisitos de matricula, certificados, practicas y modalidades de titulacion.
      </div>
    </main>
    <footer class="p-4 border-t bg-white rounded-b-xl">
      <form id="chatForm" class="flex gap-2">
        <input type="text" id="userInput" placeholder="Escribe tu consulta academica..." class="flex-1 border rounded-lg px-3 py-2 text-sm" required />
        <button type="submit" id="sendBtn" class="bg-blue-900 text-white px-4 py-2 rounded-lg text-sm font-medium">Enviar</button>
      </form>
    </footer>
  </div>
  <script>
    const form = document.getElementById('chatForm');
    const input = document.getElementById('userInput');
    const chatBox = document.getElementById('chatBox');
    const sendBtn = document.getElementById('sendBtn');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const q = input.value.trim();
      if (!q) return;

      chatBox.innerHTML += `<div class="flex justify-end"><div class="bg-blue-900 text-white p-3 rounded-lg text-sm max-w-[85%]">${q}</div></div>`;
      input.value = '';
      sendBtn.disabled = true;
      sendBtn.innerText = 'Consultando...';

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ pregunta: q })
        });
        const d = await res.json();
        chatBox.innerHTML += `<div class="flex justify-start"><div class="bg-white border p-3 rounded-lg text-sm max-w-[85%] shadow-sm">${d.respuesta}<br><br><small class="text-gray-500">Fuente: ${d.fuente} | Modelo: ${d.modelo_utilizado}</small></div></div>`;
      } catch (err) {
        chatBox.innerHTML += `<div class="text-red-500 text-sm">Error: ${err.message}</div>`;
      } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = 'Enviar';
        chatBox.scrollTop = chatBox.scrollHeight;
      }
    });
  </script>
</body>
</html>"""

@app.get("/", include_in_schema=False, response_class=HTMLResponse)
def root():
    return HTML_PAGINA

@app.get("/health")
def health():
    return {"status": "ok", "service": "titulacion-rag-api"}

class ChatRequest(BaseModel):
    pregunta: str
    modelo_preferido: Optional[Literal["gemini", "openai"]] = "gemini"

@app.post("/api/chat")
def chat(payload: ChatRequest):
    return {
        "respuesta": "Para tramites de titulacion o matricula, consulte los reglamentos oficiales de UNIANDES en Secretaria Academica.",
        "fuente": "Reglamento de Regimen Academico UNIANDES",
        "modelo_utilizado": "Inferencia Local MVP",
        "fallback_activado": False,
        "tiempo_segundos": 0.1
    }

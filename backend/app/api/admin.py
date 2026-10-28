from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
from app.services.chunking import segmentar_por_articulos
from pypdf import PdfReader
import io

router = APIRouter(prefix="/api/admin", tags=["Administración RAG"])

# Almacén en memoria para demostración/auditoría rápida
BASE_CONOCIMIENTO: List[Dict[str, Any]] = []

@router.post("/cargar-documento")
async def cargar_documento(archivo: UploadFile = File(...)):
    """Carga un PDF, lo fragmenta por artículo y lo almacena para consulta."""
    if not archivo.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se admiten archivos PDF.")
    
    contenido_bytes = await archivo.read()
    lector = PdfReader(io.BytesIO(contenido_bytes))
    
    texto_total = ""
    for num_pag, pagina in enumerate(lector.pages):
        texto = pagina.extract_text() or ""
        texto_total += f"\n[Pág. {num_pag + 1}]\n" + texto

    # Segmentación especializada
    fragmentos = segmentar_por_articulos(texto_total, archivo.filename)
    
    global BASE_CONOCIMIENTO
    BASE_CONOCIMIENTO.extend(fragmentos)
    
    return {
        "mensaje": "Documento procesado exitosamente",
        "archivo": archivo.filename,
        "total_paginas": len(lector.pages),
        "total_articulos_indexados": len(fragmentos),
        "resumen_articulos": [
            {"articulo": f["articulo"], "titulo": f["titulo"], "longitud": f["longitud_caracteres"]}
            for f in fragmentos[:10]  # Muestra preliminar de los primeros 10
        ]
    }

@router.get("/fragmentos")
async def listar_fragmentos():
    """Permite al administrador ver todos los artículos indexados con sus metadatos."""
    return {
        "total": len(BASE_CONOCIMIENTO),
        "fragmentos": BASE_CONOCIMIENTO
    }

@router.get("/simular-recuperacion")
async def simular_recuperacion(query: str):
    """
    Prueba de recuperación: muestra qué artículos coinciden con la consulta
    y cómo se le presentan al LLM antes de generar la respuesta.
    """
    palabras = query.lower().split()
    coincidencias = []
    
    for f in BASE_CONOCIMIENTO:
        puntuacion = sum(1 for p in palabras if p in f["texto"].lower())
        if puntuacion > 0:
            coincidencias.append({**f, "score": puntuacion})
            
    coincidencias.sort(key=lambda x: x["score"], reverse=True)
    seleccionados = coincidencias[:3]
    
    return {
        "consulta": query,
        "articulos_recuperados": len(seleccionados),
        "contexto_inyectado": seleccionados
    }
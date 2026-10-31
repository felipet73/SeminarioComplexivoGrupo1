import re
from typing import List, Dict, Any

def segmentar_por_articulos(texto_completo: str, nombre_documento: str) -> List[Dict[str, Any]]:
    """
    Divide un reglamento en fragmentos basados en la estructura de 'Artículo' / 'Art.'.
    Descarta encabezados previos y extrae metadatos para trazabilidad.
    """
    patron = r'(?=(?:Artículo|Art\.)\s+\d+[\s\.\:\-])'
    partes = re.split(patron, texto_completo, flags=re.IGNORECASE)
    
    fragmentos = []
    
    for parte in partes:
        contenido = parte.strip()
        # Solo procesar bloques que realmente comiencen con "Artículo" o "Art."
        if not re.match(r'^(?:Artículo|Art\.)\s+\d+', contenido, re.IGNORECASE):
            continue
            
        coincidencia = re.match(r'^(?:Artículo|Art\.)\s+(\d+)[\s\.\:\-]*([^\n\.\;]+)?', contenido, re.IGNORECASE)
        num_articulo = coincidencia.group(1) if coincidencia else "0"
        titulo_articulo = coincidencia.group(2).strip() if (coincidencia and coincidencia.group(2)) else "Disposición general"

        fragmentos.append({
            "id": f"{nombre_documento}_art_{num_articulo}",
            "articulo": f"Art. {num_articulo}",
            "titulo": titulo_articulo,
            "documento": nombre_documento,
            "texto": contenido,
            "longitud_caracteres": len(contenido),
            "tokens_aprox": len(contenido.split())
        })
        
    return fragmentos
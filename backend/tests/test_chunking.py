from app.services.chunking import segmentar_por_articulos

def test_segmentacion_por_articulos():
    texto_simulado = """
    REGLAMENTO DE RÉGIMEN ACADÉMICO
    Artículo 21.- De la matrícula ordinaria. La matrícula ordinaria se realizará dentro del cronograma oficial.
    Artículo 22.- De la matrícula extraordinaria. Se concede previa justificación y pago de aranceles.
    """
    fragmentos = segmentar_por_articulos(texto_simulado, "reglamento_prueba.pdf")
    
    assert len(fragmentos) == 2
    assert fragmentos[0]["articulo"] == "Art. 21"
    assert "matrícula ordinaria" in fragmentos[0]["titulo"].lower()
    assert fragmentos[1]["articulo"] == "Art. 22"
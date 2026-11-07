"""Genera el resumen PDF y renders; instalar docs/requirements.txt en entorno aparte."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/presentacion-entrega4.pdf'
PREVIEWS = ROOT / 'tmp/pdfs/entrega4'
W, H = 960, 540
NAVY, TEAL, RED, GRAY = '#15243B', '#087E74', '#B42318', '#526176'


def generar():
    font_dir = Path('C:/Windows/Fonts')
    if (font_dir / 'arial.ttf').exists():
        pdfmetrics.registerFont(TTFont('Texto', str(font_dir / 'arial.ttf')))
        pdfmetrics.registerFont(TTFont('Negrita', str(font_dir / 'arialbd.ttf')))
    else:
        pdfmetrics.registerFontFamily('Helvetica')
    font = 'Texto' if 'Texto' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    bold = 'Negrita' if font == 'Texto' else 'Helvetica-Bold'
    evidence = json.loads((ROOT / 'docs/evidencias/semana-4/analisis-preliminar-2026-11-07.json').read_text('utf-8'))
    tests = evidence['pytest_actual']['tests']
    if evidence['actions']['conclusion'] != 'success':
        raise ValueError('No hay despliegue aprobado para esta presentación')
    total = evidence['pruebas_publicas']['casos_definidos']
    doc = canvas.Canvas(str(OUT), pagesize=(W, H))
    doc.setTitle('Grupo 1 - Titulación y normativa académica - Entrega 4')
    doc.setAuthor('Grupo 1 - UNIANDES; asistencia de Codex declarada en README')

    def text(value, x, y, size=20, color=NAVY, strong=False, width=870):
        style = ParagraphStyle('texto', fontName=bold if strong else font, fontSize=size, leading=size*1.3,
                               textColor=HexColor(color))
        p = Paragraph(value, style)
        _, height = p.wrap(width, H)
        if y-height < 43:
            raise ValueError('Texto fuera del área útil: '+value[:50])
        p.drawOn(doc, x, y-height)
        return height

    def page(n, title, subtitle):
        doc.setFillColor(HexColor('#F6F8FC')); doc.rect(0, 0, W, H, fill=1, stroke=0)
        doc.setFillColor(HexColor(TEAL)); doc.rect(44, H-48, 60, 5, fill=1, stroke=0)
        text(title, 44, H-75, 31, strong=True)
        text(subtitle, 44, H-126, 15, GRAY)
        doc.setFont(font, 10); doc.setFillColor(HexColor(GRAY))
        doc.drawString(44, 22, 'Grupo 1 | Evidencia del 7 de noviembre de 2026 (Ecuador)')
        doc.drawRightString(W-44, 22, f'{n} / 6')

    def block(title, body, x, y, width=410, color=TEAL):
        height = text(title, x, y, 21, color, True, width)
        return text(body, x, y-height-15, 18, NAVY, False, width)+height+15

    page(1, 'Titulación y normativa académica', 'Asistente educativo con RAG, citas y herramientas de alcance controlado')
    text('Entrega 4: qué funciona y qué sigue abierto', 44, 345, 28, strong=True)
    text('Servicio corregido y pruebas públicas aprobadas', 44, 280, 25, RED, True)
    text('Orientación educativa con citas, abstención y confirmación humana. Cloud Run ejecuta 0dab82d: 35/35 casos públicos aprobados. El historial y la evaluación final completa siguen pendientes.', 44, 228, 21, width=840)
    text('Aguilar Rogel Olmes Patricio · Cevallos Mazon Widman Yadiro · Torres Lopez Christian Felipe', 44, 100, 14, GRAY)
    doc.showPage()

    page(2, 'La respuesta depende de fuentes verificables', 'Arquitectura implementada en el código actual')
    labels = [('React / Vercel',44), ('FastAPI / Cloud Run',338), ('RAG / SQLite',632)]
    for label,x in labels:
        doc.setStrokeColor(HexColor(TEAL)); doc.setLineWidth(1.4)
        doc.roundRect(x, 290, 250, 65, 9, fill=0, stroke=1)
        text(label, x+18, 334, 18, strong=True, width=220)
    for x in (300,594):
        doc.setStrokeColor(HexColor(GRAY));doc.line(x,322,x+30,322);doc.line(x+25,326,x+30,322);doc.line(x+25,318,x+30,322)
    block('Fuentes', '961 fragmentos habilitados. Otros 86 del instructivo OCR permanecen sin aprobación humana.', 44, 252)
    block('Controles', 'Citas validadas, abstención sin evidencia, cinco herramientas y máximo de cuatro turnos. Confirmación para borradores demo.', 500, 252)
    text('Gemini con respaldo OpenAI. La orientación no aprueba trámites ni modifica expedientes.',44,95,15,GRAY)
    doc.showPage()

    page(3, 'Los resultados locales y remotos son distintos', 'Denominadores y límites conservados en los informes')
    block('Pruebas locales', f'<b>{tests}</b> casos de backend aprobados.<br/>Cobertura: <b>88,73 %</b>.<br/>Sin claves de modelos ni .env privado.',44,340)
    block('URLs públicas', f'<b>{total}/{total}</b> casos aprobados.<br/>Dos consultas generativas directas y una SSE por Vercel.<br/>Actions 42378740379, intento 2.',500,340,color=TEAL)
    text('p95 del reporte exitoso: pendiente de adjuntar el JSON por caso. No usar el dato del intento fallido ni confundir estas tres consultas con evaluación completa.',44,185,19,width=850)
    text('Fuentes: analisis-preliminar-2026-11-07.json y Actions, intento 2. Código 0dab82d.',44,90,14,GRAY)
    doc.showPage()

    page(4, 'Seguridad: corregido hoy y exposición histórica', 'No confundir exclusiones de Gitleaks con credenciales legacy')
    block('Acreditado en la revisión probada', 'Módulo inseguro y rutas retirados.<br/>Detector de credenciales débiles.<br/>Límite de 30 consultas por minuto y proceso.<br/>Commit visible en /health.',44,340)
    block('Pendiente de cierre residual', 'Falsos positivos: tokens de ejemplo de un advisory de filelock.<br/>Credenciales JWT/password legacy: funcionales antes, retiradas hoy.<br/>Revocar reutilizaciones y limpiar historial coordinadamente.',500,340,color=RED)
    text('Las rutas antiguas probadas devuelven 404. El historial aún contiene valores: no declarar s4b completo.',44,123,17,GRAY)
    doc.showPage()

    page(5, 'El pipeline promueve la imagen que pasó pruebas', 'Solo main; despliegue condicionado por cinco jobs')
    text('Secretos + backend + frontend + navegador + contenedor',44,340,24,TEAL,True)
    text('Imagen probada → Artifact Registry → Cloud Run → pruebas públicas',44,280,23,strong=True)
    text('Las comprobaciones posteriores exigen el SHA, corpus disponible, retirada de rutas y SSE completo. Los 35 casos incluyen generación real y deben aprobar.',44,220,20,width=850)
    text('WIF, Artifact Registry y Cloud Run ya se usaron en el job aprobado. Las claves viven en Secret Manager; la cuenta de ejecución requiere acceso a cada secreto.',44,118,17,TEAL,width=850)
    doc.showPage()

    page(6, 'Cierre de entrega con pendientes explícitos', 'Prioridades para el equipo y la sustentación')
    block('Demo pública y evidencia', 'Respuesta con cita y abrir la fuente.<br/>Fuera de tema y abstención.<br/>Borrador demo con confirmación humana.<br/>Capturas y vídeo real de respaldo de 2 min.',44,340)
    block('Revisión humana', 'Aprobar OCR y aplicabilidad del instructivo.<br/>Repetir el agente: histórico estricto 5/6.<br/>Ensayar reinicio y resolver durabilidad.<br/>Confirmar aportes y uso de IA individual.',500,340)
    text('12 min de exposición + 3 de preguntas. ZIP máximo 20 MB: el corpus actual supera ese límite; resolver antes de entregar.',44,125,17,GRAY)
    text('Guía de cierre: docs/14-checklist-entrega-final.md. Fecha oficial 9/11, 23:59 Ecuador; prórroga 11/11.',44,70,12,GRAY)
    doc.save()
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    pdf = pymupdf.open(OUT)
    for i,p in enumerate(pdf):
        p.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(PREVIEWS / f'pagina-{i+1}.png')
    print(f'PDF: {OUT}; páginas: {len(pdf)}')


if __name__ == '__main__':
    generar()

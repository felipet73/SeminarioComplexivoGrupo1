"""Genera el resumen PDF y renders; instalar docs/requirements.txt en entorno aparte."""
from pathlib import Path
import json
from xml.etree import ElementTree
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
    remote = json.loads((ROOT / 'docs/evidencias/semana-4/pruebas-url-inicial.json').read_text('utf-8'))
    suite = ElementTree.parse(ROOT / 'docs/evidencias/semana-4/pytest-local.xml').getroot().find('testsuite')
    tests = suite.attrib['tests']
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
        doc.drawString(44, 22, 'Grupo 1 | Evidencia del 6 de noviembre de 2026 (Ecuador)')
        doc.drawRightString(W-44, 22, f'{n} / 6')

    def block(title, body, x, y, width=410, color=TEAL):
        height = text(title, x, y, 21, color, True, width)
        return text(body, x, y-height-15, 18, NAVY, False, width)+height+15

    page(1, 'Titulación y normativa académica', 'Asistente educativo con RAG, citas y herramientas de alcance controlado')
    text('Entrega 4: qué funciona y qué sigue abierto', 44, 345, 28, strong=True)
    text('La incidencia del despliegue sigue abierta', 44, 280, 25, RED, True)
    text('Cloud Run todavía acepta la credencial administrativa histórica y devuelve 500 en el chat. El código corregido está preparado, pero el servicio activo debe actualizarse.', 44, 228, 21, width=840)
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
    block('URLs públicas', f'<b>{remote["correctos"]}/{remote["total"]}</b> casos aprobados.<br/>Se ejecutaron también las dos consultas generativas; fallaron por HTTP 500.',500,340,color=RED)
    text('El preflight CORS funciona; el error 500 del backend produce una respuesta sin cabeceras CORS.',44,185,19,width=850)
    text('Fuentes: pytest-local.xml y pruebas-url-inicial.json en docs/evidencias/semana-4/.',44,90,14,GRAY)
    doc.showPage()

    page(4, 'La seguridad exige actualizar el servicio', 'La eliminación en main no revoca una imagen antigua')
    block('Preparado en el repositorio', 'Módulo inseguro y rutas retirados.<br/>Detector de credenciales débiles.<br/>Límite de 30 consultas por minuto y proceso.<br/>Commit visible en /health.',44,340)
    block('Pendiente en producción', 'Desplegar la imagen corregida.<br/>Verificar 404 en rutas antiguas.<br/>Revocar cualquier valor reutilizado.<br/>Coordinar limpieza del historial.',500,340,color=RED)
    text('La verificación de autenticación descartó el token y no realizó operaciones administrativas.',44,123,17,GRAY)
    doc.showPage()

    page(5, 'El pipeline promueve la imagen que pasó pruebas', 'Solo main; despliegue condicionado por cinco jobs')
    text('Secretos + backend + frontend + navegador + contenedor',44,340,24,TEAL,True)
    text('Imagen probada → Artifact Registry → Cloud Run → pruebas públicas',44,280,23,strong=True)
    text('Las comprobaciones posteriores exigen el SHA, corpus disponible, retirada de rutas y SSE completo. Los 32 contratos sin generación deben aprobar.',44,220,20,width=850)
    text('Se requiere configurar o confirmar proyecto, repositorio de imágenes y autenticación WIF o secreto JSON de despliegue. No se ha ejecutado este job remoto.',44,118,17,RED,width=850)
    doc.showPage()

    page(6, 'Cierre de entrega con pendientes explícitos', 'Prioridades para el equipo y la sustentación')
    block('Primero: servicio público', 'Actualizar Cloud Run y comprobar el commit.<br/>Repetir 32 contratos y dos casos generativos.<br/>Conservar evidencia del cierre de la credencial.',44,340)
    block('Revisión humana', 'Aprobar OCR y aplicabilidad del instructivo.<br/>Repetir el agente: histórico estricto 5/6.<br/>Definir persistencia duradera.<br/>Confirmar aportes y uso de IA por integrante.',500,340)
    text('La semilla de documentos no conserva las cargas posteriores. Un límite de instancia no hace persistente SQLite.',44,125,17,GRAY)
    text('Guía de verificación: docs/08-pruebas.md. Matriz: docs/evidencias/semana-4/analisis-observaciones-docente.md.',44,70,12,GRAY)
    doc.save()
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    pdf = pymupdf.open(OUT)
    for i,p in enumerate(pdf):
        p.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(PREVIEWS / f'pagina-{i+1}.png')
    print(f'PDF: {OUT}; páginas: {len(pdf)}')


if __name__ == '__main__':
    generar()

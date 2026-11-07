"""PDF técnico desde Markdown e inventario OpenAPI revisado; entorno docs/requirements.txt."""
from pathlib import Path
import argparse
import json
from html import escape
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable

ROOT = Path(__file__).resolve().parents[1]
DETAILS = {
'/api/admin/login': ('Login: username y password; mutación con cabecera X-Admin-Request y origen admitido.', '200 username y cookie de sesión; 401 credencial inválida, 403 guard, 429 cinco fallos, 503 falta configuración. Sin LLM.'),
'/api/admin/session': ('Cookie de sesión administrativa vigente.', '200 username; 401 sin sesión. Sin LLM.'),
'/api/admin/logout': ('Cookie vigente, guard de mutación; sin cuerpo.', '200 ok; elimina sesión y cookie. Sin LLM.'),
'/api/admin/bootstrap': ('Cookie vigente; sin cuerpo.', '200 prompts, documentos públicos, configuración, umbrales, casos y modelos configurados (booleanos, nunca claves). Sin LLM.'),
'/api/admin/prompts': ('PromptInput: content y description; cookie y guard.', '200 prompt con nueva versión (hasta 999) y revisión, escribe archivo y auditoría. 409 límite. Sin LLM.'),
'/api/admin/prompts/{version}': ('Versión en ruta; PromptInput con expected_revision; cookie y guard.', '200 revisión incrementada; 404 versión ausente, 409 conflicto de revisión. Sin LLM.'),
'/api/admin/config': ('RAGConfig con prompt activo, chunk_size, overlap, top_k, estrategia, embedding_model, umbrales y revision; cookie y guard.', '200 configuración revisada; 409 conflicto, 422 prompt inexistente o parámetros inválidos. No reindexa ni llama a un proveedor en esta operación.'),
'/api/admin/documents': ('Multipart: metadata JSON DocMeta y file; cookie y guard.', '200 documento guardado con revisión; 422 archivo/formato/metadatos inválidos, 409 máximo 100 documentos, 413 exceso declarado. No genera respuestas ni indexa automáticamente.'),
'/api/admin/documents/{doc_id}': ('doc_id y DocUpdate con expected_revision; cookie y guard.', '200 metadatos actualizados; 404 no encontrado, 409 revisión concurrente. Sin LLM.'),
'/api/admin/documents/{doc_id}/replace': ('doc_id; multipart metadata, expected_revision, file; cookie y guard.', '200 nueva revisión con approved=false; 404 ausente, 409 conflicto, 422 archivo inválido. Exige nueva aprobación humana; no genera texto.'),
'/api/admin/documents/{doc_id}/file': ('doc_id; query revision opcional; cookie vigente.', '200 archivo de revisión actual o histórica; 404 si no existe o ruta fuera del directorio. No ejecuta modelos.'),
'/api/admin/history': ('Query resource obligatorio; cookie vigente.', '200 hasta 100 entradas de auditoría before/after. Las páginas internas se filtran en documentos. Sin LLM.'),
'/api/admin/rag/chunks': ('Query doc_id obligatorio; cookie vigente.', '200 hasta 512 fragmentos con ID, revisión, título, sección, página y texto. Sin LLM.'),
'/api/admin/rag/index/{doc_id}': ('doc_id; cookie y guard.', '200 índice/fragmentos y traza; 404 ausente, 409 conflicto, 422 límite/entrada, 503 fallo de embeddings. Solo llama a embeddings si estrategia híbrida; conserva índice previo ante error.'),
'/api/admin/rag/search': ('Search.query; cookie y guard.', '200 chunks, estrategia efectiva, warning y trace. Puede llamar embeddings en modo híbrido; no genera respuesta de chat.'),
'/api/admin/analysis': ('GET: cookie vigente. POST: AnalysisInput con 1–5 versiones, modelo, 1–10 casos, contexto y use_rag; cookie y guard.', 'GET 200 lista resumida de hasta 30 trabajos. POST 202 id/status; 409 trabajo ocupado, 422 versión inválida. En segundo plano genera con proveedor elegido, sin fallback ni escrituras demo; no hay juez IA.'),
'/api/admin/analysis/{job_id}': ('job_id y cookie vigente.', '200 experimento, resultados, evidencia y traza; 404 ausente. La lectura no llama a modelos.'),
'/api/herramientas': ('Público; sin cuerpo.', '200 esquemas de cinco herramientas, salidas, max_iteraciones y requieren_ok. No invoca LLM ni ejecuta herramienta.'),
'/api/herramientas/calcular-plazo': ('PlazoIn: fecha_inicio ISO y dias_habiles entero estricto 0–730; público.', '200 fecha_resultado y alcance de simulación; 422 entrada inválida. Determinista, sin LLM ni feriados.'),
'/api/herramientas/consultar-requisitos': ('RequisitosIn.modalidad; público.', '200 ConsultaOut con pasajes citables y alcance. Recuperación local/híbrida; puede usar embeddings pero no generación.'),
'/api/herramientas/generar-checklist': ('ChecklistIn.perfil_estudiante; público.', '200 ChecklistOut con perfil, items citados y completo=false. Filtros deterministas y RAG; puede usar embeddings pero no generación.'),
'/api/herramientas/agente/confirmar/{action_id}': ('action_id y DecisionIn token/aprobar; capacidad de confirmación, no sesión admin.', '200 DecisionOut; 404 ID/token inválido, 410 vencida, 409 decisión contradictoria. Alias de confirmación; guarda o cancela solo borrador local, sin LLM.'),
'/api/agente/confirmar/{action_id}': ('action_id y DecisionIn token/aprobar; capacidad de confirmación, no sesión admin.', '200 DecisionOut; 404 ID/token inválido, 410 vencida, 409 decisión contradictoria. Idempotente y auditado. Sin LLM.'),
'/health': ('Público; sin cuerpo.', '200 status, service, version y revision. Comprueba proceso e identidad declarada; no corpus ni proveedor.'),
'/ready': ('Público; sin cuerpo.', '200 status ready, fragmentos_elegibles, estrategia, proveedor_verificado=false; 503 sin corpus/índice elegible. No llama a modelos.'),
'/api/sources/{doc_id}/{revision}': ('doc_id y revision; público.', '200 archivo solo si la fuente está vigente/aprobada y la revisión coincide; 404 en otro caso. No genera texto.'),
'/api/metricas': ('Público; sin cuerpo.', '200 agregados y últimos 50 eventos técnicos de una ventana de hasta 2000; sin prompts, respuestas, claves ni datos personales en esos eventos. No llama a modelos.'),
'/api/chat': ('ConsultaChat: pregunta, modelo_preferido y contexto académico opcional; público con presupuesto global.', '200 RespuestaAsistente: respuesta/abstencion/aclaracion/rechazo/confirmacion; citas, traza, campos, modelo, fallback y tiempo. 422 validación, 429 presupuesto, 503 proveedor. Modelos solo según flujo descrito.'),
'/api/agente': ('Mismo ConsultaChat y presupuesto que /api/chat.', '200 mismo contrato/orquestador de chat; no es un segundo motor distinto. Mismos errores y reglas de generación.'),
'/api/chat/stream': ('ConsultaChat; público, comparte presupuesto. El flujo se resuelve antes de iniciar SSE.', '200 text/event-stream con token y done del contrato completo; errores previos 422/429/503 como JSON. Mismo agente, evidencia y fallback que chat.'),
}


class Diagram(Flowable):
    def __init__(self, kind):
        super().__init__()
        self.kind, self.width, self.height = kind, 475, 170

    def draw(self):
        c = self.canv
        c.setFont('Texto', 8)
        if self.kind == 'arquitectura':
            boxes = [(10, 105, 'Navegador', 'React / TypeScript'), (170, 105, 'Vercel', 'SPA + proxy /api'),
                     (330, 105, 'Cloud Run', 'FastAPI / Uvicorn'), (170, 20, 'Proveedores', 'Gemini / OpenAI'),
                     (330, 20, 'Estado local', 'SQLite + FTS5 + vectores')]
            arrows = [(145,130,170,130),(305,130,330,130),(395,105,395,70),(350,105,275,70)]
        elif self.kind == 'consulta':
            boxes = [(10,105,'Entrada y defensas','Pydantic / límite / rechazo'),(170,105,'RAG','Elegibilidad + ranking'),
                     (330,105,'Agente','Modelo / herramienta / bucle'),(330,20,'Validar contrato','JSON / citas / vigencia'),
                     (170,20,'Salida','JSON o SSE token + done')]
            arrows = [(145,130,170,130),(305,130,330,130),(395,105,395,70),(330,45,305,45)]
        else:
            boxes = [(10,105,'Modelo propone','Datos declarados'),(170,105,'Backend prepara','Capacidad + TTL 30 min'),
                     (330,105,'Usuario decide','Aprueba o cancela'),(330,20,'Transacción local','Hash / auditoría / idempotencia'),
                     (170,20,'Resultado demo','No envío a universidad')]
            arrows = [(145,130,170,130),(305,130,330,130),(395,105,395,70),(330,45,305,45)]
        for x,y,title,sub in boxes:
            c.setFillColor(colors.HexColor('#eff7f6'));c.setStrokeColor(colors.HexColor('#147d73'))
            c.roundRect(x,y,135,50,6,fill=1,stroke=1)
            c.setFillColor(colors.HexColor('#16324b'));c.setFont('Negrita',8);c.drawCentredString(x+67.5,y+31,title)
            c.setFont('Texto',6.5);c.drawCentredString(x+67.5,y+15,sub)
        for x1,y1,x2,y2 in arrows:
            c.setStrokeColor(colors.HexColor('#147d73'));c.line(x1,y1,x2,y2)
            import math
            a=math.atan2(y2-y1,x2-x1)
            for d in (-0.45,0.45):c.line(x2,y2,x2-6*math.cos(a+d),y2-6*math.sin(a+d))


def generate(source, schema_path, output):
    schema=json.loads(schema_path.read_text())
    fonts=Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('Texto',str(fonts/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('Negrita',str(fonts/'DejaVuSans-Bold.ttf')))
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle('Cuerpo',fontName='Texto',fontSize=9,leading=13,spaceAfter=7))
    styles.add(ParagraphStyle('TituloInforme',fontName='Negrita',fontSize=23,leading=29,textColor=colors.HexColor('#16324b'),spaceAfter=22))
    styles.add(ParagraphStyle('Seccion',fontName='Negrita',fontSize=16,leading=22,spaceAfter=13,keepWithNext=True,textColor=colors.HexColor('#147d73')))
    styles.add(ParagraphStyle('Subseccion',fontName='Negrita',fontSize=10,leading=15,spaceBefore=10,spaceAfter=7,keepWithNext=True))
    styles.add(ParagraphStyle('Celda',fontName='Texto',fontSize=7,leading=10))
    story=[]

    def p(text,style='Cuerpo'):
        return Paragraph(escape(text).replace('`',''),styles[style])

    def fields(s):
        if '$ref' in s:s=schema['components']['schemas'][s['$ref'].split('/')[-1]]
        result=[]
        for key,v in s.get('properties',{}).items():
            typ=v.get('type') or (v.get('$ref','').split('/')[-1] if '$ref' in v else 'opcional/unión')
            detail=[]
            for k in ('minLength','maxLength','minimum','maximum','minItems','maxItems','enum'):
                if k in v:detail.append(f'{k}={v[k]}')
            result.append(key+': '+typ+(' (obligatorio)' if key in s.get('required',[]) else '')+('; '+', '.join(detail) if detail else ''))
        return '; '.join(result) or 'Ver esquema OpenAPI adjunto.'

    def endpoints():
        n=0
        for path,methods in schema['paths'].items():
            if path not in DETAILS:raise ValueError('Falta detallar '+path)
            for method,op in methods.items():
                if method not in ('get','post','put','delete','patch'):continue
                n+=1
                story.append(p(f'9.{n}. {method.upper()} {path}','Subseccion'))
                desc,resp=DETAILS[path]
                story.append(p('Acceso y función. '+desc))
                body=op.get('requestBody',{}).get('content',{})
                if body:
                    for mime,spec in body.items():story.append(p('Cuerpo ('+mime+'). '+fields(spec.get('schema',{}))))
                params=op.get('parameters',[])
                if params:story.append(p('Parámetros. '+'; '.join(f"{v['name']} ({v['in']}, {'obligatorio' if v.get('required') else 'opcional'})" for v in params)))
                story.append(p('Salida y efectos. '+resp))
        if n!=31:raise ValueError(f'Inventario cambió: {n} operaciones; revisar informe.')

    lines=source.read_text().splitlines();i=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line=='[ENDPOINTS]':endpoints();continue
        if line.startswith('[DIAGRAMA:'):
            story.append(Diagram(line[10:-1]));story.append(Spacer(1,8));continue
        if line.startswith('# '):story.append(p(line[2:],'TituloInforme'));continue
        if line.startswith('## '):
            if len(story)>2:story.append(PageBreak())
            story.append(p(line[3:],'Seccion'));continue
        if line.startswith('### '):story.append(p(line[4:],'Subseccion'));continue
        if line.startswith('|'):
            rows=[line]
            while i<len(lines) and lines[i].strip().startswith('|'):rows.append(lines[i].strip());i+=1
            cells=[[v.strip() for v in row.strip('|').split('|')] for row in rows]
            cells=[row for row in cells if not all(re.fullmatch(r'[- :]+',v) for v in row)]
            ncols=len(cells[0]);data=[[p(v,'Celda') for v in row] for row in cells]
            widths=[475/ncols]*ncols
            t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5f0ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#c9d5db')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            story.extend([t,Spacer(1,10)]);continue
        story.append(p(line))

    def footer(c,doc):
        c.saveState();c.setFont('Texto',7);c.setFillColor(colors.HexColor('#526176'))
        c.drawString(48,25,'UNIANDES | Grupo 1 | Análisis preliminar | 07-11-2026 | Código 0dab82d')
        c.drawRightString(A4[0]-48,25,str(doc.page));c.restoreState()
    output.parent.mkdir(parents=True,exist_ok=True)
    SimpleDocTemplate(str(output),pagesize=A4,rightMargin=60,leftMargin=60,topMargin=48,bottomMargin=45,title='Análisis técnico preliminar y contraste de observaciones - Grupo 1',author='Grupo 1; informe con asistencia de Codex, sujeto a revisión del equipo').build(story,onFirstPage=footer,onLaterPages=footer)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--openapi',type=Path,default=ROOT/'docs/evidencias/semana-4/openapi-revisado-2026-11-07.json')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/analisis-tecnico-preliminar.pdf')
    args=parser.parse_args()
    generate(ROOT/'docs/analisis-tecnico-preliminar.md',args.openapi,args.output)
    print(args.output)

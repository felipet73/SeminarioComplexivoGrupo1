"""Ingesta, índice persistente por artículo y recuperación filtrada por vigencia."""
from __future__ import annotations
import hashlib
import io
import json
import math
import re
import zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from defusedxml import ElementTree
from app.config import get_settings
from app.services import admin_store as store
from app.services.metrics import registrar

MAX_BYTES = 10 * 1024 * 1024
ARTICLE = re.compile(r'(?im)^\s*(?:art(?:ículo|iculo|\.)?|artículo)\s*\.?\s*(\d+[a-z]?(?:[.-]\d+)?)\b[^\n]{0,160}')
STOP = set('a al de del la el en y o las los un una que qué como cómo para por con es se mi mis sobre debo quiero necesito cuáles cual cuál'.split())

class RevisionConflict(RuntimeError):
    pass

def extract(name: str, content: bytes) -> list[dict]:
    ext = Path(name).suffix.lower()
    if ext == '.pdf':
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        if reader.is_encrypted or len(reader.pages) > 200:
            raise ValueError('PDF cifrado o mayor a 200 páginas. Divide el archivo o usa un PDF accesible.')
        pages = [{'page': i+1,'text':p.extract_text() or ''} for i,p in enumerate(reader.pages)]
    elif ext == '.docx':
        with zipfile.ZipFile(io.BytesIO(content)) as archivo:
            info = archivo.getinfo('word/document.xml')
            if info.file_size > 5_000_000:
                raise ValueError('El contenido DOCX supera el límite de extracción.')
            root = ElementTree.fromstring(archivo.read(info))
            ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            pages = [{'page':1,'text':'\n'.join(''.join(p.itertext()) for p in root.findall('.//w:p',ns))}]
    elif ext in ('.txt','.md','.csv'):
        pages = [{'page':1,'text':content.decode('utf-8-sig')}]
    else:
        raise ValueError('Formato permitido: PDF con texto, DOCX, TXT, MD o CSV UTF-8.')
    total = sum(len(p['text']) for p in pages)
    if total < 20:
        raise ValueError('No se encontró texto suficiente. El PDF puede necesitar OCR previo.')
    if total > 1_000_000:
        raise ValueError('El documento excede un millón de caracteres. Divídelo.')
    return pages

def public_doc(doc):
    return {k:v for k,v in doc.items() if k not in ('pages','path')}

def eligible(doc, today=None):
    today = today or datetime.now(timezone(timedelta(hours=-5))).date().isoformat()
    return bool(doc['enabled'] and doc['approved'] and doc['valid_from'] <= today and
                (not doc['valid_to'] or doc['valid_to'] >= today))

def save_document(name, content, meta, actor, doc_id=None, expected=None):
    if not content or len(content) > MAX_BYTES:
        raise ValueError('Archivo vacío o mayor a 10 MB.')
    pages = extract(name, content)
    name = re.split(r'[/\\]', name)[-1][:180]
    with store.db() as conn:
        old = store.get(conn,'document',doc_id) if doc_id else None
        if doc_id and not old:
            raise LookupError('Documento no encontrado')
        if old and expected != old['revision']:
            raise RevisionConflict('El documento cambió. Recarga antes de reemplazarlo.')
        doc_id = doc_id or store.new_id()
        revision = old['revision'] + 1 if old else 1
        relative = f'files/{doc_id}/{revision}{Path(name).suffix.lower()}'
        target = store.DATA_DIR / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        result = dict(meta, id=doc_id, name=name, revision=revision, updated=store.now(),
                      sha256=hashlib.sha256(content).hexdigest(), path=relative, pages=pages,
                      indexed_revision=None, chunks=0)
        store.put(conn,'document',doc_id,result)
        store.audit(conn,actor,'replace_document' if old else 'upload_document',doc_id,old,result)
        return public_doc(result)

def update_document(doc_id, meta, actor, expected):
    with store.db() as conn:
        old = store.get(conn,'document',doc_id)
        if not old:
            raise LookupError('Documento no encontrado')
        if old['revision'] != expected:
            raise RevisionConflict('El documento cambió. Recarga antes de guardarlo.')
        result = dict(old, **meta)
        result.update(revision=old['revision']+1, updated=store.now(), indexed_revision=None, chunks=0)
        store.put(conn,'document',doc_id,result)
        store.audit(conn,actor,'update_document',doc_id,old,result)
        return public_doc(result)

def split_document(doc, config):
    chunks = []
    section = 'Sección general'
    size, overlap = config['chunk_size'], config['overlap']
    for page in doc['pages']:
        text = page['text'].replace('\x00','')
        matches = list(ARTICLE.finditer(text))
        boundaries = [(0,section)]
        for match in matches:
            boundaries.append((match.start(),f'Artículo {match.group(1)}'))
        boundaries.append((len(text),''))
        for i in range(len(boundaries)-1):
            start, section_name = boundaries[i]
            fragment = text[start:boundaries[i+1][0]].strip()
            if not fragment:
                continue
            section = section_name
            offset = 0
            while offset < len(fragment):
                end = min(offset+size,len(fragment))
                if end < len(fragment):
                    split = fragment.rfind(' ',offset+size//2,end)
                    if split > offset:
                        end = split
                part = fragment[offset:end].strip()
                if part:
                    chunks.append({'id':f'{doc["id"]}-r{doc["revision"]}-{len(chunks)+1}',
                        'doc_id':doc['id'],'revision':doc['revision'],'title':doc['title'],
                        'section':section,'page':page['page'],'text':part})
                    if len(chunks) > 512:
                        raise ValueError('Demasiados fragmentos. Divide el documento o aumenta el tamaño de chunk.')
                if end == len(fragment):
                    break
                offset = end-overlap
                if len(chunks) > 512:
                    raise ValueError('Demasiados fragmentos. Divide el documento o aumenta el tamaño de chunk.')
    return chunks

def signature(config):
    return hashlib.sha256(json.dumps({k:config[k] for k in ('chunk_size','overlap','strategy','embedding_model')},sort_keys=True).encode()).hexdigest()

def still_current(chunks):
    with store.db() as conn:
        config=store.get(conn,'config','rag')
        for chunk in chunks:
            doc=store.get(conn,'document',chunk['doc_id'])
            if not doc or not eligible(doc) or doc['revision']!=chunk['revision'] or doc.get('index_signature')!=signature(config):
                return False
    return True

def embed(texts, model, task):
    from google import genai
    from google.genai import types
    s = get_settings()
    if not s.gemini_api_key:
        raise ValueError('Configura GEMINI_API_KEY para el índice semántico.')
    with genai.Client(api_key=s.gemini_api_key, http_options=types.HttpOptions(timeout=15000,retry_options=types.HttpRetryOptions(attempts=1))) as client:
        r = client.models.embed_content(model=model, contents=texts,
            config=types.EmbedContentConfig(task_type=task,output_dimensionality=768))
    values = [e.values for e in r.embeddings or []]
    if len(values) != len(texts) or any(not v for v in values):
        raise ValueError('El proveedor no devolvió todos los embeddings.')
    registrar('embedding', modelo=model, estado='indexacion' if task=='RETRIEVAL_DOCUMENT' else 'consulta')
    return values

def index_document(doc_id, actor):
    with store.db() as conn:
        doc = store.get(conn,'document',doc_id)
        config = store.get(conn,'config','rag')
    if not doc:
        raise LookupError('Documento no encontrado')
    chunks = split_document(doc,config)
    vectors = [None]*len(chunks)
    if config['strategy']=='hybrid':
        for start in range(0,len(chunks),16):
            batch = chunks[start:start+16]
            vectors[start:start+16] = embed([c['text'] for c in batch], config['embedding_model'],'RETRIEVAL_DOCUMENT')
    with store.db() as conn:
        current = store.get(conn,'document',doc_id)
        if current['revision'] != doc['revision'] or store.get(conn,'config','rag')['revision'] != config['revision']:
            raise RevisionConflict('Cambió el documento o la configuración durante la indexación. Repite la operación.')
        remaining=conn.execute('SELECT COUNT(*) FROM chunks WHERE doc_id<>?',(doc_id,)).fetchone()[0]
        if remaining+len(chunks)>5000:
            raise ValueError('El índice local admite hasta 5000 fragmentos. Reduce el corpus o aumenta el tamaño de fragmento.')
        conn.execute('DELETE FROM chunk_search WHERE id IN (SELECT id FROM chunks WHERE doc_id=?)',(doc_id,))
        conn.execute('DELETE FROM chunks WHERE doc_id=?',(doc_id,))
        for chunk,vector in zip(chunks,vectors):
            conn.execute('INSERT INTO chunks VALUES(?,?,?,?,?,?,?,?,?)',
                tuple(chunk[k] for k in ('id','doc_id','revision','title','section','page','text')) +
                (json.dumps(vector) if vector else None, config['embedding_model'] if vector else None))
            conn.execute('INSERT INTO chunk_search(id,title,section,text) VALUES(?,?,?,?)',tuple(chunk[k] for k in ('id','title','section','text')))
        current.update(indexed_revision=current['revision'], chunks=len(chunks), index_config_revision=config['revision'],index_signature=signature(config))
        store.put(conn,'document',doc_id,current)
        store.audit(conn,actor,'index_document',doc_id,{'indexed_revision':doc.get('indexed_revision')},
                    {'revision':current['revision'],'chunks':len(chunks),'config_revision':config['revision']})
    return {'document':public_doc(current), 'chunks':chunks}

def retrieve(query, config=None):
    config = config or store.settings()
    warning = None
    with store.db() as conn:
        docs = {d['id']:d for d in store.all_records(conn,'document') if eligible(d) and d['indexed_revision']==d['revision'] and d.get('index_signature')==signature(config)}
        if not docs:
            return {'chunks':[], 'strategy':'lexical','warning':'No hay documentos vigentes, aprobados e indexados con la configuración actual.'}
        params = list(docs)
        placeholders = ','.join('?' for _ in params)
        terms = list(dict.fromkeys(t.lower() for t in re.findall(r'[^\W_]{2,}',query,flags=re.UNICODE) if t.lower() not in STOP))[:24]
        lexical = []
        if terms:
            match = ' OR '.join('"'+t+'"' for t in terms)
            lexical = [dict(r) for r in conn.execute(f'''SELECT c.*, bm25(chunk_search) AS rank FROM chunk_search
                JOIN chunks c ON c.id=chunk_search.id WHERE chunk_search MATCH ? AND c.doc_id IN ({placeholders})
                ORDER BY rank LIMIT 40''',[match]+params)]
        candidates = {c['id']:c for c in lexical}
        scores = {c['id']:1/(60+i+1) for i,c in enumerate(lexical)}
        semantic = []
        rows = [dict(r) for r in conn.execute(f'SELECT * FROM chunks WHERE doc_id IN ({placeholders}) AND vector IS NOT NULL AND embedding_model=? LIMIT 5000',params+[config['embedding_model']])] if config['strategy']=='hybrid' else []
    if rows:
        try:
            q = embed([query],config['embedding_model'],'RETRIEVAL_QUERY')[0]
            qnorm = math.sqrt(sum(x*x for x in q)) or 1
            for row in rows:
                v = json.loads(row['vector'])
                similarity = sum(a*b for a,b in zip(q,v))/(qnorm*(math.sqrt(sum(x*x for x in v)) or 1))
                if similarity >= config['min_similarity']:
                    semantic.append((similarity,row))
            semantic.sort(key=lambda x:x[0],reverse=True)
            for i,(_,row) in enumerate(semantic[:40]):
                candidates[row['id']] = row
                scores[row['id']] = scores.get(row['id'],0)+1/(60+i+1)
        except Exception:
            warning = 'Búsqueda semántica no disponible; se usó el índice léxico.'
            registrar('embedding',modelo=config['embedding_model'],error='embedding_no_disponible')
    selected = sorted(candidates.values(),key=lambda c:scores[c['id']],reverse=True)[:config['top_k']]
    result = []
    for chunk in selected:
        doc = docs[chunk['doc_id']]
        result.append({k:chunk[k] for k in ('id','doc_id','revision','title','section','page','text')} |
                      {'source_url':doc['source_url'],'kind':doc['kind'],'sha256':doc['sha256'],'score':round(scores[chunk['id']],5)})
    return {'chunks':result,'strategy':'hybrid' if semantic else 'lexical','warning':warning}

"""Page-preserving ingestion and SQLite FTS5 BM25 retrieval. No vector claims."""
import hashlib
import io
import re
from pypdf import PdfReader
from .store import db, now, get_chunks

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()

def split_spans(text, size=1100, overlap=180):
    """Offsets cover the original text, including whitespace, without gaps."""
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError('Require size > 0 and 0 <= overlap < size.')
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = max(text.rfind('\n', start+size//2,end), text.rfind('. ',start+size//2,end))
            if boundary > start:
                end = boundary+1
        yield start, end
        if end == len(text):
            break
        start = max(start+1, end-overlap)

def split_text(text, size=1100, overlap=180):
    for start, end in split_spans(text, size, overlap):
        yield text[start:end]

def ingest_pages(title, filename, pages, *, kind='reference', origin='uploaded', url='', license='', raw=None):
    joined = '\n'.join(pages)
    if not joined.strip():
        raise ValueError('No readable text found. OCR is not included; upload a text version instead.')
    if len(joined)>240_000 or len(pages)>80:
        raise ValueError('Use a document of at most 80 pages and 240,000 extracted characters.')
    digest = hashlib.sha256(raw if raw is not None else joined.encode()).hexdigest()
    sid = 'src-'+hashlib.sha256((digest+kind+title).encode()).hexdigest()[:12]
    with db() as c:
        existing = c.execute('SELECT id FROM sources WHERE id=?',(sid,)).fetchone()
        if existing:
            return sid
        c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?,?)', (sid,title,filename,kind,origin,url,license,digest,now(),len(pages)))
        n=0
        for page_no, text in enumerate(pages,1):
            for part in split_text(text):
                n+=1
                cid=f'{sid}-c{n:04d}'
                locator=f'Page {page_no}' if filename.lower().endswith('.pdf') else f'Section {page_no}'
                c.execute('INSERT INTO chunks VALUES (?,?,?,?)',(cid,sid,locator,part))
                c.execute('INSERT INTO search VALUES (?,?)',(cid,part))
    return sid

def ingest_bytes(filename, data, kind, origin='uploaded'):
    if filename.lower().endswith('.pdf'):
        if not data.startswith(b'%PDF'):
            raise ValueError('This file is not a valid PDF.')
        try:
            pdf=PdfReader(io.BytesIO(data))
            if pdf.is_encrypted or len(pdf.pages)>80:
                raise ValueError('Use an unencrypted PDF of at most 80 pages.')
            pages=[p.extract_text(extraction_mode='layout') or '' for p in pdf.pages]
        except ValueError:
            raise
        except Exception as e:
            raise ValueError('PDF could not be parsed. Upload its text version.') from e
    else:
        try:
            pages=[data.decode('utf-8-sig')]
        except UnicodeDecodeError as e:
            raise ValueError('Text documents must use UTF-8 encoding.') from e
    return ingest_pages(filename,filename,pages,kind=kind,origin=origin,raw=data)

def retrieve(query, limit=8, source_ids=None):
    if limit <= 0 or source_ids is not None and not source_ids:
        return []
    stop={'what','which','when','does','this','that','with','have','from','would','could','about','there','their','please','should','will','into','they','them','your','help'}
    tokens=list(dict.fromkeys(w for w in re.findall(r'[a-zA-Z0-9]+',query.lower()) if len(w)>2 and w not in stop))[:24]
    if not tokens:
        return []
    match=' OR '.join('"'+w+'"' for w in tokens)
    params=[match]
    scope=''
    if source_ids is not None:
        ids=sorted(source_ids)
        scope=' AND ch.source_id IN ('+','.join('?' for _ in ids)+')'
        params.extend(ids)
    params.append(limit)
    with db() as c:
        rows=c.execute('SELECT ch.*,s.title,s.origin,s.url,s.kind,bm25(search) AS rank FROM search JOIN chunks ch ON ch.id=search.chunk_id JOIN sources s ON s.id=ch.source_id WHERE search MATCH ?'+scope+' ORDER BY rank,ch.id LIMIT ?',params).fetchall()
    return [dict(r) for r in rows]

def valid_citations(citations, chunks):
    """Validate IDs and exact normalized excerpts. This does not certify semantics."""
    by_id={c['id']:c for c in chunks}
    verified=[]
    for ref in citations:
        if not isinstance(ref,dict) or not isinstance(ref.get('chunk_id'),str) or not isinstance(ref.get('quote'),str):
            continue
        cid=ref.get('chunk_id',''); quote=normalize(ref.get('quote',''))
        if cid not in by_id or len(quote)<16 or len(quote)>650:
            continue
        c=by_id[cid]
        if quote.lower() not in normalize(c['content']).lower():
            continue
        verified.append({'chunk_id':cid,'quote':quote,'source_id':c['source_id'],'title':c['title'],'locator':c['locator'],'origin':c['origin'],'url':c['url']})
    return verified

def evidence_for(sid, needle=None):
    chunks=get_chunks(sid)
    chosen=next((c for c in chunks if needle and needle.lower() in c['content'].lower()), chunks[0] if chunks else None)
    if not chosen:
        return []
    text=chosen['content']
    start=max(0,text.lower().find(needle.lower())-60) if needle else 0
    quote=normalize(text[start:start+450])
    return valid_citations([{'chunk_id':chosen['id'],'quote':quote}],chunks)

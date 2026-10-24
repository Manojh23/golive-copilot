"""Bounded, balanced context selection across all active document positions."""
from .store import get_chunks, list_sources
from .rag import retrieve

QUERIES = (
    'responsibility ownership nurse physician front desk review escalation',
    'notification alert recipient workload volume shift',
    'duplicate manual entry automation task workflow',
    'required input output interface operation laboratory missing',
    'unavailable error failure fallback downtime',
    'training completion validation pilot evidence',
    'privacy processing hosting region policy',
    'referral receipt appointment confirmation closure follow up',
)

def select_review_context(project, per_source=24, char_budget=65000):
    selected=[]; seen=set(); used=0; coverage=[]
    main_ids=list(dict.fromkeys(s for s in (project.get('current_source_id'),project.get('new_source_id')) if s))
    for sid in main_ids:
        chunks=get_chunks(sid)
        # Small dossiers are read in full. Large dossiers are searched without a prefix cutoff.
        candidates=list(chunks) if len(chunks)<=per_source else []
        if not candidates and chunks:
            candidates=[chunks[0],chunks[-1]]
            for query in QUERIES:
                candidates.extend(retrieve(query,limit=3,source_ids={sid}))
            # A spread of positions fills unused slots when keywords do not match.
            candidates.extend(chunks[round(i*(len(chunks)-1)/(per_source-1))] for i in range(per_source))
        count=0
        for chunk in candidates:
            if count>=per_source:
                break
            if chunk['id'] in seen or used+len(chunk['content'])>char_budget:
                continue
            selected.append(chunk); seen.add(chunk['id']); used+=len(chunk['content']); count+=1
        coverage.append({'source_id':sid,'title':chunks[0]['title'] if chunks else sid,
                         'selected_chunks':count,'total_chunks':len(chunks),'complete':count==len(chunks)})
    refs={s['id'] for s in list_sources() if s['kind'] in ('reference','research') and s['id'] not in main_ids}
    for chunk in retrieve(' '.join(QUERIES[:4]),limit=8,source_ids=refs):
        if chunk['id'] not in seen and used+len(chunk['content'])<=char_budget:
            selected.append(chunk); seen.add(chunk['id']); used+=len(chunk['content'])
    return selected, {'sources':coverage,'context_characters':used,'character_budget':char_budget,
                      'selected_chunk_ids':[c['id'] for c in selected],
                      'limitation':'Selection coverage is not an accuracy measure. Unselected passages may contain relevant facts.'}

import asyncio
import pytest
from hypothesis import given, settings, strategies as st
from backend import rag, store, seed, engine, llm
from backend.retrieval import select_review_context

@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setenv('GOLIVE_DB', str(tmp_path/'isolated.sqlite3'))
    store.init_db(); seed.seed()

@given(text=st.text(max_size=3000), size=st.integers(2,150), fraction=st.floats(min_value=0,max_value=0.95))
@settings(max_examples=120, deadline=None)
def test_chunk_offsets_cover_every_original_character(text,size,fraction):
    spans=list(rag.split_spans(text,size,int((size-1)*fraction)))
    if not text:
        assert spans==[]; return
    assert spans[0][0]==0 and spans[-1][1]==len(text)
    rebuilt=''; previous_end=0
    for start,end in spans:
        assert start<=previous_end<end and 0<end-start<=size
        rebuilt+=text[previous_end:end]; previous_end=end
    assert rebuilt==text

@given(size=st.integers(1,100), extra=st.integers(0,100))
def test_invalid_chunk_parameters_fail_instead_of_hanging(size,extra):
    with pytest.raises(ValueError): list(rag.split_text('abc',size,size+extra))

def example_chunk(content):
    return {'id':'known','source_id':'source','title':'test','locator':'Section 1','origin':'uploaded','url':'','content':content}

@given(st.text(alphabet='abcdefghijklmnopqrstuvwxyz ',min_size=16,max_size=400).filter(lambda s:len(rag.normalize(s))>=16))
def test_citation_accepts_normalized_source_but_rejects_invention(quote):
    chunk=example_chunk('Prefix '+quote+' suffix')
    assert rag.valid_citations([{'chunk_id':'known','quote':quote}],[chunk])
    assert not rag.valid_citations([{'chunk_id':'invented','quote':quote}],[chunk])
    assert not rag.valid_citations([{'chunk_id':'known','quote':quote+' NONEXISTENT_MARKER_989'}],[chunk])

@given(st.one_of(st.none(),st.integers(),st.lists(st.integers()),st.dictionaries(st.text(max_size=10),st.integers())))
def test_malformed_citation_values_are_rejected(value):
    assert not rag.valid_citations([{'chunk_id':'known','quote':value}], [example_chunk('A sufficiently long source passage.')])

def test_active_scope_is_applied_before_fts_limit(workspace):
    # All retired hits outrank the active document. A global LIMIT 100 loses it.
    for i in range(105):
        rag.ingest_pages(f'Retired {i}',f'old{i}.txt',['lactate '*10],kind='proposed_app')
    sid=rag.ingest_pages('Active','active.txt',['lactate plus '+('unrelated '*400)],kind='proposed_app')
    found=rag.retrieve('lactate',source_ids={sid})
    assert found and all(c['source_id']==sid for c in found)
    assert rag.retrieve('lactate',source_ids=set())==[]

def test_late_relevant_passage_is_selected_and_retired_version_excluded(workspace):
    pages=['Administrative boilerplate. '*80 for _ in range(25)]
    pages[20]='Referral closure requires appointment confirmation; receipt is not appointment confirmation.'
    sid=rag.ingest_pages('New referral guide','new.txt',pages,kind='proposed_app')
    project=store.get_setting('project'); old=project['new_source_id']; project['new_source_id']=sid
    chunks,coverage=select_review_context(project)
    assert any('receipt is not appointment confirmation' in c['content'] for c in chunks)
    assert not any(c['source_id']==old for c in chunks)
    row=next(s for s in coverage['sources'] if s['source_id']==sid)
    assert row['total_chunks']>24 and row['selected_chunks']<=24 and not row['complete']
    assert coverage['context_characters']<=coverage['character_budget']

def test_long_document_fact_pass_rejects_fabricated_quote(workspace,monkeypatch):
    sid=rag.ingest_pages('Long guide','long.txt',['Training completion is required before pilot launch. '+str(i) for i in range(16)],kind='proposed_app')
    project=store.get_setting('project'); project['new_source_id']=sid; store.set_setting('project',project)
    chunk=store.get_chunks(sid)[0]; calls=[]
    async def generate(prompt,output_type):
        calls.append(output_type)
        if output_type is llm.FactOutput:
            return llm.FactOutput(facts=[
                llm.WorkflowFact(subject='Staff',relationship='requires',object='training',citations=[llm.Citation(chunk_id=chunk['id'],quote='Training completion is required before pilot launch.')]),
                llm.WorkflowFact(subject='Staff',relationship='completed',object='training',citations=[llm.Citation(chunk_id=chunk['id'],quote='All staff have completed training already.')])]),{'model':'mock','usage':{}}
        assert '"relationship": "requires"' in prompt
        assert '"relationship": "completed"' not in prompt
        return llm.AnalysisOutput(impacts=[]),{'model':'mock','usage':{}}
    monkeypatch.setattr(llm,'generate',generate)
    result=asyncio.run(engine.analyze(True))
    assert calls==[llm.FactOutput,llm.AnalysisOutput]
    a=result['assessment']
    assert a['discarded_facts']==1 and len(a['extracted_facts'])==1
    assert a['coverage']['sources'][-1]['complete']

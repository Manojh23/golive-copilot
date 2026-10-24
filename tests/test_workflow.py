import io
import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader
from backend.app import app
from backend import rag, store, engine, llm

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('GOLIVE_DB',str(tmp_path/'test.sqlite3'))
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    with TestClient(app) as c:
        yield c

def analyze(client):
    response=client.post('/api/analyze',json={'use_llm':False})
    assert response.status_code==200
    return response.json()

def test_complete_review_export_feedback_journey(client):
    assert client.get('/api/health').json()['live_llm_configured'] is False
    result=analyze(client)
    expected=json.loads((store.ROOT/'data/evaluation_cases.json').read_text())['expected_rule_ids']
    assert set(i['id'] for i in result['impacts'])==set(expected)
    assert all(len(i['citations'])==2 for i in result['impacts'])
    assert client.patch('/api/impacts/duplicate_entry',json={'status':'approved','owner':'Nursing education lead','review_note':'Checked against the fictional pilot plan.'}).status_code==200
    pdf=client.get('/api/exports/brief.pdf?role=Nurse')
    assert pdf.status_code==200
    text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf.content)).pages)
    assert 'Duplicate entry' in text and 'Fictional' in text
    assert 'Local validation evidence is missing' not in text
    assert client.get('/api/exports/checklist.csv').status_code==200
    assert client.post('/api/feedback',json={'role':'Nurse','text':'I entered the same values twice today.'}).status_code==200
    assert client.post('/api/feedback/demo').json()['added']==20
    assert client.post('/api/feedback/demo').json()['added']==0
    groups=client.post('/api/feedback/analyze',json={'use_llm':False}).json()['clusters']
    assert sum(len(g['reports']) for g in groups)==21
    assert any(g['linked_impact_id']=='duplicate_entry' for g in groups)
    assert all(not g['confirmed'] for g in groups)

def test_changed_inputs_block_old_approval(client):
    analyze(client)
    client.patch('/api/impacts/duplicate_entry',json={'status':'approved','owner':'Reviewer'})
    r=client.post('/api/sources',files={'file':('new.txt',b'New evidence says the workflow needs additional review.')},data={'kind':'reference'})
    assert r.status_code==200
    assert client.get('/api/state').json()['assessment']['stale']
    assert client.get('/api/exports/brief.pdf').status_code==409
    assert client.patch('/api/impacts/duplicate_entry',json={'status':'approved','owner':'Reviewer'}).status_code==409
    updated=analyze(client)
    assert next(i for i in updated['impacts'] if i['id']=='duplicate_entry')['status']=='open'

def test_unchanged_rerun_preserves_review(client):
    analyze(client)
    client.patch('/api/impacts/duplicate_entry',json={'status':'approved','owner':'Reviewer'})
    assert next(i for i in analyze(client)['impacts'] if i['id']=='duplicate_entry')['status']=='approved'

def test_no_demo_findings_for_unrelated_uploaded_app(client):
    client.post('/api/sources',files={'file':('different-app.txt',b'This scheduling app sends appointment reminders. No clinical screening is performed.')},data={'kind':'proposed_app'})
    r=analyze(client)
    assert r['impacts']==[]
    assert 'Custom documents' in r['notice']
    assert client.get('/api/evaluation').json()['applicable'] is False

def test_citation_validation_rejects_fabrications(client):
    chunks=store.get_chunks()
    good=chunks[0]
    refs=[{'chunk_id':'invented','quote':'a supposedly supporting passage'}, {'chunk_id':good['id'],'quote':'This sentence does not occur in the document.'}, {'chunk_id':good['id'],'quote':rag.normalize(good['content'][:120])}]
    validated=rag.valid_citations(refs,chunks)
    assert len(validated)==1 and validated[0]['chunk_id']==good['id']

def test_retrieval_uses_indexed_evidence_and_abstains(client):
    r=client.post('/api/ask',json={'question':'lactate exported laboratory feed','use_llm':False}).json()
    assert r['mode']=='retrieval_only' and r['citations']
    assert any('lactate' in c['quote'].lower() for c in r['citations'])
    empty=client.post('/api/ask',json={'question':'zyxwvu nonexistentqwerty','use_llm':False}).json()
    assert not empty['citations'] and 'No matching' in empty['answer']

def test_no_live_key_never_fake_generation(client):
    r=client.post('/api/analyze',json={'use_llm':True})
    assert r.status_code==409
    assert client.get('/api/state').json()['assessment'] is None

def test_resolve_requires_owner_and_note(client):
    analyze(client)
    assert client.patch('/api/impacts/duplicate_entry',json={'status':'approved'}).status_code==422
    assert client.patch('/api/impacts/duplicate_entry',json={'status':'resolved','owner':'Reviewer'}).status_code==422
    assert client.patch('/api/impacts/duplicate_entry',json={'status':'resolved','owner':'Reviewer','review_note':'Tested the agreed revised process.'}).status_code==200

def test_document_validation(client):
    assert client.post('/api/sources',files={'file':('bad.exe',b'anything')}).status_code==400
    assert client.post('/api/sources',files={'file':('bad.pdf',b'not a pdf')}).status_code==400
    assert client.post('/api/sources',files={'file':('empty.txt',b'  ')}).status_code==400
    assert client.post('/api/sources',files={'file':('big.txt',b'x'*(5*1024*1024+1))}).status_code==413

def test_config_edits_change_findings_and_invalidate_benchmark(client):
    analyze(client)
    assert client.patch('/api/project',json={'checks':{'training_recorded':True,'alert_owner':'Charge nurse'}}).status_code==200
    ids={i['id'] for i in analyze(client)['impacts']}
    assert 'training_missing' not in ids and 'alert_owner' not in ids
    assert client.get('/api/evaluation').json()['applicable'] is False
    assert client.patch('/api/project',json={'checks':{'training_recorded':'yes'}}).status_code==422

def test_grounded_model_path_rejects_uncited_proposals(client,monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','test-key-not-a-real-credential')
    chunk=store.get_chunks(store.get_setting('project')['new_source_id'])[0]
    async def fake_generate(prompt,output_type):
        output=llm.AnalysisOutput(impacts=[
          llm.GeneratedImpact(title='Unsupported claim',category='Review',roles=['Nurse'],impact='Unfounded.',action='Review.',citations=[llm.Citation(chunk_id='fake',quote='A fabricated quotation that does not exist.')]),
          llm.GeneratedImpact(title='Potential task change',category='Workflow',roles=['Nurse'],impact='Potential task change needing review.',action='Confirm local responsibilities.',citations=[llm.Citation(chunk_id=chunk['id'],quote=rag.normalize(chunk['content'][:180]))])])
        return output,{'model':'mock-model','usage':{},'prompt_version':'test'}
    monkeypatch.setattr(llm,'generate',fake_generate)
    r=client.post('/api/analyze',json={'use_llm':True}).json()
    assert r['assessment']['discarded_ai_findings']==1
    proposals=[i for i in r['impacts'] if i['origin']=='llm_proposal']
    assert len(proposals)==1 and proposals[0]['status']=='open'

def test_structured_gemini_transport(client,monkeypatch):
    import httpx
    monkeypatch.setenv('GEMINI_API_KEY','unit-test-credential')
    monkeypatch.setenv('GEMINI_MODEL','test-text-model')
    original=httpx.AsyncClient
    def handler(request):
        assert request.headers['x-goog-api-key']=='unit-test-credential'
        payload=json.loads(request.content)
        assert payload['generationConfig']['responseMimeType']=='application/json'
        assert 'responseJsonSchema' in payload['generationConfig']
        return httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'{"impacts":[]}' }]}}],'usageMetadata':{'totalTokenCount':100}})
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    r=client.post('/api/analyze',json={'use_llm':True})
    assert r.status_code==200 and r.json()['assessment']['model']=='test-text-model'

def test_benchmark_is_real_aggregate_not_patient_endpoint(client):
    data=client.get('/api/benchmark').json()
    assert data['available'] and data['cases']>1000 and data['events']>15000
    assert data['sha256']=='20f844ab39f96045daff8470448c1d3fb47dfebf3a9fd5dc21bb80995d2cb6bb'
    assert 'patients' not in data and 'traces' not in data
    sources=client.get('/api/state').json()['sources']
    assert any(s['origin']=='public_research' and 'Duke' in s['title'] for s in sources)

def test_frontend_and_api_share_one_server(client):
    page=client.get('/')
    assert page.status_code==200 and 'GoLive' in page.text
    assert 'GEMINI_API_KEY' not in client.get('/api/state').text

def test_feedback_relationship_review_persists_and_is_audited(client):
    analyze(client)
    client.post('/api/feedback/demo')
    client.post('/api/feedback/analyze',json={'use_llm':False})
    r=client.patch('/api/feedback/groups/duplicate_entry',json={'review_status':'confirmed','owner':'Nursing lead','note':'Reviewed the report and pilot plan.','linked_impact_id':'duplicate_entry'})
    assert r.status_code==200 and r.json()['confirmed']
    s=client.get('/api/state').json()
    assert next(g for g in s['clusters'] if g['id']=='duplicate_entry')['review_owner']=='Nursing lead'
    assert any(a['action']=='feedback_relationship_reviewed' for a in s['audit'])
    assert all(f['origin']=='synthetic' for f in s['feedback'])

def test_feedback_link_cannot_confirm_unknown_or_stale_finding(client):
    analyze(client);client.post('/api/feedback/demo')
    body={'review_status':'confirmed','owner':'Reviewer','note':'Checked the report.'}
    assert client.patch('/api/feedback/groups/duplicate_entry',json=body).status_code==422
    assert client.patch('/api/feedback/groups/duplicate_entry',json={**body,'linked_impact_id':'fabricated'}).status_code==422
    client.patch('/api/project',json={'name':'Changed workspace'})
    assert client.patch('/api/feedback/groups/duplicate_entry',json={**body,'linked_impact_id':'duplicate_entry'}).status_code==409

def test_replaced_current_workflow_disables_demo_rules(client):
    client.post('/api/sources',files={'file':('clinic.txt',b'Our clinic has a different workflow and no EarlyWatch pilot.')},data={'kind':'current_workflow'})
    assert analyze(client)['impacts']==[]

def test_invalid_inventory_and_null_name_rejected(client):
    assert client.patch('/api/project',json={'name':None}).status_code==422
    assert client.patch('/api/project',json={'current_apps':[]}).status_code==422
    assert client.patch('/api/project',json={'current_apps':[{'name':'New app','role':'Nurse','purpose':'Review','origin':'user_supplied'}]}).status_code==200
    assert analyze(client)['impacts']==[]

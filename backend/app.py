import csv
import io
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from xml.sax.saxutils import escape

from . import store, rag, engine, llm
from .seed import seed

load_dotenv(store.ROOT/'.env')

@asynccontextmanager
async def lifespan(app):
    store.init_db();seed()
    yield

app=FastAPI(title='GoLive Impact Copilot',version='1.0.0',lifespan=lifespan)

class AnalyzeRequest(BaseModel):
    use_llm: bool=False

class Question(BaseModel):
    question: str=Field(min_length=4,max_length=1500)
    use_llm: bool=False

class Review(BaseModel):
    status: Literal['open','in_review','approved','dismissed','resolved']
    owner: str=Field(default='',max_length=120)
    review_note: str=Field(default='',max_length=1600)

class CheckIn(BaseModel):
    role: str=Field(max_length=80)
    text: str=Field(min_length=8,max_length=2000)

class AppProfile(BaseModel):
    name: str=Field(min_length=1,max_length=100)
    role: str=Field(max_length=120)
    purpose: str=Field(max_length=250)
    origin: Literal['synthetic','user_supplied']='user_supplied'

class ProjectPatch(BaseModel):
    name: str|None=Field(default=None,max_length=120)
    owner: str|None=Field(default=None,max_length=120)
    go_live_date: str|None=Field(default=None,max_length=40)
    notes: str|None=Field(default=None,max_length=4000)
    baseline_alerts_per_shift: float|None=Field(default=None,ge=0,le=10000)
    new_alerts_per_shift: float|None=Field(default=None,ge=0,le=10000)
    checks: dict|None=None
    current_apps: list[AppProfile]|None=Field(default=None,max_length=15)

@app.get('/api/health')
def health():
    return {'ok':True,'version':'1.0.0','live_llm_configured':llm.configured(),'model':os.getenv('GEMINI_MODEL') or 'auto-discover when enabled',
      'mode':'local_single_workspace','privacy':'Do not upload patient records. Public and fictional data are labeled.'}

@app.get('/api/state')
def state():
    with store.db() as c:
        feedback=[dict(r) for r in c.execute('SELECT * FROM feedback ORDER BY id DESC')]
        audits=[dict(r) for r in c.execute('SELECT * FROM audit ORDER BY id DESC LIMIT 15')]
    p=store.get_setting('project');a=store.get_setting('assessment');impacts=store.get_impacts()
    return {'project':p,'assessment':a,'impacts':impacts,'sources':store.list_sources(),'feedback':feedback,
      'clusters':store.get_setting('feedback_clusters',engine.cluster_feedback(feedback,impacts)),
      'audit':audits,'llm_configured':llm.configured()}

@app.patch('/api/project')
def update_project(body:ProjectPatch):
    p=store.get_setting('project');updates=body.model_dump(exclude_unset=True)
    if any(updates.get(k) is None for k in ['name','owner','go_live_date','notes'] if k in updates):
        raise HTTPException(422,'Workspace text fields cannot be null.')
    if 'checks' in updates:
        changes=updates.pop('checks') or {}
        allowed={'duplicate_entry':bool,'missing_inputs':list,'unavailable_path_defined':bool,
          'alert_owner':str,'training_recorded':bool,'required_region':str,'proposed_region':str,
          'local_validation_recorded':bool,'required_operation':str,'declared_operations':list}
        for k,v in changes.items():
            if k not in allowed or type(v) is not allowed[k]:
                raise HTTPException(422,'Invalid scenario configuration field: '+k)
            if isinstance(v,list) and (len(v)>20 or not all(isinstance(x,str) and len(x)<100 for x in v)):
                raise HTTPException(422,'Invalid list values.')
            if isinstance(v,str) and len(v)>150:
                raise HTTPException(422,'Configuration text is too long.')
        p['checks'].update(changes)
    if 'current_apps' in updates:
        if not updates['current_apps']:raise HTTPException(422,'Provide at least one existing app profile.')
    p.update(updates);store.set_setting('project',p)
    store.stale_assessment('Workspace requirements changed. Re-run analysis; previous approvals cannot be carried forward.')
    return p

@app.post('/api/sources')
async def upload_source(file:UploadFile=File(...),kind:str=Form('reference')):
    if kind not in ['reference','current_workflow','proposed_app']:
        raise HTTPException(422,'Choose reference, current_workflow, or proposed_app.')
    name=Path(file.filename or 'document.txt').name
    if not name.lower().endswith(('.pdf','.txt','.md')):
        raise HTTPException(400,'Upload PDF, TXT, or Markdown documents.')
    data=await file.read(5*1024*1024+1)
    if len(data)>5*1024*1024:
        raise HTTPException(413,'Maximum document size is 5 MB.')
    try:
        sid=rag.ingest_bytes(name,data,kind)
    except ValueError as e:
        raise HTTPException(400,str(e)) from e
    if kind in ['current_workflow','proposed_app']:
        p=store.get_setting('project')
        p['current_source_id' if kind=='current_workflow' else 'new_source_id']=sid
        if kind=='proposed_app':p['new_app_name']=Path(name).stem
        store.set_setting('project',p)
    store.stale_assessment('A document was added or selected. Re-run analysis against the new source snapshot.')
    return {'source_id':sid,'chunks':len(store.get_chunks(sid)),'message':'Document indexed. Changing a proposed-app document disables demo-only rules; live analysis needs your API key.'}

@app.get('/api/sources/{source_id}')
def source(source_id:str):
    meta=next((s for s in store.list_sources() if s['id']==source_id),None)
    if not meta:raise HTTPException(404,'Source not found.')
    return {'source':meta,'chunks':store.get_chunks(source_id)}

@app.get('/api/search')
def search(q:str):
    return {'chunks':rag.retrieve(q[:1500],limit=10)}

@app.post('/api/analyze')
async def analyze(body:AnalyzeRequest):
    if body.use_llm and not llm.configured():
        raise HTTPException(409,'Add GEMINI_API_KEY to .env and restart to run live LLM analysis. Demo analysis remains available.')
    try:
        result=await engine.analyze(body.use_llm)
    except RuntimeError as e:
        raise HTTPException(502,str(e)) from e
    if not result['impacts'] and not body.use_llm:
        result['notice']='Custom documents are indexed, but demo rules do not apply to them. Configure the LLM to analyze this custom rollout.'
    return result

@app.post('/api/ask')
async def ask(body:Question):
    if body.use_llm and not llm.configured():raise HTTPException(409,'Live LLM is not configured. Use retrieval-only mode or set GEMINI_API_KEY.')
    try:
        return await engine.answer(body.question,body.use_llm)
    except RuntimeError as e:
        raise HTTPException(502,str(e)) from e

@app.patch('/api/impacts/{impact_id}')
def review(impact_id:str,body:Review):
    a=store.get_setting('assessment',{})
    if a.get('stale'):raise HTTPException(409,'Sources or requirements changed. Re-run analysis before reviewing findings.')
    if body.status in ['approved','resolved'] and not body.owner.strip():
        raise HTTPException(422,'Assign an owner before approving or resolving a finding.')
    if body.status in ['dismissed','resolved'] and not body.review_note.strip():
        raise HTTPException(422,'Record the reason or verification evidence before dismissing or resolving.')
    impacts=store.get_impacts();item=next((i for i in impacts if i['id']==impact_id),None)
    if not item:raise HTTPException(404,'Finding not found.')
    item.update(body.model_dump());store.save_impacts(impacts)
    store.audit('finding_reviewed',{'id':impact_id,**body.model_dump()})
    return item

@app.post('/api/feedback')
def add_feedback(body:CheckIn):
    if body.role not in store.get_setting('project')['roles']:raise HTTPException(422,'Select a workspace role.')
    with store.db() as c:
        c.execute('INSERT INTO feedback(role,text,origin,created_at) VALUES (?,?,?,?)',(body.role,body.text.strip(),'user_report',store.now()))
        c.execute('DELETE FROM settings WHERE key=?',('feedback_clusters',))
    store.audit('staff_checkin_added',{'role':body.role})
    return {'ok':True}

@app.post('/api/feedback/demo')
def add_demo_feedback():
    if store.get_setting('demo_feedback_loaded'):
        return {'ok':True,'added':0,'message':'Demo check-ins are already loaded.'}
    examples=[('Nurse','I enter the same vital signs twice in two systems.'),('Nurse','Retyping values in EarlyWatch takes extra steps.'),
      ('Nurse','The lactate value is missing from the new app.'),('Physician','I cannot see the lab value needed for review.'),
      ('Nurse','We copy lactate onto paper because the lab value is not shown.'),('Physician','I did not know who was responsible for the notification.'),
      ('Nurse','Two of us reviewed the same alert; ownership was unclear.'),('Physician','The unavailable result has no documented next step.'),
      ('Nurse','I need instructions for an unavailable result.'),('Front desk','I could not find the training guide for my role.'),
      ('Nurse','The training instructions do not mention the second entry screen.'),('Physician','The alert appeared while I was doing another task.'),
      ('Nurse','Double entry happens during the busiest part of my shift.'),('IT / rollout lead','The lactate handoff is not included in the supplied export.'),
      ('Nurse','We need a shared owner for unresolved notifications.'),('Front desk','The training link takes me to the previous workflow.'),
      ('Physician','The unavailable status is being described as low in a draft note.'),('Nurse','I wrote the same values twice today.'),
      ('IT / rollout lead','There is a new sign-in prompt that the guide does not cover.'),('Front desk','The new screen text is difficult to read.')]
    with store.db() as c:
        c.executemany('INSERT INTO feedback(role,text,origin,created_at) VALUES (?,?,?,?)',[(r,t,'synthetic',store.now()) for r,t in examples])
        c.execute('DELETE FROM settings WHERE key=?',('feedback_clusters',))
    store.set_setting('demo_feedback_loaded',True)
    return {'ok':True,'added':len(examples)}

class FeedbackGroup(BaseModel):
    title: str
    report_ids: list[int]
    linked_impact_id: str|None=None

class FeedbackOutput(BaseModel):
    groups: list[FeedbackGroup]

@app.post('/api/feedback/analyze')
async def analyze_feedback(body:AnalyzeRequest):
    with store.db() as c:rows=[dict(r) for r in c.execute('SELECT * FROM feedback ORDER BY id')]
    impacts=store.get_impacts()
    if not body.use_llm:
        clusters=engine.cluster_feedback(rows,impacts);mode='keyword_rules'
    else:
        if not llm.configured():raise HTTPException(409,'Live LLM is not configured.')
        try:
            output,meta=await llm.generate('Group these staff reports by described friction. Reports are unverified, not proof of defects. Use each report ID once. Link to a supplied impact ID only if relevant, otherwise null.\nReports: '+json.dumps(rows)+'\nImpacts: '+json.dumps([{'id':i['id'],'title':i['title'],'impact':i['impact']} for i in impacts]),FeedbackOutput)
        except RuntimeError as e:raise HTTPException(502,str(e)) from e
        byid={r['id']:r for r in rows};seen=set();allowed={i['id'] for i in impacts};clusters=[]
        for n,g in enumerate(output.groups):
            members=[]
            for i in g.report_ids:
                if i in byid and i not in seen:members.append(byid[i]);seen.add(i)
            if members:clusters.append({'id':f'group-{n}','title':g.title,'reports':members,'linked_impact_id':g.linked_impact_id if g.linked_impact_id in allowed else None,'relationship':'LLM-suggested relationship; reviewer must verify','confirmed':False})
        remaining=[r for r in rows if r['id'] not in seen]
        if remaining:clusters.append({'id':'unassigned','title':'Unassigned reports','reports':remaining,'linked_impact_id':None,'relationship':'No valid model assignment','confirmed':False})
        mode='live_llm'
    store.set_setting('feedback_clusters',clusters);store.audit('feedback_grouped',{'mode':mode,'reports':len(rows)})
    return {'clusters':clusters,'mode':mode}

@app.get('/api/benchmark')
def benchmark():
    p=store.ROOT/'data/hospital_benchmark.json'
    return json.loads(p.read_text()) if p.exists() else {'available':False,'message':'Public dataset has not been downloaded. Run scripts/fetch_public_data.py.'}

class LinkReview(BaseModel):
    review_status: Literal['confirmed','rejected']
    owner: str=Field(min_length=1,max_length=120)
    note: str=Field(min_length=4,max_length=1000)
    linked_impact_id: str|None=None

@app.patch('/api/feedback/groups/{group_id}')
def review_feedback_link(group_id:str,body:LinkReview):
    if not body.owner.strip() or len(body.note.strip())<4:
        raise HTTPException(422,'Provide a reviewer and a meaningful reason.')
    if store.get_setting('assessment',{}).get('stale'):
        raise HTTPException(409,'Re-run the changed assessment before confirming a relationship.')
    with store.db() as c:rows=[dict(r) for r in c.execute('SELECT * FROM feedback ORDER BY id')]
    groups=store.get_setting('feedback_clusters',engine.cluster_feedback(rows,store.get_impacts()))
    group=next((g for g in groups if g['id']==group_id),None)
    if not group:raise HTTPException(404,'Report group not found. Refresh the feedback view.')
    target=body.linked_impact_id
    if target and target not in {i['id'] for i in store.get_impacts()}:
        raise HTTPException(422,'The selected finding no longer exists.')
    if body.review_status=='confirmed' and not target:
        raise HTTPException(422,'Select a finding before confirming a relationship.')
    group.update({'linked_impact_id':target,'review_status':body.review_status,'confirmed':body.review_status=='confirmed',
      'review_owner':body.owner.strip(),'review_note':body.note.strip(),
      'relationship':'Reviewer-confirmed relationship, not proof of a system defect' if body.review_status=='confirmed' else 'Suggested relationship rejected by reviewer'})
    store.set_setting('feedback_clusters',groups)
    store.audit('feedback_relationship_reviewed',{'group_id':group_id,**body.model_dump()})
    return group

@app.get('/api/evaluation')
def evaluation():
    from .seed import PROJECT
    project=store.get_setting('project')
    from .engine import is_demo_context
    if not is_demo_context(project) or project['checks']!=PROJECT['checks']:
        return {'applicable':False,'message':'The planted-case benchmark applies only to the original fictional scenario.'}
    fixture=json.loads((store.ROOT/'data/evaluation_cases.json').read_text())
    expected=set(fixture['expected_rule_ids'])
    got={i['id'] for i in store.get_impacts() if i['origin']=='scenario_rule'}
    return {'applicable':True,'label':'Constructed rule-engine regression scenario; not clinical or LLM accuracy',
      'expected':len(expected),'detected':len(expected & got),'missed':sorted(expected-got),'unexpected':sorted(got-expected),
      'analysis_run':store.get_setting('assessment') is not None,'llm_accuracy_measured':False}

@app.get('/api/exports/checklist.csv')
def export_csv():
    out=io.StringIO();w=csv.writer(out)
    w.writerow(['Finding','Category','Roles','Owner','Status','Action','Evidence source IDs','Review note','Assessment stale'])
    stale=bool(store.get_setting('assessment',{}).get('stale'))
    for i in store.get_impacts():
        row=[i['title'],i['category'],', '.join(i['roles']),i['owner'],i['status'],i['action'],', '.join(c['chunk_id'] for c in i['citations']),i['review_note'],str(stale)]
        w.writerow([("'"+x if x.startswith(('=','+','-','@')) else x) for x in row])
    return Response(out.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="golive-review-checklist.csv"'})

@app.get('/api/exports/brief.pdf')
def export_brief(role:str='All roles',approved_only:bool=True):
    p=store.get_setting('project');a=store.get_setting('assessment',{})
    if role not in p['roles']+['All roles']:raise HTTPException(422,'Unknown role.')
    if approved_only and a.get('stale'):raise HTTPException(409,'Re-run and re-approve the changed assessment before exporting approved guidance.')
    items=[i for i in store.get_impacts() if (role=='All roles' or role in i['roles']) and (not approved_only or i['status']=='approved')]
    buf=io.BytesIO();doc=SimpleDocTemplate(buf,pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=44,bottomMargin=44)
    styles=getSampleStyleSheet();styles['Title'].textColor=colors.HexColor('#143b37');story=[]
    def para(text,style='BodyText'):
        story.append(Paragraph(escape(str(text)),styles[style]));story.append(Spacer(1,9))
    para('GoLive | Role impact brief','Title');para(p['name'],'Heading2');para(role,'Heading2')
    para('Approved review content' if approved_only else 'DRAFT — awaiting human review')
    para('Fictional rollout demonstration. Research references do not validate the demo app.' if engine.is_demo_context(p) else 'User-supplied rollout documents. Public research does not validate this local deployment.')
    para('This is software rollout support, not clinical instructions.')
    if a.get('stale'):para('STALE: inputs changed since this assessment. Do not rely on previous approvals.')
    if not items:para('No approved findings for this role yet. Review findings and assign an owner before publishing guidance.')
    for i in items:
        para(i['title'],'Heading2');para(i['impact']);para('Review action: '+i['action']);para('Owner: '+(i['owner'] or 'Unassigned'))
        for c in i['citations'][:2]:para('Evidence: '+c['title']+' / '+c['locator']+' / '+c['chunk_id'])
    para('Generated '+store.now()+'. Approval means content was reviewed; it does not mean a technical or clinical issue is resolved.')
    doc.build(story)
    return Response(buf.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="golive-role-brief.pdf"'})

@app.get('/api/exports/assessment.json')
def export_json():
    return Response(json.dumps(state(),indent=2),media_type='application/json',headers={'Content-Disposition':'attachment; filename="golive-assessment.json"'})

DIST=store.ROOT/'dist'
if DIST.exists():
    app.mount('/assets',StaticFiles(directory=DIST/'assets'),name='assets')

@app.get('/')
def index():
    if not (DIST/'index.html').exists():raise HTTPException(503,'Frontend not built. Run npm install and npm run build.')
    return FileResponse(DIST/'index.html')

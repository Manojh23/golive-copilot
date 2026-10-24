import json
from .store import ROOT, get_setting, set_setting, audit
from .rag import ingest_pages

CURRENT='''NORTHSTAR DEMO HOSPITAL — FICTIONAL CURRENT-STATE WORKFLOW
This is constructed evaluation material, not a description of an actual hospital.
Current tools: CareRecord EHR, LabBridge laboratory interface, TeamInbox messaging, and FollowTrack follow-up board.
Nurses record vital signs in CareRecord. Physicians review patient information there. Front-desk staff manage demographics.
LabBridge exports white-cell count and temperature. Lactate is not exported by the configured laboratory feed.
The current Observation interface declares read support only; it does not declare search-type support. This is synthetic interface metadata, not a real vendor statement.
Current workflow accounts for high and low results only. No workflow is defined for an unavailable assessment.
The hospital's fictional data policy requires processing in the United States.
Alert ownership for the new EarlyWatch app has not been assigned.
No EarlyWatch staff training completion or local validation results have been recorded.
Existing entry tasks and review responsibilities must be confirmed by the rollout lead before changes are approved.
'''
PROPOSED='''EARLYWATCH DEMO v1 — FICTIONAL PROPOSED-APP GUIDE
This product, vendor documentation and rollout are synthetic. Do not attribute its capabilities or validation to Duke, Epic, or any real vendor.
EarlyWatch is a demonstration early-warning application. It consumes temperature, white-cell count, and lactate values.
The proposed interface requires Observation search-type support. A declared capability match is not a successful data exchange test.
During the demo pilot nurses must manually enter the same vital signs in EarlyWatch and CareRecord.
Outputs can be high, low, or unavailable. An unavailable assessment must remain distinct from a low result.
The app sends notifications through TeamInbox. The hospital must assign a recipient and an owner for reviewing unresolved notifications.
Training must be completed before the fictional pilot starts. The hospital must approve a local validation plan and review results before clinical use.
This fictional vendor's proposed hosting region is the European Union.
No measured alert rate per patient or per shift is supplied. Do not invent an alert-volume estimate.
'''

PROJECT={
 'name':'Northstar rollout review', 'hospital':'Northstar Demo Hospital (fictional)',
 'new_app_name':'EarlyWatch demo v1', 'workflow':'Early-warning rollout',
 'owner':'Clinical informatics lead', 'go_live_date':'2026-11-09',
 'roles':['Nurse','Physician','Front desk','IT / rollout lead'],
 'current_apps':[
  {'name':'CareRecord','role':'Nurse · Physician','purpose':'Clinical record & vital signs','origin':'synthetic'},
  {'name':'LabBridge','role':'Nurse · IT','purpose':'Laboratory data handoff','origin':'synthetic'},
  {'name':'TeamInbox','role':'Physician · Nurse','purpose':'Team notifications','origin':'synthetic'},
  {'name':'FollowTrack','role':'Front desk','purpose':'Follow-up work queue','origin':'synthetic'}],
 'checks':{'duplicate_entry':True,'missing_inputs':['Lactate'],'unavailable_path_defined':False,
   'alert_owner':'','training_recorded':False,'required_region':'US','proposed_region':'EU',
   'local_validation_recorded':False,'required_operation':'search-type','declared_operations':['read']},
 'baseline_alerts_per_shift':None,'new_alerts_per_shift':None,
 'notes':'The hospital, apps, rollout, local configuration and staff feedback are synthetic. Public hospital research and workflow aggregates are separate reference sources.'
}

def seed():
    if get_setting('project'):
        return
    sid1=ingest_pages('Current workflow · fictional hospital','demo-current-workflow.txt',[CURRENT],kind='current_workflow',origin='synthetic')
    sid2=ingest_pages('EarlyWatch v1 · fictional proposed guide','demo-proposed-app.txt',[PROPOSED],kind='proposed_app',origin='synthetic')
    project={**PROJECT,'current_source_id':sid1,'new_source_id':sid2,'demo_source_id':sid2}
    set_setting('project',project)
    set_setting('seed_sources',{'current':sid1,'proposed':sid2})
    ref=ROOT/'data/reference_sources.json'
    if ref.exists():
        for item in json.loads(ref.read_text()):
            ingest_pages(item['title'],item['filename'],item['pages'],kind='research',origin='public_research',url=item['url'],license=item.get('license','See original source'))
    audit('workspace_created',{'scenario':'synthetic','public_references_separate':True})

"""Prepare attributed public research and aggregate hospital data; never serve raw cases.

The 4TU origin returned HTTP 503 during development. A disclosed Git-LFS mirror is
used for retrieval, with its exact file digest verified. This is not a new hospital
deployment dataset and does not identify software products or establish causality.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from statistics import median
import urllib.request
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL='https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460'
MIRROR='https://media.githubusercontent.com/media/delafuenteh/medical-data-eventlogs/main/Sepsis%20Cases%20-%20IO%20Acts.xes'
EXPECTED_SHA='20f844ab39f96045daff8470448c1d3fb47dfebf3a9fd5dc21bb80995d2cb6bb'
DUKE='https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7714645/fullTextXML'

def fetch(url):
    with urllib.request.urlopen(url,timeout=45) as r:
        data=r.read(15*1024*1024+1)
        if len(data)>15*1024*1024:raise ValueError('Public source exceeded download limit.')
        return data

def summarize_xes(data):
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED_SHA:raise ValueError('Event log digest differs from the reviewed mirror snapshot. Review the new data before accepting it.')
    root=ET.fromstring(data)
    ns={'x':'http://www.xes-standard.org/'}
    traces=root.findall('x:trace',ns)
    if not traces:traces=root.findall('trace')
    activities=Counter();transitions=Counter();lengths=[];boundary_markers=0
    for trace in traces:
        events=trace.findall('x:event',ns) or trace.findall('event')
        names=[]
        for event in events:
            attrs={x.attrib.get('key'):x.attrib.get('value') for x in event}
            name=attrs.get('concept:name','Unknown activity')
            if name in {'α','ω'}:
                boundary_markers+=1
                continue
            activities[name]+=1;names.append(name)
        lengths.append(len(names));transitions.update(zip(names,names[1:]))
    if not lengths:raise ValueError('No event traces were found.')
    return {'available':True,'title':'Sepsis Cases — Event Log','creator':'Felix Mannhardt (2016)',
      'description':'Anonymized historical hospital pathways recorded in an ERP system. One trace is a hospital pathway; activity labels are not app identities.',
      'cases':len(traces),'events':sum(lengths),'median_events_per_case':median(lengths),
      'activities':[{'name':n,'count':c} for n,c in activities.most_common()],
      'transitions':[{'from':a,'to':b,'count':c} for (a,b),c in transitions.most_common(12)],
      'source_url':ORIGINAL,'retrieval_url':MIRROR,'sha256':digest,
      'excluded_boundary_markers':boundary_markers,
      'license':'4TU General Terms of Use; consult the original record. Only computed aggregates are bundled.',
      'license_url':'https://data.4tu.nl/info/about-our-services/terms-of-use',
      'provenance':'Original creator: Felix Mannhardt; publisher: 4TU.ResearchData. Historical coverage: November 2013–June 2015. The disclosed IO Acts mirror adds alpha/omega trace boundaries: these artificial markers are excluded from activity and event counts. The origin was unavailable. No patient-level rows are included in the application bundle.',
      'prepared_at':datetime.now(timezone.utc).isoformat(),
      'limitations':['Not a dataset of installed medical apps','Not an EarlyWatch evaluation','Repeated events are not automatically unnecessary','No estimated clinical benefit or avoided delay']}

def research_reference(data):
    root=ET.fromstring(data)
    title=''.join(root.find('.//article-title').itertext())
    if 'Integrating a Machine Learning System Into Clinical Workflows' not in title:
        raise ValueError('The article identity does not match the reviewed Duke publication.')
    permission=' '.join(''.join(x.itertext()) for x in root.findall('.//permissions'))
    if 'creativecommons.org/licenses/by/' not in ET.tostring(root,encoding='unicode'):
        raise ValueError('Could not verify the expected open-access reuse notice.')
    paragraphs=[]
    for x in root.findall('.//abstract//p')+root.findall('.//body//p'):
        t=' '.join(''.join(x.itertext()).split())
        if 90<len(t)<2000 and any(w in t.lower() for w in ['workflow','communication','nurse','implementation','knowledge','roles']):
            paragraphs.append(t)
    return {'title':'Duke Sepsis Watch · published implementation study (2020)',
      'filename':'duke-sepsis-watch-excerpts.txt',
      'url':'https://www.jmir.org/2020/11/e22421/',
      'license':permission,
      'pages':['Attributed excerpts: Sandhu S et al. Integrating a Machine Learning System Into Clinical Workflows: Qualitative Study. JMIR 2020;22(11):e22421. DOI 10.2196/22421. Historical implementation research; not evidence validating the fictional EarlyWatch app. Excerpts are verbatim with XML citation markers retained.']+paragraphs[:12]}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--event-log',type=Path);args=parser.parse_args()
    data=args.event_log.read_bytes() if args.event_log else fetch(MIRROR)
    aggregate=summarize_xes(data)
    (ROOT/'data/hospital_benchmark.json').write_text(json.dumps(aggregate,indent=2))
    ref=research_reference(fetch(DUKE))
    (ROOT/'data/reference_sources.json').write_text(json.dumps([ref],indent=2))
    print(json.dumps({'cases':aggregate['cases'],'events':aggregate['events'],'activity_types':len(aggregate['activities']),'sha256':aggregate['sha256'],'research_title':ref['title']}))

if __name__=='__main__':main()

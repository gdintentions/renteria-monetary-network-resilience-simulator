"""Public authored scenarios driving the real Python cores, locally and in browsers.

No network adapters, model claims, uploaded documents, or independent labels.
"""
import asyncio
import json
from datetime import date
from tracelens import diagnose, sweep
from continuity_router import Router, Provider, ProviderFailure
from sourcegate import Evidence, run

TRACE_CORPUS = [
    {'id':'general-access','text':'Vendor access request access account access guide.'},
    {'id':'exception','text':'Access exception guide for an invented team.'},
    {'id':'vendor-policy','text':'Vendor production access requires a sponsor.'},
]

def trace_example(mode='selection-miss'):
    # A deliberately simple lexical count baseline makes the distractor rank first.
    query='vendor access'
    ranked=sorted(TRACE_CORPUS,key=lambda d:-sum(d['text'].lower().split().count(w) for w in query.split()))
    trace={'candidates':[{'id':d['id']} for d in ranked], 'kept_ids':[ranked[0]['id']],
           'judge_labels':{d['id']:('answers' if d['id']=='vendor-policy' else 'unrelated') for d in ranked},
           'gold_ids':['vendor-policy']}
    if mode=='candidate-miss':
        trace['candidates']=[c for c in trace['candidates'] if c['id']!='vendor-policy']
        del trace['judge_labels']['vendor-policy']
    elif mode=='unknown':
        trace['judge_labels']['vendor-policy']='partial';trace.pop('gold_ids')
    elif mode=='judge-disagreement':
        trace['kept_ids']=['general-access'];trace['judge_labels']['general-access']='answers'
    elif mode=='corpus-gap':
        trace['gold_ids']=[];trace['judge_labels']={c['id']:'unrelated' for c in trace['candidates']}
    elif mode=='judge-unavailable':trace['judge_labels'].pop('vendor-policy')
    elif mode!='selection-miss':raise ValueError('unknown trace scenario')
    return trace

async def route_example(mode, classification, budget):
    calls=[]
    async def primary(q):
        calls.append('primary')
        if mode=='deadline':await asyncio.sleep(.2)
        if mode=='failover' or (mode=='recovery' and calls.count('primary')==1):raise ProviderFailure(503,0)
        if mode=='auth-failure':raise ProviderFailure(401)
        return 'Synthetic primary response.'
    async def backup(q):
        calls.append('backup');return 'Synthetic backup response.'
    if mode not in {'healthy','failover','deadline','auth-failure','recovery'}:raise ValueError('unknown router scenario')
    r=Router([Provider('primary',primary,frozenset({'public','internal'})),Provider('backup',backup)],
             retries=0,timeout=.1,cooldown=.03,threshold=1)
    outputs=[await r.route('Invented support question',classification=classification,budget=budget)]
    if mode in {'failover','recovery'}:
        outputs.append(await r.route('Invented follow-up',classification=classification,budget=budget))
    if mode=='recovery':
        await asyncio.sleep(.05)
        outputs.append(await r.route('Invented recovery probe',classification=classification,budget=budget))
    return {'requests':outputs,'provider_calls':calls,
            'baseline':'An unguarded primary-only call would fail on the injected outage; no external reliability measured.'}

def source_example(mode, web_allowed):
    kb=Evidence('kb-access','Fictional vendor access requires a sponsor.','https://policy.example/access','2099-01-01',{'approver':'sponsor'})
    web=Evidence('web-duration','Fictional access expires after 14 days.','https://policy.example/duration','2099-01-01',{'duration':14},'web')
    if mode=='conflict':web=Evidence('web-conflict','Fictional access requires IT; expires after 14 days.',web.source,web.expires,{'duration':14,'approver':'IT'},'web')
    elif mode=='untrusted':web=Evidence(web.id,web.text,'https://policy.example.evil.test/rule',web.expires,web.claims,'web')
    elif mode=='expired':web=Evidence(web.id,web.text,web.source,'2020-01-01',web.claims,'web')
    elif mode=='bad-metadata':web=Evidence(web.id,web.text,web.source,web.expires,{'duration':float('nan')},'web')
    elif mode not in {'complete','bad-grade'}:raise ValueError('unknown evidence scenario')
    calls=[]
    def search(q):calls.append('fixture-search');return [web]
    def grade(q,docs):return {} if mode=='bad-grade' else {d.id:'partial' for d in docs}
    result=run('Who approves access and for how long?', ['approver','duration'],lambda q:[kb],grade,search,
               allowed_hosts={'policy.example'},today=date(2026,10,10),web_allowed=web_allowed)
    return {'result':result,'search_calls':calls,'evaluation_date':'2026-10-10',
            'baseline':'Local-only evidence cannot cover duration; blindly concatenating sources would retain the conflict/untrusted/expired fixtures.'}

async def execute(payload):
    if not isinstance(payload,dict):raise ValueError('request must be an object')
    project=payload.get('project');mode=payload.get('scenario')
    if project=='tracelens':
        trace=payload.get('trace')
        if trace is None:trace=trace_example(mode)
        result={'input_trace':trace,'diagnosis':diagnose(trace),'replay':sweep(trace,[1,2,3]),
                'baseline':'Top-1 lexical retrieval vs top-k replay; supplied synthetic labels, not measured answer accuracy.'}
    elif project=='continuity-router':result=await route_example(mode,payload.get('classification','public'),payload.get('budget',.08))
    elif project=='sourcegate':result=source_example(mode,payload.get('web_allowed',False))
    else:raise ValueError('unknown project')
    return {'project':project,'synthetic':True,'engine':'repository Python core','result':result}

async def execute_json(raw):
    if not isinstance(raw,str) or len(raw)>32768:raise ValueError('request limit is 32768 characters')
    def invalid_constant(value):raise ValueError('non-finite JSON value')
    return json.dumps(await execute(json.loads(raw,parse_constant=invalid_constant)),allow_nan=False)

"""Publish actual outputs of authored success/failure scenarios, with source hashes."""
import asyncio
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reliability_lab'))
for folder in ('tracelens','continuity-router','sourcegate'):sys.path.insert(0,str(ROOT/'portfolio_projects'/f'renteria-{folder}'))
from scenarios import execute
async def main():
    cases=[]
    for mode in ('selection-miss','candidate-miss','unknown','judge-disagreement','corpus-gap','judge-unavailable'):
        cases.append({'project':'tracelens','scenario':mode})
    for mode in ('healthy','failover','deadline','auth-failure','recovery'):
        cases.append({'project':'continuity-router','scenario':mode,'classification':'public','budget':.08})
    cases.append({'project':'continuity-router','scenario':'failover','classification':'restricted','budget':.08})
    for mode in ('complete','conflict','untrusted','expired','bad-grade','bad-metadata'):
        cases.append({'project':'sourcegate','scenario':mode,'web_allowed':True})
    cases.append({'project':'sourcegate','scenario':'complete','web_allowed':False})
    output={'scope':'19 authored synthetic scenarios; NOT an independent benchmark','cases':[]}
    for case in cases:output['cases'].append({'input':case,'observed':await execute(case)})
    out=ROOT/'artifacts/reliability/scenario_outputs.json';out.write_text(json.dumps(output,indent=2)+'\n')
    print(f'Published {len(cases)} observed scenario outputs.')
asyncio.run(main())

"""Synthetic adapter-to-core end-to-end acceptance checks, not independent labels."""
import asyncio
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reliability_lab'))
for folder in ('tracelens','continuity-router','sourcegate'):sys.path.insert(0,str(ROOT/'portfolio_projects'/f'renteria-{folder}'))
from scenarios import execute

class EndToEnd(unittest.IsolatedAsyncioTestCase):
    async def test_trace_ranking_selection_replay(self):
        out=(await execute({'project':'tracelens','scenario':'selection-miss'}))['result']
        self.assertEqual(out['diagnosis']['status'],'SELECTION_MISS')
        self.assertEqual(out['diagnosis']['gold_metrics']['selected_recall'],0)
        self.assertEqual(out['replay'][-1]['diagnosis']['gold_metrics']['selected_recall'],1)
    async def test_trace_unknown_and_disagreement(self):
        for scenario,status in [('unknown','INSUFFICIENT_EVIDENCE'),('judge-disagreement','JUDGE_DISAGREEMENT'),('judge-unavailable','JUDGE_UNAVAILABLE'),('candidate-miss','CANDIDATE_MISS'),('corpus-gap','CORPUS_GAP_CONFIRMED')]:
            with self.subTest(scenario=scenario):
                out=await execute({'project':'tracelens','scenario':scenario})
                self.assertEqual(out['result']['diagnosis']['status'],status)
    async def test_router_recovery_sequence(self):
        r=(await execute({'project':'continuity-router','scenario':'recovery'}))['result']
        self.assertEqual([q['provider'] for q in r['requests']],['backup','backup','primary'])
        self.assertEqual(r['requests'][1]['events'][0]['event'],'CIRCUIT_SKIP')
    async def test_router_authorization_blocks_every_call(self):
        r=(await execute({'project':'continuity-router','scenario':'failover','classification':'restricted'}))['result']
        self.assertEqual(r['provider_calls'],[])
        self.assertTrue(all(q['status']=='NEEDS_REVIEW' for q in r['requests']))
    async def test_router_deadline_withholds(self):
        r=(await execute({'project':'continuity-router','scenario':'deadline','budget':.01}))['result']
        self.assertEqual(r['requests'][0]['status'],'NEEDS_REVIEW')
        self.assertIsNone(r['requests'][0]['text'])
        self.assertLess(r['requests'][0]['elapsed_s'],.3)
    async def test_source_permission_and_citations(self):
        off=(await execute({'project':'sourcegate','scenario':'complete'}))['result']
        self.assertEqual(off['search_calls'],[]);self.assertIsNone(off['result']['answer'])
        on=(await execute({'project':'sourcegate','scenario':'complete','web_allowed':True}))['result']
        self.assertEqual(on['search_calls'],['fixture-search'])
        self.assertEqual([a['citation'] for a in on['result']['answer']],['kb-access','web-duration'])
    async def test_source_negative_cases_withhold(self):
        for mode,reason in [('conflict','CONFLICT'),('untrusted','MISSING_EVIDENCE'),('expired','MISSING_EVIDENCE'),('bad-grade','ADAPTER_OR_SCHEMA_FAILURE'),('bad-metadata','ADAPTER_OR_SCHEMA_FAILURE')]:
            with self.subTest(mode=mode):
                r=(await execute({'project':'sourcegate','scenario':mode,'web_allowed':True}))['result']['result']
                self.assertEqual(r['reason'],reason);self.assertIsNone(r['answer'])
    async def test_trace_malformed_input_withholds(self):
        with self.assertRaises(ValueError):await execute({'project':'tracelens','trace':{'candidates':[{}]}})
    async def test_unknown_project_rejected(self):
        with self.assertRaises(ValueError):await execute({'project':'nope'})

if __name__=='__main__':unittest.main()

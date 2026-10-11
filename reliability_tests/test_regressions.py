"""Boundary regressions discovered during the October 11 portfolio review."""
import asyncio
import importlib.util
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
for name, folder in [('tracelens','tracelens'),('continuity_router','continuity-router'),('sourcegate','sourcegate')]:
    spec=importlib.util.spec_from_file_location(name,ROOT/'portfolio_projects'/f'renteria-{folder}'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
from tracelens import diagnose
from continuity_router import Router,Provider
from sourcegate import Evidence,run

class BoundaryRegressions(unittest.TestCase):
    def test_trace_malformed_candidate_is_validation_error(self):
        with self.assertRaises(ValueError):
            diagnose({'candidates':[{}], 'kept_ids':[], 'judge_labels':{}})
    def test_trace_gold_disagreement_not_supported(self):
        result=diagnose({'candidates':[{'id':'a'}], 'kept_ids':['a'], 'judge_labels':{'a':'answers'}, 'gold_ids':[]})
        self.assertEqual(result['status'],'JUDGE_DISAGREEMENT')
    def test_router_nonfinite_timeout_rejected(self):
        async def up(q):return 'ok'
        with self.assertRaises(ValueError):Router([Provider('up',up)],timeout=float('nan'))
    def test_router_fractional_retries_rejected(self):
        async def up(q):return 'ok'
        with self.assertRaises(ValueError):Router([Provider('up',up)],retries=1.5)
    def test_sourcegate_bad_claims_fail_closed(self):
        doc=Evidence('a','fixture','https://policy.example/a','2099-01-01',None)
        result=run('q',['a'],lambda q:[doc],lambda q,ds:{'a':'relevant'},lambda q:[],allowed_hosts={'policy.example'})
        self.assertEqual(result['status'],'NEEDS_REVIEW')
        self.assertEqual(result['reason'],'ADAPTER_OR_SCHEMA_FAILURE')
    def test_sourcegate_nonfinite_claims_fail_closed(self):
        doc=Evidence('a','fixture','https://policy.example/a','2099-01-01',{'a':float('nan')})
        result=run('q',['a'],lambda q:[doc],lambda q,ds:{'a':'relevant'},lambda q:[],allowed_hosts={'policy.example'})
        self.assertEqual(result['status'],'NEEDS_REVIEW')

if __name__=='__main__':unittest.main()

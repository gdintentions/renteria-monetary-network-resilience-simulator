import unittest
from datetime import date
from sourcegate import Evidence,run,demo
class Tests(unittest.TestCase):
 def test_complete(self):self.assertEqual(demo()["status"],"CITED_EXTRACTS")
 def test_conflict(self):self.assertEqual(demo("conflict")["reason"],"CONFLICT")
 def test_untrusted(self):self.assertEqual(demo("untrusted")["reason"],"MISSING_EVIDENCE")
 def test_offline(self):self.assertNotIn("WEB_FALLBACK",demo("offline")["events"])
 def doc(self,**kw):
  args=dict(id="a",text="Invented policy.",source="https://policy.example/a",expires="2099-01-01",claims={"a":1});args.update(kw);return Evidence(**args)
 def call(self,docs,grade=None,web=False):
  def forbidden(q):raise AssertionError("unexpected web call")
  return run("q",["a"],lambda q:docs,grade or (lambda q,ds:{d.id:"relevant" for d in ds}),forbidden,allowed_hosts={"policy.example"},today=date(2026,10,10),web_allowed=web)
 def test_expired(self):self.assertEqual(self.call([self.doc(expires="2020-01-01")])["status"],"NEEDS_REVIEW")
 def test_host_suffix_spoof(self):self.assertEqual(self.call([self.doc(source="https://policy.example.evil.test/a")])["status"],"NEEDS_REVIEW")
 def test_missing_grade(self):self.assertEqual(self.call([self.doc()],lambda q,ds:{})["reason"],"ADAPTER_OR_SCHEMA_FAILURE")
 def test_duplicate_id(self):self.assertEqual(self.call([self.doc(),self.doc()])["status"],"NEEDS_REVIEW")
 def test_exact_citation(self):self.assertEqual(self.call([self.doc()])["answer"][0]["citation"],"a")
 def test_unknown_claim_not_inferred(self):self.assertEqual(self.call([self.doc(claims={"b":1})])["status"],"NEEDS_REVIEW")
if __name__=="__main__":unittest.main()

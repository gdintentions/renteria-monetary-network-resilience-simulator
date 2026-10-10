import asyncio
import unittest
from continuity_router import Router,Provider,ProviderFailure,Breaker
class Tests(unittest.IsolatedAsyncioTestCase):
 async def test_failover_and_open(self):
  calls=[]
  async def down(q):calls.append(q);raise ProviderFailure(503,0)
  async def up(q):return "ok"
  r=Router([Provider("down",down),Provider("up",up)],threshold=1)
  self.assertEqual((await r.route("fixture"))["provider"],"up")
  self.assertEqual((await r.route("fixture"))["events"][0]["event"],"CIRCUIT_SKIP")
  self.assertEqual(len(calls),2)
 async def test_no_retry_auth(self):
  calls=[]
  async def bad(q):calls.append(q);raise ProviderFailure(401)
  result=await Router([Provider("bad",bad)],retries=4).route("q")
  self.assertEqual(len(calls),1);self.assertIsNone(result["text"])
 async def test_policy_never_calls(self):
  async def forbidden(q):raise AssertionError("private prompt leaked")
  out=await Router([Provider("cloud",forbidden)]).route("secret",classification="restricted")
  self.assertEqual(out["events"][0]["event"],"POLICY_SKIP")
  self.assertNotIn("secret",str(out))
 async def test_total_deadline(self):
  async def slow(q):await asyncio.sleep(10);return "late"
  out=await Router([Provider("slow",slow)],timeout=10).route("q",budget=.02)
  self.assertEqual(out["status"],"NEEDS_REVIEW");self.assertLess(out["elapsed_s"],.5)
 async def test_long_retry_after_fails_over(self):
  async def down(q):raise ProviderFailure(429,999)
  async def up(q):return "ok"
  out=await Router([Provider("down",down),Provider("up",up)]).route("q",budget=.2)
  self.assertEqual(out["provider"],"up")
 async def test_programming_error_visible(self):
  async def bug(q):raise TypeError("bug")
  with self.assertRaises(TypeError):await Router([Provider("bug",bug)]).route("q")
 async def test_cancel_propagates(self):
  async def cancel(q):raise asyncio.CancelledError()
  with self.assertRaises(asyncio.CancelledError):await Router([Provider("cancel",cancel)]).route("q")
 async def test_empty_output(self):
  async def empty(q):return " "
  self.assertEqual((await Router([Provider("empty",empty)]).route("q"))["status"],"NEEDS_REVIEW")
 def test_single_recovery_probe(self):
  b=Breaker();b.finish(False,0,1)
  self.assertFalse(b.acquire(1,2));self.assertTrue(b.acquire(3,2));self.assertFalse(b.acquire(3,2))
  b.finish(True,4,1);self.assertTrue(b.acquire(4,2))
if __name__=="__main__":unittest.main()

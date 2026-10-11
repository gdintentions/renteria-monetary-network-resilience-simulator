"""Async provider routing with explicit authorization and a total time budget."""
import asyncio
import json
import random
import math
import time
from dataclasses import dataclass, field
from typing import Callable, Awaitable

class ProviderFailure(Exception):
    def __init__(self, code, retry_after=None):
        super().__init__(str(code))
        self.code=code
        self.retry_after=retry_after
    @property
    def retryable(self): return self.code in {408,429,500,502,503,504,"timeout","network"}

@dataclass
class Provider:
    name: str
    complete: Callable[[str], Awaitable[str]]
    classifications: frozenset = frozenset({"public"})

@dataclass
class Breaker:
    failures: int = 0
    opened: float | None = None
    probing: bool = False
    def acquire(self, now, cooldown):
        if self.opened is None: return True
        if now-self.opened < cooldown or self.probing: return False
        self.probing=True
        return True
    def finish(self, ok, now, threshold):
        probe=self.probing
        self.probing=False
        if ok:
            self.failures=0;self.opened=None
        else:
            self.failures+=1
            if probe or self.failures>=threshold:self.opened=now

class Router:
    def __init__(self, providers, *, retries=1, timeout=2.0, cooldown=30.0, threshold=2, seed=7):
        if not providers or len(providers)>16 or any(not isinstance(p, Provider) or not isinstance(p.name,str) or not p.name or len(p.name)>100 or not callable(p.complete) for p in providers):
            raise ValueError("1 to 16 named callable providers required")
        if len({p.name for p in providers})!=len(providers):raise ValueError("unique providers required")
        if any(not isinstance(p.classifications, (set,frozenset)) or not p.classifications <= {"public","internal","restricted"} for p in providers):
            raise ValueError("invalid provider classifications")
        if type(retries) is not int or not 0<=retries<=5 or type(threshold) is not int or threshold<1:
            raise ValueError("integer retry/threshold limits required")
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (timeout,cooldown)) or not 0<timeout<=60 or not 0<=cooldown<=3600:
            raise ValueError("finite bounded time limits required")
        self.providers=providers;self.retries=retries;self.timeout=timeout
        self.cooldown=cooldown;self.threshold=threshold;self.rng=random.Random(seed)
        self.breakers={p.name:Breaker() for p in providers}
    async def route(self, prompt, *, classification="public", budget=5.0):
        if classification not in {"public","internal","restricted"}:raise ValueError("unknown classification")
        if type(budget) not in (int,float) or not math.isfinite(budget) or not 0<budget<=60:raise ValueError("finite budget in (0,60] required")
        if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>2000:raise ValueError("prompt must contain 1 to 2000 characters")
        start=time.monotonic();deadline=start+budget;events=[]
        for provider in self.providers:
            if classification not in provider.classifications:
                events.append({"provider":provider.name,"event":"POLICY_SKIP"});continue
            if time.monotonic()>=deadline:break
            breaker=self.breakers[provider.name]
            if not breaker.acquire(time.monotonic(),self.cooldown):
                events.append({"provider":provider.name,"event":"CIRCUIT_SKIP"});continue
            try:
                for attempt in range(self.retries+1):
                    remaining=deadline-time.monotonic()
                    if remaining<=0:break
                    try:
                        text=await asyncio.wait_for(provider.complete(prompt), min(self.timeout,remaining))
                        if not isinstance(text,str) or not text.strip():raise ProviderFailure("invalid_output")
                        breaker.finish(True,time.monotonic(),self.threshold)
                        events.append({"provider":provider.name,"event":"SUCCESS","attempt":attempt+1})
                        return {"status":"ANSWERED","provider":provider.name,"text":text,
                                "events":events,"elapsed_s":time.monotonic()-start}
                    except (asyncio.TimeoutError,ProviderFailure) as exc:
                        err=exc if isinstance(exc,ProviderFailure) else ProviderFailure("timeout")
                        events.append({"provider":provider.name,"event":"FAILURE","code":err.code,"attempt":attempt+1})
                        if not err.retryable or attempt==self.retries:break
                        delay=err.retry_after if err.retry_after is not None else self.rng.uniform(0,min(1,0.05*2**attempt))
                        if not isinstance(delay,(int,float)) or not 0<=delay<deadline-time.monotonic():break
                        await asyncio.sleep(delay)
                breaker.finish(False,time.monotonic(),self.threshold)
            except asyncio.CancelledError:
                breaker.probing=False
                raise
            except Exception:
                # Programming failures must not be disguised as provider outages.
                breaker.probing=False
                raise
        return {"status":"NEEDS_REVIEW","provider":None,"text":None,"events":events,
                "elapsed_s":time.monotonic()-start}

async def demo():
    async def down(_):raise ProviderFailure(503,0)
    async def backup(_):return "Synthetic support response; no live model called."
    router=Router([Provider("primary",down),Provider("backup",backup)], threshold=1)
    return [await router.route("Invented support request"),await router.route("Invented request"),
            await router.route("Private fixture",classification="restricted")]
if __name__=="__main__":print(json.dumps(asyncio.run(demo()),indent=2))

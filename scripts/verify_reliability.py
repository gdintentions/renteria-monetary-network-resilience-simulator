"""Run each project suite plus cross-project boundary and end-to-end checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/reliability';OUT.mkdir(parents=True,exist_ok=True)
suites=['portfolio_projects/renteria-tracelens','portfolio_projects/renteria-continuity-router','portfolio_projects/renteria-sourcegate','reliability_tests']
results=[]
for path in suites:
    proc=subprocess.run([sys.executable,'-m','unittest','discover','-s',path,'-v'],cwd=ROOT,text=True,capture_output=True)
    name=Path(path).name;log=OUT/(name+'.txt');log.write_text(proc.stdout+proc.stderr)
    results.append({'suite':path,'exit_code':proc.returncode,'log':str(log.relative_to(ROOT))})
    print(name+(': PASS' if proc.returncode==0 else ': FAIL'))
sources={}
for path in sorted([*ROOT.glob('portfolio_projects/renteria-tracelens/*.py'),*ROOT.glob('portfolio_projects/renteria-continuity-router/*.py'),*ROOT.glob('portfolio_projects/renteria-sourcegate/*.py'),*ROOT.glob('reliability_lab/*.py'),*ROOT.glob('reliability_tests/*.py')]):
    sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
report={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'scope':'Authored synthetic contract, boundary and adapter-to-core scenarios; not independent domain validation','suites':results,'source_sha256':sources}
(OUT/'python_results.json').write_text(json.dumps(report,indent=2)+'\n')
raise SystemExit(any(r['exit_code'] for r in results))

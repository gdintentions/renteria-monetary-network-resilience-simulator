"""Bundle pinned Pyodide and exact project sources for same-origin static hosting."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,default=ROOT/'reliability_lab/node_modules/pyodide');args=p.parse_args()
if json.loads((args.runtime/'package.json').read_text())['version']!='0.27.7':raise SystemExit('Pyodide 0.27.7 required')
out=ROOT/'hosted_demo/reliability';vendor=out/'runtime';vendor.mkdir(parents=True,exist_ok=True)
for name in ('pyodide.js','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json'):
    shutil.copy2(args.runtime/name,vendor/name)
sources={}
for name,folder in [('tracelens','tracelens'),('continuity_router','continuity-router'),('sourcegate','sourcegate')]:
    path=ROOT/'portfolio_projects'/f'renteria-{folder}'/f'{name}.py';sources[f'{name}.py']=path
sources['scenarios.py']=ROOT/'reliability_lab/scenarios.py'
manifest={'runtime':'Pyodide 0.27.7','scope':'actual Python cores; authored synthetic adapters','sources':{}}
for name,path in sources.items():
    content=path.read_bytes();(out/name).write_bytes(content)
    manifest['sources'][name]={'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(content).hexdigest()}
(out/'source-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built actual Python browser runtime and four source files.')

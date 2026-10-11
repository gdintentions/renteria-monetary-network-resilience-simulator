/* Exact Python cores loaded from the same origin; no user code is evaluated. */
let python, manifest;
const ready=(async()=>{
  importScripts('runtime/pyodide.js');
  python=await loadPyodide({indexURL:new URL('runtime/',self.location.href).href});
  const response=await fetch('source-manifest.json');
  if(!response.ok)throw Error('Source manifest unavailable');
  manifest=await response.json();
  for(const [name,entry] of Object.entries(manifest.sources)){
    const file=await fetch(name);if(!file.ok)throw Error('Source unavailable: '+name);
    const bytes=await file.arrayBuffer();
    const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
    if(digest!==entry.sha256)throw Error('Source integrity mismatch: '+name);
    python.FS.writeFile('/home/pyodide/'+name,new Uint8Array(bytes));
  }
  await python.runPythonAsync('from scenarios import execute_json');
  self.postMessage({type:'ready',manifest});
})().catch(error=>{self.postMessage({type:'boot-error',message:error.message});throw error;});
self.onmessage=async({data})=>{
  try{
    await ready;
    python.globals.set('_request_json',JSON.stringify(data.payload));
    const raw=await python.runPythonAsync('await execute_json(_request_json)');
    self.postMessage({type:'result',id:data.id,result:JSON.parse(raw)});
  }catch(error){self.postMessage({type:'error',id:data.id,message:String(error.message).split('\n').filter(Boolean).slice(-1)[0]});}
};

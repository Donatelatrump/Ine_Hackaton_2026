(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.Decision=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 function planScenario(items,capacity,reach,response){
  if(![capacity,reach,response].every(Number.isFinite)||!Number.isInteger(capacity)||capacity<0||reach<0||response<0||response>100)throw new Error('Parámetros fuera de rango');
  const selected=items.filter(r=>Number.isFinite(r.risk)&&r.risk>=0&&r.risk<=100&&Number.isFinite(r.ln)&&r.ln>0)
   .slice().sort((a,b)=>b.risk-a.risk||a.key.localeCompare(b.key)).slice(0,capacity).map(r=>{
    const served=Math.min(reach,r.ln),additional=served*r.risk/100*response/100;
    return {...r,served,additional,after:Math.max(0,r.risk-100*additional/r.ln)};
   });
  const population=selected.reduce((s,r)=>s+r.ln,0),additional=selected.reduce((s,r)=>s+r.additional,0);
  const before=population?selected.reduce((s,r)=>s+r.risk*r.ln,0)/population:0;
  return {selected,served:selected.reduce((s,r)=>s+r.served,0),additional,reference_population:population,before,after:population?Math.max(0,before-100*additional/population):0};
 }
 return {planScenario};
});

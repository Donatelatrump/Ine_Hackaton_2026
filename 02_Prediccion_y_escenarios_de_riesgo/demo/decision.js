(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.Decision=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const variants=['persistencia_5','ridge_5','persistencia_10','ridge_10','persistencia_20','ridge_20'];
 function valid(r){return Number.isFinite(r.risk)&&r.risk>=0&&r.risk<=100&&Number.isFinite(r.observed)&&r.observed>0;}
 function score(r,lens){if(lens==='volumen')return r.risk*r.observed/100;if(lens==='deterioro')return Number.isFinite(r.baseline)?r.risk-r.baseline:-Infinity;return r.risk;}
 function rank(items,lens='tasa'){if(!['tasa','volumen','deterioro'].includes(lens))throw Error('Criterio fuera de rango');return items.filter(valid).slice().sort((a,b)=>score(b,lens)-score(a,lens)||a.key.localeCompare(b.key));}
 function params(capacity,reach,response){
  if(![capacity,reach,response].every(Number.isFinite)||!Number.isInteger(capacity)||capacity<0||reach<0||response<0||response>100)throw new Error('Parámetros fuera de rango');
 }
 function item(r,served,response){const additional=served*r.risk/100*response/100;return {...r,served,additional,after:Math.max(0,r.risk-100*additional/r.observed)};}
 function summarize(selected){
  const population=selected.reduce((s,r)=>s+r.observed,0),additional=selected.reduce((s,r)=>s+r.additional,0);
  const before=population?selected.reduce((s,r)=>s+r.risk*r.observed,0)/population:0;
  return {selected,served:selected.reduce((s,r)=>s+r.served,0),additional,reference_population:population,before,after:population?Math.max(0,before-100*additional/population):0};
 }
 function planScenario(items,capacity,reach,response,lens='tasa'){
  params(capacity,reach,response);
  return summarize(rank(items,lens).slice(0,capacity).map(r=>item(r,Math.min(reach,r.observed),response)));
 }
 function planByBudget(items,budget,reach,response,lens='tasa'){
  params(0,reach,response);
  if(!Number.isFinite(budget)||budget<0)throw new Error('Parámetros fuera de rango');
  const selected=[];let used=0;
  for(const r of rank(items,lens)){
   const remaining=budget-used;if(remaining<=0)break;
   const served=Math.min(reach,r.observed,remaining);if(served<=0)break;
   selected.push(item(r,served,response));used+=served;
  }
  return summarize(selected);
 }
 function confidenceTier(count,total){
  if(!total||count===null||count===undefined)return {tier:'sin_datos',label:'Sin datos',frequency:null,count:count||0,total:total||0};
  const f=count/total,tier=f>=5/6?'alta':f>=3/6?'media':'baja';
  return {tier,label:tier[0].toUpperCase()+tier.slice(1),frequency:f,count,total};
 }
 function selectionStability(items,capacity,lens){
  const result=Object.fromEntries(items.map(r=>[r.key,{count:0,eligible:0,frequency:0,robust:false,members:{}}]));
  for(const variant of variants){
   const limit=variant.split('_')[1];
   const rows=items.map(r=>({...r,risk:r.variants?.[variant],baseline:r.variants?.['persistencia_'+limit]}));
   for(const r of rows)if(valid(r))result[r.key].eligible++;
   for(const r of rank(rows,lens).slice(0,capacity)){result[r.key].count++;result[r.key].members[variant]=true;}
  }
  for(const v of Object.values(result)){v.frequency=v.count/variants.length;v.robust=v.count===variants.length;v.confidence=confidenceTier(v.count,variants.length);}
  return result;
 }
 function decisionFrontier(items,capacity,lens,precomputed){
  const estabilidad=precomputed||selectionStability(items,capacity,lens);
  const nucleo=[],frontera=[],fuera=[];
  for(const r of items){const s=estabilidad[r.key];if(!s)continue;
   if(s.count>=variants.length)nucleo.push(r.key);else if(s.count>0)frontera.push(r.key);else fuera.push(r.key);}
  return {nucleo,frontera,fuera,estabilidad};
 }
 function level(rate,thresholds){return !Number.isFinite(rate)?'sin_datos':rate>=thresholds.high?'alto':rate<thresholds.low?'bajo':'medio';}
 function inverseScenario(r,reach,response,thresholds){
  if(!valid(r))return {reason:'Sin estimación válida',required_reach:null,required_response:null};
  const current=level(r.risk,thresholds);
  if(current==='bajo')return {reason:'Ya está en nivel bajo',required_reach:0,required_response:0,feasible_reach:true,feasible_response:true};
  const target=Math.max(0,(current==='alto'?thresholds.high:thresholds.low)-1e-6),need=r.observed*(r.risk-target)/100;
  const required_reach=response>0&&r.risk>0?Math.ceil(need/(r.risk/100*response/100)):null;
  const capped=Math.min(reach,r.observed),required_response=capped>0&&r.risk>0?100*need/(capped*r.risk/100):null;
  return {target,additional_required:need,required_reach,required_response,feasible_reach:required_reach!==null&&required_reach<=r.observed,feasible_response:required_response!==null&&required_response<=100};
 }
 function overlap(a,b){const second=new Set(b.map(r=>r.key));return a.filter(r=>second.has(r.key)).length;}
 return {planScenario,planByBudget,rank,selectionStability,decisionFrontier,confidenceTier,inverseScenario,level,overlap,variants};
});

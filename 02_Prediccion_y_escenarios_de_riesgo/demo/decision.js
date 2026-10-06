(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.Decision=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 const variants=['persistencia_5','ridge_5','persistencia_10','ridge_10','persistencia_20','ridge_20'];
 const interventions=Object.freeze({
  ninguna:Object.freeze({id:'ninguna',label:'Sin intervención',effect_pp:0,estimand:'ninguno',unit:'Sin asignación de acción',source:null,limits:'Escenario base; conserva los municipios del plan.'}),
  sms_suecia:Object.freeze({id:'sms_suecia',label:'Recordatorio SMS · estudio de Suecia',effect_pp:0.30,low_pp:0.13,high_pp:0.48,estimand:'ITT',unit:'Personas asignadas al SMS',country:'Suecia',election:'Parlamento Europeo 2019',population:'Electores de 18–75 años con un único número móvil asociado; muestra inicial de 3,161,654 personas.',citation:'Lindgren, Nyman y Oskarsson (2025). Examining Voting Spillover Effects of Text Message Reminders. British Journal of Political Science. DOI: 10.1017/S0007123424000504.',source:'https://doi.org/10.1017/S0007123424000504',locator:'Resultados, figura 1',uncertainty:'Intervalo publicado: 0.13–0.48 pp.',limits:'Efecto directo de asignación, sobre voto registrado. No sumar efectos en convivientes. No equivale a WhatsApp ni demuestra efecto en México.'}),
  sms_eeuu:Object.freeze({id:'sms_eeuu',label:'Campaña SMS · estudio de Estados Unidos',effect_pp:0.25,low_pp:0.17,high_pp:0.34,estimand:'ITT',unit:'Personas asignadas a la campaña SMS',country:'Estados Unidos',election:'Intermedias 2018',population:'7.1 millones de electores; campaña orientada a mujeres menores de 30 años y electores de color.',citation:'Haenschen, Mann y DeMora (2026). The Effects of SMS Mobilization, Message, and Timing on Voter Turnout. Political Behavior. DOI: 10.1007/s11109-026-10121-2.',source:'https://doi.org/10.1007/s11109-026-10121-2',locator:'Introducción: efecto global e IC 95%',uncertainty:'IC 95% publicado convertido a pp: 0.17–0.34.',limits:'Promedio de una campaña concreta, sobre voto registrado. No es el efecto de cualquier texto ni de toda población. Transferencia a México no validada.'}),
  plan_voto:Object.freeze({id:'plan_voto',label:'Llamada para elaborar un plan de votación',effect_pp:4.1,estimand:'ATT',unit:'Personas efectivamente contactadas',country:'Estados Unidos',election:'Presidencial 2008, Pensilvania',population:'Electores de baja propensión a votar en registro demócrata; experimento de 287,228 personas.',citation:'Nickerson y Rogers (2010). Do You Have a Voting Plan? Psychological Science, 21(2), 194–199. DOI: 10.1177/0956797609359326.',source:'https://doi.org/10.1177/0956797609359326',fulltext:'https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/nickerson20and20rogers_FINAL.pdf',locator:'Tabla 1, implementation intentions, ATT',uncertainty:'Error estándar publicado: 1.7 pp; no se incorpora un intervalo calculado como si fuera publicado.',limits:'Efecto ajustado por contacto, sobre voto registrado. El ITT publicado es 0.9 pp. No aplicar 4.1 pp a intentos de llamada ni a talleres; fuerte variación por hogar. Transferencia a México no validada.'}),
  personalizada:Object.freeze({id:'personalizada',label:'Acción personalizada · solo supuesto',estimand:'supuesto',unit:'Personas alcanzadas (supuesto)',source:null,limits:'Sin coeficiente causal respaldado. Respuesta elegida por el usuario; no atribuirla a talleres, infografías ni a las tesis.'})
 });
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
 function proportionalCoverage(items,budget,lens){
  if(!Number.isInteger(budget)||budget<0)throw Error('Cobertura fuera de rango');
  const ranked=rank(items,lens),population=ranked.reduce((s,r)=>s+Math.floor(r.observed),0),total=Math.min(budget,population);
  if(!population||!total)return [];
  const shares=ranked.map(r=>{const exact=total*Math.floor(r.observed)/population;return {...r,served:Math.floor(exact),remainder:exact-Math.floor(exact)};});
  let remaining=total-shares.reduce((s,r)=>s+r.served,0);
  const remainderOrder=shares.slice().sort((a,b)=>b.remainder-a.remainder||a.key.localeCompare(b.key));
  for(const r of remainderOrder){if(!remaining)break;if(r.served<Math.floor(r.observed)){r.served++;remaining--;}}
  return shares.filter(r=>r.served>0).map(({remainder,...r})=>r);
 }
 function planIntervention(items,{capacity=0,budget,reach,action='ninguna',response=0,lens='tasa',distribution='prioridad'}={}){
  const a=interventions[action];if(!a)throw Error('Acción fuera de rango');
  if(!['prioridad','proporcional'].includes(distribution))throw Error('Distribución fuera de rango');
  if(!Number.isInteger(reach))throw Error('Alcance fuera de rango');
  params(capacity,reach,0);
  const p=distribution==='proporcional'?{selected:proportionalCoverage(items,budget??reach,lens)}:budget===undefined?planScenario(items,capacity,reach,0,lens):planByBudget(items,budget,reach,0,lens);
  if(action==='personalizada')params(capacity,reach,response);
  const selected=p.selected.map(r=>{
   const served=action==='ninguna'?0:r.served;
   // Positive external effects cannot exceed expected abstainers in the reached population.
   const cap=served*r.risk/100;
   const amount=pp=>Math.min(cap,served*pp/100);
   const additional=action==='personalizada'?cap*response/100:amount(a.effect_pp);
   return {...r,served,additional,additional_low:Number.isFinite(a.low_pp)?amount(a.low_pp):null,additional_high:Number.isFinite(a.high_pp)?amount(a.high_pp):null,after:Math.max(0,r.risk-100*additional/r.observed)};
  });
  const result=summarize(selected),hasRange=Number.isFinite(a.low_pp);
  return {...result,action:a,distribution,response:action==='personalizada'?response:null,additional_low:hasRange?selected.reduce((s,r)=>s+r.additional_low,0):null,additional_high:hasRange?selected.reduce((s,r)=>s+r.additional_high,0):null};
 }
 function confidenceTier(count,total){
  if(!total||count===null||count===undefined)return {tier:'sin_datos',label:'Sin datos',frequency:null,count:count||0,total:total||0};
  const f=count/total,tier=f>=5/6?'alta':f>=3/6?'media':'baja';
  return {tier,label:tier[0].toUpperCase()+tier.slice(1),frequency:f,count,total};
 }
 function territorialScenario(items,plan){
  const eligible=items.filter(valid),population=eligible.reduce((s,r)=>s+r.observed,0);
  const keys=new Set(eligible.map(r=>r.key)),selected=plan.selected.filter(r=>keys.has(r.key));
  const additional=selected.reduce((s,r)=>s+r.additional,0),before=population?eligible.reduce((s,r)=>s+r.risk*r.observed,0)/population:0;
  return {population,before,after:population?before-100*additional/population:0,additional,municipalities:eligible.length,selected:selected.length};
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
 return {planScenario,planByBudget,planIntervention,territorialScenario,interventions,rank,selectionStability,decisionFrontier,confidenceTier,inverseScenario,level,overlap,variants};
});

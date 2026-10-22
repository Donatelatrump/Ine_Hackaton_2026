/* State action assumptions, traceable allocation, portable briefs and presentation. */
(() => {
  'use strict';
  const A=UmbralAnalytics,settings=new Map();
  const f=n=>Number.isFinite(n)?fmt.format(n):'Sin dato';
  const p=n=>Number.isFinite(n)?n.toFixed(2)+'%':'Sin dato';
  const pp=n=>Number.isFinite(n)?n.toLocaleString('es-MX',{maximumFractionDigits:5})+' pp':'Sin dato';
  let context=null,snapshot=null,formKey='',page=0,allocationKey='',diagnostic=null,exportText='';
  const criterion={tasa:'Mayor porcentaje de abstención',volumen:'Mayor volumen de abstención',deterioro:'Mayor deterioro frente a 2021'};
  const normalized=text=>String(text).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const validRow=r=>Number.isFinite(r.risk)&&r.observed>0;
  function weighted(rows,field){
    const data=rows.filter(r=>r.observed>0&&Number.isFinite(r.profile?.[field]));
    const base=data.reduce((sum,r)=>sum+r.observed,0);
    return base?data.reduce((sum,r)=>sum+r.profile[field]*r.observed,0)/base:null;
  }
  function actionTexts(){
    return [...document.querySelectorAll('.d7-action-list li')].map(li=>{
      if(!li.dataset.actionText){const clone=li.cloneNode(true);clone.querySelectorAll('.d7-action-number,.d7-action-rationale').forEach(n=>n.remove());li.dataset.actionText=clone.textContent.trim();}
      return li.dataset.actionText;
    });
  }
  function stateSettings(rows,selection,base){
    const texts=actionTexts();
    let state=settings.get(selection.state);
    if(!state){
      // Whole documented plan, one shared population: never sum overlapping activities.
      state={selected:0,actions:[{text:'Plan estatal de '+(rows[0]?.state_name||selection.state),activities:texts,group:'Base estatal observable',groupKnown:true,coverage:10,scenario:'central',reach:Math.floor(base*.10),effect:1.5,low:.3,high:3,distribution:'proporcional',lens:'tasa',edited:false,informational:true}]};
      settings.set(selection.state,state);
    }
    const cfg=state.actions[0];
    if(!cfg.manualReach){
      const coverage=Number(cfg.coverage);
      cfg.reach=String(cfg.coverage).trim()!==''&&Number.isFinite(coverage)&&coverage>=0&&coverage<=100?Math.floor(base*coverage/100):'';
    }
    return state;
  }
  function configurationError(cfg,base){
    if(!cfg)return 'No se encontró una actividad del plan para este estado.';
    const reach=Number(cfg.reach),low=Number(cfg.low),central=Number(cfg.effect),high=Number(cfg.high);
    if([cfg.reach,cfg.low,cfg.effect,cfg.high].some(v=>String(v).trim()===''))return 'Completa cobertura y los tres valores de efecto.';
    if(!Number.isInteger(reach)||reach<0||reach>Math.floor(base))return 'La cobertura debe ser un entero entre 0 y '+f(Math.floor(base))+'.';
    if(![low,central,high].every(Number.isFinite)||low<0||high>100||low>central||central>high)return 'Los efectos deben cumplir 0 ≤ inferior ≤ central ≤ superior ≤ 100 puntos porcentuales.';
    return '';
  }
  function createPlan(rows,cfg){
    const coverage=Number(cfg.reach);
    const allocation=Decision.planIntervention(rows,{reach:coverage,budget:coverage,action:'info_institucional',distribution:cfg.distribution,lens:cfg.lens});
    const selected=allocation.selected.map(r=>{
      const amount=effect=>Math.min(r.served*r.risk/100,r.served*Number(effect)/100);
      const additional=amount(cfg.effect);
      return {...r,additional,additional_low:amount(cfg.low),additional_high:amount(cfg.high),after:Math.max(0,r.risk-100*additional/r.observed)};
    });
    const additional=selected.reduce((n,r)=>n+r.additional,0);
    const action={id:'plan_estatal',label:cfg.text,effect_pp:Number(cfg.effect),low_pp:Number(cfg.low),high_pp:Number(cfg.high),unit:'Personas que se supone alcanzar',estimand:'Escenario de referencia del plan documental (sección 8)',source:'https://github.com/Donatelatrump/Ine_Hackaton_2026/blob/main/docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md',citation:'Plan documental del proyecto; coeficiente ilustrativo editable, sin efecto causal local validado',limits:'Plan completo sobre una población compartida; no se suman efectos por actividad. Efecto no validado localmente.'};
    return {...allocation,selected,additional,additional_low:selected.reduce((n,r)=>n+r.additional_low,0),additional_high:selected.reduce((n,r)=>n+r.additional_high,0),after:allocation.reference_population?allocation.before-100*additional/allocation.reference_population:0,action,description:`${cfg.text}: ${cfg.activities.length} acciones del documento. Cobertura ${cfg.coverage} %; escenario ${cfg.scenario}. Referencia documental: 10 % de cobertura y 0.3–3 pp entre personas alcanzadas (central 1.5 pp). Se aplica un solo efecto compartido, sin sumar actividades; es una aproximación, no una eficacia medida del plan completo.`};
  }
  runtime.createStateScenario=function(rows,selection,baseline){
    const state=stateSettings(rows,selection,baseline.denominator),cfg=state.actions[state.selected];
    runtime.stateScenarioError=configurationError(cfg,baseline.denominator);
    return runtime.stateScenarioError?null:createPlan(rows,cfg);
  };

  function renderDiagnosis(rows,selection,baseline){
    const sourcesOpen=$('d7-diagnosis').querySelector('details')?.open||false;
    const young=weighted(rows,'young_pct'),urban=weighted(rows,'urban_pct'),older=weighted(rows,'older_pct');
    const reference=A.summary(rows,2027,'baseline').rate;
    const delta=Number.isFinite(reference)&&Number.isFinite(baseline.rate)?baseline.rate-reference:null;
    diagnostic={young,urban,older,reference,delta,rate:baseline.rate,base:baseline.denominator};
    $('d7-diagnosis').hidden=false;
    $('d7-diagnosis').innerHTML=`<h4>Datos que orientan la recomendación</h4><div class="d7-diagnosis-grid"><article><span>Abstención estimada · 2027</span><strong>${p(baseline.rate)}</strong><small>${Number.isFinite(delta)?(delta>=0?'+':'')+pp(delta)+' frente a la referencia de 2021':'Sin referencia comparable'}</small></article><article><span>Proporción de 18–29 años</span><strong>${p(young)}</strong><small>Composición agregada del antecedente</small></article><article><span>Proporción en zonas urbanas</span><strong>${p(urban)}</strong><small>Composición agregada del antecedente</small></article></div><p class="d6-note">CCPC, último antecedente disponible; promedios ponderados por la base observable de municipios estimables con cada indicador disponible. Describen composición y asociaciones territoriales; no demuestran causas individuales. <a href="https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/" target="_blank" rel="noopener noreferrer">Fuente oficial CCPC ↗</a></p>`;
    const sources=document.createElement('details');sources.className='d7-inline-details';sources.open=sourcesOpen;
    const sourceLabel=document.createElement('summary');sourceLabel.textContent='Fuentes y alcance de los datos';
    sources.append(sourceLabel,$('d7-diagnosis').querySelector('.d6-note'));$('d7-diagnosis').append(sources);
    [...document.querySelectorAll('.d7-action-list li')].forEach(li=>{
      const t=normalized(li.dataset.actionText||li.textContent);
      let reason;
      if(/joven|universidad|bachiller|escuela|primer voto/.test(t))reason=`La proporción agregada de 18–29 años es ${p(young)}. La propuesta explora canales educativos; la edad no implica desinterés ni prueba su eficacia.`;
      else if(/rural|selva|comunitari/.test(t))reason=`La proporción urbana es ${p(urban)}${Number.isFinite(urban)?' (complemento no urbano: '+p(100-urban)+')':''}. Conviene validar cobertura territorial y accesibilidad antes de elegir sedes.`;
      else if(/mayor|legib|accesib/.test(t))reason=`La proporción de personas de 60 años o más es ${p(older)}. La accesibilidad debe validarse con usuarios y mantenerse abierta a toda la comunidad.`;
      else reason=`La abstención estimada es ${p(baseline.rate)}${Number.isFinite(delta)?', con diferencia de '+pp(delta)+' respecto de la referencia de 2021':''}. Esto orienta dónde revisar; no demuestra que esta actividad vaya a reducirla.`;
      let box=li.querySelector('.d7-action-rationale');if(!box){box=document.createElement('details');box.className='d7-action-rationale';li.append(box);}
      const open=box.open;
      box.innerHTML='<summary>Por qué esta acción</summary><p>'+esc(reason)+' Regla del prototipo por validar con la junta local. Fuente: CCPC y plan documental.</p>';
      box.open=open;
    });
  }
  function renderEditor(data){
    const state=stateSettings(data.rows,data.selection,data.baseline.denominator),cfg=state.actions[state.selected];
    $('d7-action-editor').hidden=false;
    const key=data.selection.state+'|'+state.selected;
    if(formKey!==key){
      $('d7-plan-action').replaceChildren(...state.actions.map((a,i)=>new Option(a.text,String(i))));
      $('d7-plan-action').value=String(state.selected);
      for(const [id,field] of [['reach','reach'],['effect','effect'],['low','low'],['high','high'],['distribution','distribution'],['lens','lens']])$('d7-action-'+id).value=String(cfg?.[field]??'');
      formKey=key;
    }
    $('d7-action-reach').max=String(Math.floor(data.baseline.denominator));
    $('d7-plan-coverage').value=String(cfg.coverage);
    $('d7-plan-scenario').value=cfg.scenario;
    $('d7-action-assumption').textContent='Referencia: sección 8 del documento de planes estatales. Al 10 % de cobertura: +0.03 a +0.30 pp de participación (central +0.15 pp). Se usa un efecto compartido para todas las acciones, sin duplicar personas. No es eficacia comprobada del plan.';
    $('d7-editor-error').textContent=configurationError(cfg,data.baseline.denominator);
    $('d7-editor-mode').textContent=$('action').value==='ninguna'?'Plan completo: todas las acciones mostradas arriba.':'Simulador general activo. Pulsa Simular plan estatal para volver al plan investigado.';
  }

  function allocationRows(){
    if(!snapshot)return [];
    const ranked=Decision.rank(snapshot.rows,snapshot.lens),positions=new Map(ranked.map((r,i)=>[r.key,i+1]));
    const selected=new Map(snapshot.plan.selected.map(r=>[r.key,r]));
    return snapshot.rows.map(r=>{
      const assigned=selected.get(r.key),eligible=validRow(r),served=assigned?.served||0;
      return {key:r.key,name:r.name,state:r.state_name,position:positions.get(r.key)||null,status:!eligible?'Sin estimación':served>0?'Con atención':'Pendiente',served,before:eligible?r.risk:null,reduction:eligible?r.risk-(assigned?.after??r.risk):null,reason:!eligible?'Revisar calidad de los datos':snapshot.plan.distribution==='proporcional'?'Cuota proporcional a SV+NV 2024':criterion[snapshot.lens]};
    }).sort((a,b)=>(a.position??Infinity)-(b.position??Infinity)||a.key.localeCompare(b.key));
  }
  function renderAllocation(){
    const all=allocationRows(),filter=$('d7-allocation-filter').value;
    const list=all.filter(r=>filter==='todos'||filter==='atendidos'&&r.status==='Con atención'||filter==='pendientes'&&r.status==='Pendiente'||filter==='sin_datos'&&r.status==='Sin estimación');
    const pages=Math.max(1,Math.ceil(list.length/10));page=Math.min(page,pages-1);
    $('d7-allocation-rows').innerHTML=list.slice(page*10,page*10+10).map(r=>`<tr><td>${r.position||'—'}</td><td>${esc(r.name)}<small>${esc(r.state)} · ${r.key}</small></td><td>${r.status}</td><td>${f(r.served)}</td><td>${p(r.before)}</td><td>${pp(r.reduction)}</td><td>${esc(r.reason)}</td></tr>`).join('')||'<tr><td colspan="7">No hay municipios en esta categoría.</td></tr>';
    $('d7-allocation-page').textContent=`Página ${page+1} de ${pages} · ${list.length} municipios`;
    $('d7-allocation-prev').disabled=page===0;$('d7-allocation-next').disabled=page>=pages-1;
    const treated=all.filter(r=>r.status==='Con atención').length,pending=all.filter(r=>r.status==='Pendiente').length,missing=all.filter(r=>r.status==='Sin estimación').length;
    $('d7-allocation-summary').textContent=`${treated} atendidos · ${pending} pendientes · ${missing} sin estimación · ${f(snapshot.plan.served)} personas. Distribución ${snapshot.plan.distribution==='proporcional'?'proporcional':'por prioridad'}; ${criterion[snapshot.lens].toLowerCase()}.`;
  }
  function adoptSnapshot(data){
    snapshot=data;
    const international=$('action').value!=='ninguna'&&snapshot;
    if(international){
      const a=snapshot.plan.action,t=snapshot.territory,delta=t.before-t.after;
      $('d7-international-impact').innerHTML=`<strong>${esc(a.country||'Escenario personalizado')} ${Number.isFinite(a.effect_pp)?'· referencia: +'+pp(a.effect_pp)+' de participación':''}</strong><br>Abstención 2027: <strong>${p(t.before)} → ${p(t.after)}</strong> · reducción relativa <strong>${p(t.before>0?100*delta/t.before:0)}</strong> (${pp(delta)}).<small> Transferencia hipotética al territorio seleccionado; no es un efecto comprobado en México.</small>`;
    }else{
      $('d7-international-impact').textContent=$('action').value==='ninguna'?'Elige una estrategia internacional para ver el efecto del estudio y su impacto estimado en el territorio.':'Revisa la cobertura para calcular el impacto de la estrategia.';
    }
    for(const id of ['d7-allocation','d7-comparison-block'])$(id).hidden=!snapshot;
    for(const id of ['d7-download-brief','d7-print-brief','d7-allocation-download'])$(id).disabled=!snapshot;
    if(!snapshot){$('d7-allocation-rows').innerHTML='';return;}
    const key=JSON.stringify([snapshot.selection,snapshot.plan.served,snapshot.plan.additional,snapshot.plan.distribution,snapshot.lens]);
    if(key!==allocationKey){page=0;allocationKey=key;}
    renderAllocation();runtime.refreshComparisonMaps?.();
  }
  runtime.getDisplayedScenario=()=>snapshot;
  runtime.renderPlanning=function(data){
    renderDiagnosis(data.rows,data.selection,data.baseline);renderEditor(data);
    const manual=$('action').value!=='ninguna';
    const rows=manual?filtered:data.rows;
    const scenario=manual?(simulationActive()&&$('reach').checkValidity()?plan:null):data.scenarioPlan;
    const lens=manual?$('lens').value:settings.get(data.selection.state)?.actions[settings.get(data.selection.state).selected]?.lens||'tasa';
    const exportDiagnosis=manual?{young:weighted(rows,'young_pct'),urban:weighted(rows,'urban_pct'),older:weighted(rows,'older_pct')}:diagnostic;
    adoptSnapshot(data.valid&&scenario?{rows,plan:scenario,territory:Decision.territorialScenario(rows,scenario),selection:{...data.selection},method:data.selection.method,label:manual?context.territoryLabel():rows[0]?.state_name||data.selection.state,lens,diagnostic:exportDiagnosis,mode:manual?'Simulador general':'Plan estatal investigado'}:null);
  };
  const previousSummary=runtime.views.renderSummary;
  runtime.views.renderSummary=function(ctx){
    context=ctx;previousSummary(ctx);
    if(ctx.state.year!==2027){
      $('d7-diagnosis').hidden=true;$('d7-action-editor').hidden=true;
      formKey='';adoptSnapshot(null);return;
    }
    if(!ctx.state.state){
      $('d7-diagnosis').hidden=true;$('d7-action-editor').hidden=true;formKey='';
      adoptSnapshot(ctx.state.year===2027&&simulationActive()?{rows:filtered,plan,territory:Decision.territorialScenario(filtered,plan),selection:{...ctx.state},method:ctx.state.method,label:ctx.territoryLabel(),lens:$('lens').value,diagnostic:null,mode:'Simulador general'}:null);
    }
  };

  function download(text,name,type){
    const blob=new Blob([text],{type}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),30000);
  }
  function downloadAllocation(){
    if(!snapshot)return;
    const cell=value=>{let text=String(value??'');if(typeof value==='string'&&/^[=+\-@]/.test(text))text="'"+text;return '"'+text.replace(/"/g,'""')+'"';};
    const s=snapshot,a=s.plan.action,t=s.territory;
    const lookup=new Map(s.rows.map(r=>[r.key,r]));
    const rows=[['Prioridad','Clave INE','Municipio','Estado','Atención','Personas asignadas','Abstención base (%)','Reducción (pp)','Criterio','Abstención con acción (%)','Semáforo sin acción','Semáforo con acción','Umbral medio (%)','Umbral alto (%)','Base observable SV+NV 2024','Año proyectado','Método','Territorio','Catálogo constante','Distribución','Acción','Unidad de cobertura','Efecto supuesto o externo (pp)','Límite inferior efecto (pp)','Límite superior efecto (pp)','Respuesta personalizada (%)','Estimador o supuesto','Fuente de la acción','Cita','Límites','Cobertura total asignada','Base territorial incluida','Abstención territorial sin acción (%)','Abstención territorial con acción (%)'],...allocationRows().map(r=>{
      const after=Number.isFinite(r.before)?r.before-r.reduction:null;
      return [r.position,r.key,r.name,r.state,r.status,r.served,r.before,r.reduction,r.reason,after,Decision.level(r.before,thresholds),Decision.level(after,thresholds),thresholds.low,thresholds.high,lookup.get(r.key)?.observed,2027,A.methodName(s.method),s.label,s.selection.stable,s.plan.distribution,a.label,a.unit,a.effect_pp,a.low_pp,a.high_pp,a.id==='personalizada'?Number($('response').value):null,a.estimand,a.source,a.citation,a.limits,s.plan.served,t.population,t.before,t.after];
    })];
    download('\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\r\n'),'Umbral_demo7_distribucion.csv','text/csv;charset=utf-8');
  }
  function brief(){
    if(!snapshot)return '';
    const s=snapshot,t=s.territory,action=s.plan.action,top=allocationRows().filter(r=>r.served>0).slice(0,5),d=s.diagnostic;
    const source=action.source&&/^https:\/\//.test(action.source)?action.source:'https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/';
    const date=new Date().toLocaleString('es-MX',{timeZone:'America/Mexico_City'});
    return `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Umbral · Ficha de ${esc(s.label)}</title><style>@page{size:A4;margin:12mm}*{box-sizing:border-box}body{font:12px/1.45 Arial,sans-serif;color:#172d28;max-width:185mm;margin:22px auto;padding:0 12px}h1{font-size:25px;margin:8px 0}h2{font-size:15px;margin:16px 0 6px}p{margin:6px 0}.top{font-size:10px;color:#52645c}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.metrics div{padding:12px;background:#edf3ef;border:1px solid #cad8cf;border-radius:8px}.metrics b{font-size:22px;display:block}.metrics span{font-size:11px}table{width:100%;border-collapse:collapse;font-size:11px}th,td{text-align:left;padding:7px 4px;border-bottom:1px solid #d6ded9}a{color:#224f74;overflow-wrap:anywhere}.note{font-size:10px;color:#52645c}.actions{margin:12px 0}button{padding:10px;border:1px solid #173f35;border-radius:6px;background:white;color:#173f35}svg{width:100%;height:75px}.limit{border-left:3px solid #c69036;padding:7px 11px;background:#fbf5e8}@media print{body{margin:0;padding:0;font-size:11px}.actions{display:none}a{color:inherit}h2,table,.metrics,.limit{break-inside:avoid}.note{font-size:9px}}</style></head><body><p class="top">AGUAS.EXE · UMBRAL · RETO 2 · DEMO7 · ${esc(date)}</p><h1>${esc(s.label)} · escenario 2027</h1><p>${esc(s.mode)} · ${esc(A.methodName(s.method))} · ${s.selection.stable?'Catálogo constante':'Catálogo completo'} · base observable: ${f(t.population)} personas (SV+NV 2024).</p><div class="actions"><button onclick="window.print()">Imprimir / guardar como PDF</button></div><div class="metrics"><div><span>Abstención sin acción</span><b>${p(t.before)}</b></div><div><span>Abstención con acción</span><b>${p(t.after)}</b></div><div><span>Votos adicionales hipotéticos</span><b>≈ ${f(t.additional)}</b></div></div><svg viewBox="0 0 650 75" role="img" aria-label="Comparación de abstención en escala de cero a cien"><text x="0" y="20" font-size="12">Sin acción</text><rect x="110" y="5" width="${Math.max(0,t.before)*4.5}" height="18" fill="#b95d77"/><text x="0" y="55" font-size="12">Con acción</text><rect x="110" y="40" width="${Math.max(0,t.after)*4.5}" height="18" fill="#1a7769"/><text x="570" y="20" font-size="12">${p(t.before)}</text><text x="570" y="55" font-size="12">${p(t.after)}</text></svg><p>Reducción: <strong>${pp(t.before-t.after)}</strong> · alcance supuesto: <strong>${f(s.plan.served)}</strong> personas.</p><h2>Diagnóstico y acción</h2><p>${d?'Proporciones agregadas: jóvenes '+p(d.young)+'; zonas urbanas '+p(d.urban)+'.':'Diagnóstico territorial según la proyección del método activo.'} Son datos descriptivos, no causas.</p><p><strong>${esc(action.label)}</strong></p><p class="note">${esc(action.estimand||'Supuesto editable')} · ${Number.isFinite(action.effect_pp)?'Efecto central: '+action.effect_pp+' pp entre alcanzados. ':''}${Number.isFinite(action.low_pp)?'Rango de efecto: '+action.low_pp+' a '+action.high_pp+' pp. ':''}${esc(action.unit||'Cobertura supuesta')}. ${esc(action.citation||'Respuesta declarada por el usuario.')}</p><h2>Priorización de recursos</h2><p>Distribución ${s.plan.distribution==='proporcional'?'proporcional a SV+NV 2024':'por prioridad'}; ${esc(criterion[s.lens])}. ${allocationRows().filter(r=>r.status==='Con atención').length} municipios atendidos; ${allocationRows().filter(r=>r.status==='Pendiente').length} pendientes; ${allocationRows().filter(r=>r.status==='Sin estimación').length} sin estimación.</p><table><thead><tr><th>Municipio (primeros cinco)</th><th>Personas asignadas</th><th>Reducción</th></tr></thead><tbody>${top.map(r=>`<tr><td>${esc(r.name)} · ${r.key}</td><td>${f(r.served)}</td><td>${pp(r.reduction)}</td></tr>`).join('')||'<tr><td colspan="3">Sin atención asignada.</td></tr>'}</tbody></table><h2>Fuentes y límites</h2><p class="note"><a href="https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/">CCPC INE 2009–2024</a> · <a href="${esc(source)}">Fuente de la acción / supuesto</a> · <a href="https://github.com/Donatelatrump/Ine_Hackaton_2026/blob/main/docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md">Plan documental</a></p><p class="limit">Proyección exploratoria y acción hipotética. El efecto del plan es una referencia documental sin validación local. No se suman efectos por actividad. La base de 2024 no proyecta el electorado de 2027; los municipios sin estimación no cuentan como cero. El rango del efecto no es un intervalo de confianza de 2027. Recursos expresados en personas, sin costos monetarios inventados.</p></body></html>`;
  }

  let tourStep=0,highlighted=null;
  const steps=[
    ['Diagnóstico','Ubica el territorio y explica qué muestran los antecedentes. El botón de ejemplo prepara el caso histórico 23008 y una simulación reproducible.','#d7-diagnosis'],
    ['Predicción','Muestra la proyección 2027 frente a los antecedentes. Es exploratoria; cambia de método para explicar la sensibilidad.','#d6-history-title'],
    ['Acción','Relaciona la propuesta con datos agregados. Simula el plan estatal investigado y compara escenarios de cobertura e impacto.','#paso-3'],
    ['Recursos y resultado','Revisa quién recibe atención, quién queda pendiente y cuánto cambiaría la abstención. La vista de diferencias permite ver efectos pequeños.','#d7-allocation'],
    ['Compartir la propuesta','Descarga la ficha o guárdala como PDF. Incluye territorio, método, acción, cobertura, asignación, fuentes y límites.','#d7-download-brief']
  ];
  function showStep(){
    highlighted?.classList.remove('d7-tour-target');
    const [title,text,target]=steps[tourStep];
    $('d7-tour-counter').textContent=`Paso ${tourStep+1} de ${steps.length}`;$('d7-tour-title').textContent=title;$('d7-tour-text').textContent=text;
    $('d7-tour-prev').disabled=tourStep===0;$('d7-tour-next').textContent=tourStep===steps.length-1?'Terminar':'Siguiente';
    highlighted=document.querySelector(target);highlighted?.classList.add('d7-tour-target');
    highlighted?.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'center'});
  }
  function closeTour(){highlighted?.classList.remove('d7-tour-target');$('d7-tour').close();$('d7-start-tour').focus({preventScroll:true});}

  document.addEventListener('umbral:ready',()=>{
    $('action').querySelector('option[value="personalizada"]')?.remove();
    const fields=[['reach','reach'],['effect','effect'],['low','low'],['high','high'],['distribution','distribution'],['lens','lens']];
    for(const [id,field] of fields)$('d7-action-'+id).addEventListener('input',()=>{
      const state=settings.get(context.state.state);if(!state)return;state.actions[state.selected][field]=$('d7-action-'+id).value;if(field==='reach')state.actions[state.selected].manualReach=true;state.actions[state.selected].edited=true;update();
    });
    for(const id of ['d7-plan-coverage','d7-plan-scenario'])$(id).addEventListener('input',()=>{
      const state=settings.get(context.state.state);if(!state)return;
      const cfg=state.actions[0],base=A.summary(context.state.state?records.filter(r=>r.state===context.state.state&&(!context.state.stable||r.stable_catalog_state)):[],2027,context.state.method).denominator;
      const coverage=Number($('d7-plan-coverage').value);
      cfg.coverage=$('d7-plan-coverage').value;cfg.manualReach=false;cfg.reach=cfg.coverage.trim()!==''&&coverage>=0&&coverage<=100?Math.floor(base*coverage/100):'';
      cfg.scenario=$('d7-plan-scenario').value;cfg.effect={conservador:.3,central:1.5,optimista:3}[cfg.scenario];cfg.edited=true;
      $('action').value='ninguna';formKey='';update();
    });
    $('d7-plan-action').onchange=()=>{const state=settings.get(context.state.state);if(!state)return;state.selected=Number($('d7-plan-action').value);formKey='';update();};
    $('d7-use-state-action').onclick=()=>{$('action').value='ninguna';$('search').value='';$('search').dispatchEvent(new Event('input',{bubbles:true}));};
    $('d7-allocation-filter').onchange=()=>{page=0;renderAllocation();};
    $('d7-allocation-prev').onclick=()=>{page=Math.max(0,page-1);renderAllocation();};$('d7-allocation-next').onclick=()=>{page++;renderAllocation();};
    $('d7-allocation-download').onclick=downloadAllocation;
    $('d7-download-brief').onclick=()=>{exportText=brief();if(exportText)download(exportText,'Umbral_demo7_ficha_'+(snapshot.selection.state||'Mexico')+'.html','text/html;charset=utf-8');};
    $('d7-print-brief').onclick=()=>{
      exportText=brief();if(!exportText)return;
      const popup=window.open('','_blank');if(!popup)return;
      popup.document.write(exportText);popup.document.close();popup.onload=()=>popup.print();
    };
    $('d7-start-tour').onclick=()=>{
      const dialog=$('d7-tour');if(dialog.open){showStep();return;}
      $('method').value='hgb';$('stable').checked=false;
      window.Umbral7.example();$('d7-prepare-plan').click();
      tourStep=0;dialog.show();showStep();
    };
    $('d7-tour-prev').onclick=()=>{tourStep=Math.max(0,tourStep-1);showStep();};
    $('d7-tour-next').onclick=()=>{if(tourStep===steps.length-1)closeTour();else{tourStep++;showStep();}};
    $('d7-tour-close').onclick=closeTour;$('d7-tour').addEventListener('cancel',()=>highlighted?.classList.remove('d7-tour-target'));
    $('d7-tour').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();closeTour();}});
    // Immutable snapshots make scenario/export review possible without changing data.
    window.Umbral7Planning=Object.freeze({get snapshot(){return snapshot?{label:snapshot.label,method:snapshot.method,population:snapshot.territory.population,served:snapshot.plan.served,additional:snapshot.plan.additional,rows:allocationRows(),mode:snapshot.mode}:null;},get lastBrief(){return exportText;}});
  },{once:true});
})();

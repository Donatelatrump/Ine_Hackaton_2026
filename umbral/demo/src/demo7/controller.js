/* Selección común para mapa, resultados y escenarios de demo6. */
(() => {
  'use strict';
  const A=UmbralAnalytics;
  const name=A.methodName;
  let state=Object.freeze({year:2027,state:'',municipality:null,method:'baseline',stable:false});
  let ready=false;
  const thresholdCache=new Map();
  function readSelection(){
    const stateKey=$('state').value;
    const exact=records.find(r=>r.state===stateKey&&(r.key===$('search').value||r.name===$('search').value));
    state=Object.freeze({year:currentMapYear,state:stateKey,municipality:exact?.key||null,
      method:$('method').value,stable:$('stable').checked});
    return state;
  }
  function selectedRecords(){
    return A.subset(view.length?view:records,state).filter(r=>!$('search').value.trim()||matches(r));
  }
  function territoryLabel(){
    const r=state.municipality&&byKey.get(state.municipality);
    return r?r.name+' · '+r.state_name:state.state?(records.find(r=>r.state===state.state)?.state_name||state.state):'México';
  }
  function renderScenario(){
    const on=state.year===2027&&simulationActive();
    $('d6-scenario-comparison').hidden=!on;
    if(!on)return;
    const t=Decision.territorialScenario(filtered,plan);
    $('d6-scenario-bars').innerHTML=[['Sin acción',t.before],['Con acción',t.after]].map(([label,value])=>`<div class="d6-scenario-row"><span>${label}</span><div class="d6-scenario-track"><i style="width:${Number.isFinite(value)?Math.max(0,Math.min(100,value)):0}%"></i></div><strong>${pct(value)}</strong></div>`).join('');
    $('d6-scenario-detail').textContent=Number.isFinite(t.before)&&Number.isFinite(t.after)?
      'Reducción hipotética: '+(t.before-t.after).toFixed(5)+' pp. Las barras comparten escala de 0 a 100%; un efecto pequeño puede no distinguirse visualmente.':'Sin base observable suficiente para comparar.';
  }
  function refresh(){
    if(!ready)return;
    readSelection();
    const context={A,state,selectedRecords,territoryLabel,records,view,metadata,name,$,pct,fmt,esc};
    const views=runtime.views;
    views.renderSummary(context);views.renderHistory(context);views.renderEvidence(context);
    renderScenario();
    if(state.year===2027)runtime.renderStatePlan?.(state,records);
    $('method').disabled=state.year!==2027;
    $('modulo-3').hidden=state.year!==2027;
    $('d6-historical-notice').hidden=state.year===2027;
    document.querySelectorAll('a[href="#modulo-3"],a[href="#paso-3"]').forEach(link=>{link.hidden=state.year!==2027;});
    const historical=state.year!==2027;
    $('analysis-eligible-label').textContent=historical?'Con dato observado en '+state.year:'Con estimación en tu búsqueda';
    $('analysis-missing-label').textContent=historical?'Sin dato observado en '+state.year:'Sin estimación en tu búsqueda';
    $('analysis-ranking-label').textContent=historical?'No votaron en '+state.year:'Podrían no votar en 2027';
    $('analysis-description').textContent=historical?'Resultados observados de '+state.year+', participación y calidad de los datos del territorio seleccionado.':'Consulta antecedentes, proyección exploratoria de 2027 y diferencias entre métodos. La comparación con el estado usa el mismo método y filtro de catálogo.';
    $('map-year-hint').textContent=historical?'Datos observados de '+state.year+'. Puedes cambiar de año conservando la selección.':'Proyección exploratoria de 2027 con el método seleccionado. Compara con la referencia de 2021.';
    $('state-plan-panel').hidden=true;
  }
  function mapThresholds(){
    const key=currentMapYear+'|'+$('method').value;
    if(thresholdCache.has(key))return thresholdCache.get(key);
    const rates=records.map(r=>A.observation(r,currentMapYear,$('method').value).rate).filter(Number.isFinite);
    const result=rates.length?{low:quantile(rates,1/3),high:quantile(rates,2/3)}:thresholds;
    thresholdCache.set(key,result);
    return result;
  }
  function repaint(){
    if(!ready)return;
    activeMapState=$('state').value||null;
    reconstruirMapa(currentMapYear,{encuadrar:false});
    $('map-title').textContent=$('state').value?'Explora los municipios':'Explora los estados';
    $('map').setAttribute('aria-label',$('state').value?'Mapa municipal de '+territoryLabel():'Mapa de los estados de México');
    if(currentMapYear===2027&&simulationActive()){
      const mode=$('map-mode').value;
      $('map-caption').textContent=mode==='cambio'?'Reducción hipotética de la abstención, en puntos porcentuales.':mode==='intervencion'?'Abstención proyectada con la acción elegida.':'Abstención proyectada sin acción.';
      if(mode==='cambio')document.querySelector('.legend').innerHTML='<span>Reducción: blanco = 0 pp; azul claro = hasta 1 pp; azul medio = 1–5 pp; azul oscuro = más de 5 pp. Gris = sin estimación.</span>';
      if($('confidence').checked)document.querySelector('.legend').innerHTML='<span>Repetición de prioridad: verde = 6/6 variantes; ámbar = revisión. Gris = sin estimación.</span>';
    }
    refresh();
  }
  function selectMunicipality(key){
    const record=byKey.get(key);
    if(!record)return;
    $('state').value=record.state;
    activeMapState=record.state;
    $('search').value='';
    geographyFocusKey=null;
    update();
    const polygon=municipalityLayer?.getLayers().find(p=>p.feature.properties.key===key)||layer.getLayers().find(p=>p.feature.properties.key===key);
    if(polygon)focusMunicipality(key,polygon);
  }
  function preset(kind){
    if(kind==='reset'){
      $('action').value='ninguna';
    }else{
      $('action').value=kind==='sms'?'sms_suecia':'plan_voto';
      $('reach').value='1000';
      $('distribution').value=kind==='sms'?'proporcional':'prioridad';
    }
    update();
    $('d6-preset-note').textContent=kind==='reset'?'Simulación desactivada.':
      'Ejemplo editable: 1,000 '+(kind==='sms'?'personas asignadas al SMS; distribución proporcional.':'conversaciones completadas; distribución por prioridad.')+' La cobertura es un supuesto del usuario y el efecto externo no está validado para México.';
  }
  // Instantánea de diagnóstico: valores copiados, sin referencias mutables a mapas o registros.
  function inspect(stateKey=state.state){
    const rows=(view.length?view:records).filter(r=>r.state===stateKey);
    const center=map.getCenter();
    return Object.freeze({
      focusKey:geographyFocusKey,
      map:Object.freeze({lat:center.lat,lng:center.lng,zoom:map.getZoom()}),
      stateRate:A.summary(rows,state.year,state.method).rate,
      municipalityRate:state.municipality?A.observation(byKey.get(state.municipality),state.year,state.method).rate:null,
      additional:plan?.additional??0,
      stateFill:stateKey?estiloEstado(state.year)({properties:{state:stateKey}}).fillColor:null,
      thresholds:Object.freeze({...mapThresholds()})
    });
  }
  function init(){
    if(typeof mapInitialized==='undefined'||!mapInitialized)return false;
    runtime.hooks.beforeUpdate=()=>{
      const active=$('method').value==='baseline'?'ridge':$('method').value;
      for(const r of records){
        for(const limit of [5,10,20]){
          r.variants['persistencia_'+limit]=r.model_variants?.baseline?.[limit]??null;
          r.variants['ridge_'+limit]=r.model_variants?.[active]?.[limit]??null;
        }
      }
    };
    runtime.hooks.afterUpdate=()=>{
      if(currentMapYear!==2027)updateExplorationAnalysis();
      repaint();
    };
    runtime.hooks.afterExplore=refresh;
    runtime.hooks.afterFocus=refresh;
    runtime.selectMunicipality=selectMunicipality;
    runtime.hooks.afterScope=()=>{
      if($('simulation-scope').value==='municipio'){
        const key=$('simulation-municipality').value;
        const polygon=layer.getLayers().find(p=>p.feature.properties.key===key);
        if(polygon)focusMunicipality(key,polygon);
      }else{reconstruirMapa(currentMapYear);}
      refresh();
    };
    // Los controles comparten selección y el cambio de método conserva el encuadre.
    $('method').value=A.initialMethod(metadata);
    $('d6-export').addEventListener('click',()=>{
      readSelection();
      const content=A.csv(selectedRecords(),state,metadata,{compact:true});
      const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));
      const a=document.createElement('a');a.href=url;a.download='Umbral_consulta_'+(state.municipality||state.state||'Mexico')+'_'+state.year+'.csv';
      a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
    $('d6-excel').addEventListener('click',()=>{
      readSelection();
      const rows=UmbralSpreadsheet.parseCsv(A.csv(selectedRecords(),state,metadata,{compact:true}));
      const numeric=new Set([3,6,7,8,9,10]);
      const table=rows.map((row,i)=>row.slice(0,12).map((v,c)=>i&&numeric.has(c)&&v!==''?Number(v):v));
      UmbralSpreadsheet.download([
        {name:'Consulta',title:'UMBRAL | Consulta territorial',subtitle:territoryLabel()+' | '+state.year,rows:table,widths:[14,25,32,12,26,28,22,22,20,20,16,22]},
        {name:'Fuentes',title:'UMBRAL | Fuentes y alcance',subtitle:'Datos agregados de participacion ciudadana',rows:[['Concepto','Detalle'],['Fuente',rows[1]?.[12]||'INE CCPC'],['Nota',rows[1]?.[13]||'Consulta sin registros'],['Metodo',state.year===2027?A.methodName(state.method):'Dato observado']],widths:[30,100]}
      ],'Umbral_consulta_'+(state.municipality||state.state||'Mexico')+'_'+state.year+'.xlsx');
    });
    document.querySelectorAll('[data-d6-preset]').forEach(button=>button.addEventListener('click',()=>preset(button.dataset.d6Preset)));
    $('d6-return-2027').addEventListener('click',()=>{$('map-year').value='2027';$('map-year').dispatchEvent(new Event('change'));});
    $('map-year').addEventListener('change',()=>{
      if(currentMapYear!==2027)$('action').value='ninguna';
      update();
    });
    window.Umbral6=Object.freeze({get state(){return state;},selectMunicipality,refresh,preset,returnToMexico:volverAMexico,inspect});
    ready=true;
    update();
    return true;
  }
  // Reemplazar solo el estilo de demo6: una única agregación para mapa y resumen.
  runtime.mapStyles.state=year=>feature=>{
    const method=$('method').value;
    const rows=(view.length?view:records).filter(r=>r.state===feature.properties.state&&(!$('stable').checked||r.stable_catalog_state));
    const simulated=year===2027&&simulationActive()&&$('map-mode').value==='intervencion';
    const data=simulated?rows.map(r=>({...r,[method]:selectedMap.get(r.key)?.after??r[method]})):rows;
    let rate=A.summary(data,year,method).rate;
    const limits=mapThresholds();
    let color=colors[!Number.isFinite(rate)?'sin_datos':rate>=limits.high?'alto':rate>=limits.low?'medio':'bajo'];
    if(year===2027&&simulationActive()&&$('map-mode').value==='cambio'){
      const base=A.summary(rows,year,method).rate;
      const after=A.summary(rows.map(r=>({...r,[method]:selectedMap.get(r.key)?.after??r[method]})),year,method).rate;
      const delta=base-after;
      color=!Number.isFinite(base)?colors.sin_datos:delta>5?'#135e87':delta>1?'#4b94b8':delta>0?'#9dccdf':'#f6faf9';
    }
    return {color:'#000000',weight:1.2,fillColor:color,fillOpacity:.85,opacity:1};
  };
  runtime.mapStyles.municipality=(year,stateKey)=>feature=>{
    const r=byKey.get(feature.properties.key),method=$('method').value;
    let rate=r?A.observation(r,year,method).rate:null;
    const limits=mapThresholds();
    const selected=r&&selectedMap.get(r.key);
    if(year===2027&&simulationActive()&&$('map-mode').value==='intervencion')rate=selected?.after??rate;
    let color=colors[!Number.isFinite(rate)?'sin_datos':rate>=limits.high?'alto':rate>=limits.low?'medio':'bajo'];
    if(year===2027&&simulationActive()&&$('map-mode').value==='cambio'){
      const delta=selected?r.risk-selected.after:0;
      color=!Number.isFinite(rate)?colors.sin_datos:delta>5?'#135e87':delta>1?'#4b94b8':delta>0?'#9dccdf':'#f6faf9';
    }
    if(year===2027&&simulationActive()&&$('confidence').checked&&Number.isFinite(rate))color=stability[r.key]?.robust?'#176b58':'#ddb263';
    return {color:'#000000',weight:1.2,fillColor:color,fillOpacity:.85,opacity:1};
  };
  runtime.startController=init;
})();

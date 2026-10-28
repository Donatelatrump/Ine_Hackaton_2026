/* Demo7: persistent context, operational plans, paired maps and controlled motion. */
(() => {
  'use strict';
  const A=UmbralAnalytics;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  let latest=null, mapTimer=0, pair=[], overlays=[], bounds=null, syncing=false, mapSignature='',territorySignature='';
  const smooth=()=>reduced.matches?'auto':'smooth';
  const safePercent=n=>Number.isFinite(n)?n.toFixed(2)+'%':'Sin estimación';
  const fixedDelta=n=>Number.isFinite(n)?n.toLocaleString('es-MX',{minimumFractionDigits:2,maximumFractionDigits:5})+' pp':'Sin comparación';
  const count=n=>Number.isFinite(n)?n.toLocaleString('es-MX',{maximumFractionDigits:2}):'Sin dato';
  const revisions=new WeakMap();
  function softenUpdate(element,signature){
    if(revisions.get(element)===signature)return;
    revisions.set(element,signature);
    if(!reduced.matches&&element.animate)element.animate([{opacity:.5,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}],{duration:220,easing:'ease-out'});
  }

  function operationalPlan(){
    const container=$('d6-state-plan-content');
    if(!container||container.querySelector('.d7-action-list')||!container.querySelector('li'))return;
    container.dataset.organized='true';
    const items=[...container.children];
    let actions=[];
    const grid=document.createElement('div');grid.className='d7-plan-facts';
    for(const item of items){
      if(item.tagName==='OL'){
        actions=[...item.children].map(li=>li.textContent.trim());
        item.classList.add('d7-action-list');
        [...item.children].forEach((li,index)=>{
          const number=document.createElement('span');number.className='d7-action-number';number.textContent=String(index+1).padStart(2,'0');
          li.prepend(number);
        });
      }
      if(item.tagName==='UL'){
        [...item.children].forEach(li=>{
          const text=li.textContent.trim();
          if(/^(Actores|Indicadores|Horizonte):/.test(text)){
            const cell=document.createElement('article');
            const title=document.createElement('h4');title.textContent=text.slice(0,text.indexOf(':'));
            const description=document.createElement('p');description.textContent=text.slice(text.indexOf(':')+1).trim();
            cell.append(title,description);grid.append(cell);li.remove();
          }
        });
        if(!item.children.length)item.remove();
      }
    }
    if(grid.children.length){const followup=document.createElement('details');followup.className='d7-inline-details';const label=document.createElement('summary');label.textContent='Responsables y seguimiento';followup.append(label,grid);container.append(followup);}
    const source=document.createElement('details');source.className='d7-plan-source';
    const summary=document.createElement('summary');summary.textContent='Fuente del plan y condiciones para implementarlo';
    const note=document.createElement('p');note.textContent='Propuesta documental por validar con la junta local y las comunidades. Revisar atribuciones, accesibilidad, población destinataria y capacidad antes de ejecutar. El impacto del plan es una referencia documental, sin validación local.';
    const link=document.createElement('a');link.href='../../docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md';link.target='_blank';link.rel='noopener noreferrer';link.textContent='Consultar documento de planes estatales ↗';
    source.append(summary,note,link);container.append(source);
    if(actions.length)container.setAttribute('aria-label','Diagnóstico y '+actions.length+' acciones propuestas');
  }

  runtime.renderPlanComparison=function(selection,rows){
    const container=$('d6-state-plan-content');
    // The base renderer replaces the Markdown only on state changes.
    if(container.dataset.state!==selection.state){delete container.dataset.organized;container.dataset.state=selection.state;}
    operationalPlan();
    rows=rows.filter(r=>!selection.stable||r.stable_catalog_state).map(r=>({...r,risk:r[selection.method]}));
    const baseline=A.summary(rows,2027,selection.method);
    const automaticReach=Math.floor(baseline.denominator*.10);
    const scenarioPlan=baseline.denominator?runtime.createStateScenario(rows,selection,baseline):null;
    const territory=scenarioPlan?Decision.territorialScenario(rows,scenarioPlan):null;
    const hasImpact=Boolean(territory&&baseline.denominator);
    const eligible=new Set(rows.filter(r=>Number.isFinite(r.risk)&&r.observed>0).map(r=>r.key));
    const assigned=scenarioPlan?scenarioPlan.selected.filter(r=>eligible.has(r.key)):[];
    const low=assigned.reduce((n,r)=>n+(r.additional_low??0),0),high=assigned.reduce((n,r)=>n+(r.additional_high??0),0);
    const served=assigned.reduce((n,r)=>n+r.served,0);
    $('d6-plan-comparison').hidden=false;
    $('d6-plan-comparison-values').innerHTML=`<article><span>Sin intervención · 2027</span><strong>${safePercent(baseline.rate)}</strong><small>Abstención; participación ${safePercent(baseline.participation)}</small></article><span class="d6-plan-comparison-arrow" aria-hidden="true">→</span><article><span>Aplicación ilustrativa · plan estatal</span><strong>${hasImpact?safePercent(territory.after):'—'}</strong><small>${hasImpact?'Participación '+safePercent(100-territory.after)+' · cambio '+fixedDelta(territory.before-territory.after):'Introduce una cobertura válida para calcular el impacto.'}</small></article>`;
    $('d7-plan-impact-metrics').innerHTML=hasImpact?`<article><span>Votos adicionales aproximados</span><strong>≈ ${fmt.format(territory.additional)}</strong><small>${Number.isFinite(scenarioPlan.action.low_pp)?'Rango supuesto: '+fmt.format(low)+' a '+fmt.format(high):'Respuesta definida en tu simulación'}</small></article><article><span>Reducción relativa de abstención</span><strong>${safePercent(territory.before>0?100*(territory.before-territory.after)/territory.before:0)}</strong><small>Participación: +${fixedDelta(territory.before-territory.after)}</small></article><article><span>Personas alcanzadas en el estado</span><strong>${fmt.format(served)}</strong><small>10 % de la base estatal estimable</small></article>`:'';
    $('d6-plan-comparison-note').textContent=hasImpact?
      `${scenarioPlan.description} Promedio estatal sobre ${fmt.format(baseline.denominator)} personas (SV+NV 2024). El modelo y el filtro de consulta se conservan. Este resultado del plan es independiente de las acciones simuladas debajo.`:
      'No hay base estimable suficiente para calcular el impacto del estado con estos filtros.';
    $('d7-prepare-plan').disabled=!baseline.denominator;
    $('d7-impact-caption').textContent=`Plan estatal hipotético de ${rows[0]?.state_name||'la entidad'}: ${fmt.format(served)} personas, equivalentes al 10 % de la base estatal estimable, y efecto supuesto de 1.5 pp. Este alcance pertenece al plan estatal; no es la cobertura que introduces en el simulador de abajo. Son escenarios alternativos y no se suman. No es eficacia medida del plan.`;
    softenUpdate($('d6-plan-comparison-values'),$('d6-plan-comparison-values').textContent);
    runtime.renderPlanning?.({selection,rows,baseline,scenarioPlan,territory,automatic:true,valid:hasImpact});
  };

  const originalSummary=runtime.views.renderSummary;
  runtime.views.renderSummary=function(context){
    originalSummary(context);latest=context;
    softenUpdate($('d6-summary'),$('d6-summary').textContent);
    const {state,territoryLabel}=context;
    const label=territoryLabel()+' · '+state.year+' · '+(state.year===2027?'Proyección exploratoria · '+A.methodName(state.method):'Dato observado');
    if($('d7-context-label').textContent!==label)$('d7-context-label').textContent=label;
    $('d7-back-forecast').hidden=state.year===2027;
    $('d7-context-action').hidden=state.year!==2027;
    $('d7-model-takeaway').textContent='Proyección exploratoria con antecedentes electorales, edad y urbanización. La evaluación retrospectiva no confirma 2027.';
    $('method-note').textContent='Se comparan cuatro modelos con una referencia de 2021 usando los cortes de 2021 y 2024. Ambos participan en la selección retrospectiva. El método elegido no está validado para 2027; los escenarios de intervención dependen de supuestos explícitos.';
    $('methodology').innerHTML='<p>Los modelos usan antecedentes anteriores al objetivo y variables agregadas de edad y urbanización. Los cortes de 2021 y 2024 participan en la selección retrospectiva entre cuatro modelos. 2024 es presidencial; 2027 es intermedia. No existe una prueba futura independiente de 2027.</p><p>Abstención = NV / (SV + NV). La proyección y los escenarios usan SV+NV 2024 como base observable; no estiman el electorado de 2027. Los municipios sin estimación no cuentan como cero. Los umbrales por tercios se fijan con la proyección base del método activo y se conservan al comparar escenarios.</p><p>Los efectos de acciones son supuestos o transferencias de estudios externos, según la fuente de cada acción. Su rango no es un intervalo de confianza para la predicción futura. La frecuencia de selección entre variantes no es una probabilidad calibrada. Ver el reporte metodológico para fuentes, cohortes y limitaciones.</p>';
    const limits=thresholds;
    if(limits&&state.year===2027){
      let key=$('d7-thresholds');
      if(!key){key=document.createElement('p');key.id='d7-thresholds';key.className='d6-note';document.querySelector('#paso-1-map .map-reading').append(key);}
      key.hidden=false;key.textContent=`Semáforo de abstención relativa: bajo < ${safePercent(limits.low)}; medio desde ${safePercent(limits.low)} y < ${safePercent(limits.high)}; alto ≥ ${safePercent(limits.high)}. Gris: sin estimación. Cortes nacionales por tercios del método activo, fijos entre escenarios. No son probabilidades ni umbrales oficiales. Los colores estatales resumen municipios estimables.`;
      const standard=!$('confidence').checked&&(!simulationActive()||$('map-mode').value!=='cambio');
      if(standard){
        document.querySelector('#paso-1-map .legend').innerHTML=[
          ['low','Menor abstención','< '+safePercent(limits.low)],
          ['medium','Intermedia',safePercent(limits.low)+' – < '+safePercent(limits.high)],
          ['high','Mayor abstención','≥ '+safePercent(limits.high)],
          ['missing','Sin estimación','Datos insuficientes']
        ].map(([color,label,range])=>`<span><i class="${color}" aria-hidden="true"></i><span class="map-key-label">${label}<small>${range.replace(/</g,'&lt;')}</small></span></span>`).join('');
      }
    }else if($('d7-thresholds'))$('d7-thresholds').hidden=true;
    const guide=document.querySelector('#paso-1-map .map-guide');
    if(guide)guide.textContent=state.municipality?'Selecciona otro municipio para comparar.':state.state?'Selecciona un municipio para abrir su ficha.':'Selecciona un estado para explorar sus municipios.';
    scheduleMaps();
    document.dispatchEvent(new CustomEvent('umbral7:updated'));
  };

  const originalHistory=runtime.views.renderHistory;
  runtime.views.renderHistory=function(context){
    originalHistory(context);
    softenUpdate($('d6-history-chart'),JSON.stringify(context.state));
  };

  function prepareExample(){
    if(!window.Umbral6)return;
    $('map-year').value='2027';$('map-year').dispatchEvent(new Event('change'));
    // Historical key 23008 is the reproducible case used in the project documentation.
    const record=records.find(r=>r.key==='23008'&&Number.isFinite(r[$('method').value]))||records.find(r=>Number.isFinite(r[$('method').value]));
    if(!record)return;
    $('state').value=record.state;$('search').value=record.key;
    $('state').dispatchEvent(new Event('input',{bubbles:true}));
    window.Umbral6.preset('sms');
    $('modulo-2').scrollIntoView({behavior:smooth(),block:'start'});
    $('d7-example').textContent='Caso preparado: '+record.name;
  }

  function ensureMaps(){
    if(pair.length)return;
    pair=['d7-map-before','d7-map-after','d7-map-difference'].map(id=>L.map(id,{preferCanvas:true,scrollWheelZoom:false,zoomSnap:.25,zoomAnimation:!reduced.matches,fadeAnimation:!reduced.matches}).setView([23.7,-102.5],4));
    pair.forEach((instance,index)=>{
      instance.attributionControl.addAttribution('Referencia INE / INEGI · datos agregados');
      instance.on('moveend',()=>{
        if(syncing)return;syncing=true;
        pair.forEach((other,otherIndex)=>{if(otherIndex!==index)other.setView(instance.getCenter(),instance.getZoom(),{animate:false});});syncing=false;
      });
    });
  }
  function scheduleMaps(){clearTimeout(mapTimer);mapTimer=setTimeout(renderMaps,180);}
  function renderMaps(){
    if(!latest||latest.state.year!==2027)return;
    const displayed=runtime.getDisplayedScenario?.()||(simulationActive()&&validBudget()?{rows:filtered,plan,label:latest.territoryLabel(),method:latest.state.method}:null);
    if(!displayed||!displayed.plan)return;
    const difference=$('d7-map-view')?.value==='difference';
    const selected=new Map(displayed.plan.selected.map(r=>[r.key,r]));
    const maxDelta=Math.max(0,...displayed.plan.selected.map(r=>Math.abs(r.risk-r.after)));
    const t=Decision.territorialScenario(displayed.rows,displayed.plan);
    const improving=displayed.rows.filter(r=>Number.isFinite(r.risk)&&r.risk-(selected.get(r.key)?.after??r.risk)>1e-10);
    const crossings=improving.filter(r=>Decision.level(r.risk,thresholds)!==Decision.level(selected.get(r.key).after,thresholds)).length;
    $('d7-maps-context').textContent=`${displayed.label} · ${A.methodName(displayed.method)} · ${fmt.format(t.municipalities)} / ${fmt.format(displayed.rows.length)} municipios estimables`;
    $('d7-change-summary').innerHTML=`<article><span>Reducción media</span><strong>${fixedDelta(t.before-t.after)}</strong><small>Abstención ${safePercent(t.before)} → ${safePercent(t.after)}</small></article><article><span>Votos adicionales hipotéticos</span><strong>≈ ${fmt.format(t.additional)}</strong><small>Con la cobertura y el efecto declarados</small></article><article><span>Municipios con reducción</span><strong>${improving.length} / ${t.municipalities}</strong><small>${crossings} cambian de categoría</small></article>`;
    $('d7-change-explanation').textContent=maxDelta<1e-10?'Sin cambio con los supuestos actuales.':crossings===0?'Hay reducción, aunque el semáforo conserva las mismas categorías.':`${crossings} municipios cambian de categoría del semáforo.`;
    $('d7-map-legend').innerHTML=difference?`<span><i style="background:#f4f5f0"></i>Sin cambio</span>${maxDelta>1e-10?`<span><i style="background:#b7dce3"></i>Baja: &lt; ${fixedDelta(maxDelta/3)}</span><span><i style="background:#5aacc1"></i>Media: &lt; ${fixedDelta(maxDelta*2/3)}</span><span><i style="background:#15586d"></i>Alta: hasta ${fixedDelta(maxDelta)}</span>`:''}<span>Escala relativa a este escenario, en puntos porcentuales.</span><span><i style="background:${colors.sin_datos}"></i>Sin estimación</span>`:[['bajo','Menor: < '+safePercent(thresholds.low)],['medio','Intermedia'],['alto','Mayor: ≥ '+safePercent(thresholds.high)],['sin_datos','Sin estimación']].map(([key,text])=>`<span><i style="background:${colors[key]}"></i>${text}</span>`).join('');
    $('d7-map-explanation').textContent=difference?'El azul más oscuro representa la mayor reducción dentro de este escenario. La leyenda muestra su magnitud exacta; la escala se ajusta a los supuestos actuales. Cartografía de referencia: límites históricos sin armonizar.':'Estos dos mapas mantienen los mismos umbrales de riesgo. Una reducción pequeña puede conservar el mismo color. Usa «Ver cambio exacto» para examinar la diferencia en puntos porcentuales.';
    const box=$(difference?'d7-map-difference':'d7-map-before').getBoundingClientRect();
    if(box.width<1||box.bottom<0||box.top>window.innerHeight+500)return;
    ensureMaps();
    const keys=displayed.rows.map(r=>r.key);
    const signature=JSON.stringify([latest.state,keys,displayed.plan.action.id,displayed.plan.served,displayed.plan.additional,displayed.plan.distribution,displayed.plan.selected.map(r=>[r.key,r.served,r.after]),difference,$('lens').value]);
    if(signature===mapSignature){pair.forEach(m=>m.invalidateSize({pan:false}));return;}
    const lookup=new Map(displayed.rows.map(r=>[r.key,r]));
    const features=geo.features.filter(f=>lookup.has(f.properties.key));
    const deltaColor=delta=>!Number.isFinite(delta)?colors.sin_datos:Math.abs(delta)<1e-10?'#f4f5f0':delta<0?'#b45c78':delta/maxDelta<1/3?'#b7dce3':delta/maxDelta<2/3?'#5aacc1':'#15586d';
    const fc={type:'FeatureCollection',features};
    if(!features.length){mapSignature='';return;}
    const nextTerritory=JSON.stringify(features.map(feature=>feature.properties.key));
    const refit=nextTerritory!==territorySignature;
    pair.forEach((instance,index)=>{
      if(overlays[index])instance.removeLayer(overlays[index]);
      overlays[index]=L.geoJSON(fc,{
        style:feature=>{const r=lookup.get(feature.properties.key);const rate=index?(selected.get(r.key)?.after??r.risk):r.risk;return {fillColor:index===2?deltaColor(Number.isFinite(r.risk)?r.risk-rate:null):colors[Decision.level(rate,thresholds)],fillOpacity:.85,color:'#fffdf7',weight:.6};},
        onEachFeature:(feature,polygon)=>{const r=lookup.get(feature.properties.key);const rate=index?(selected.get(r.key)?.after??r.risk):r.risk;const text=document.createElement('span');text.textContent=r.name+' · '+(index===2&&Number.isFinite(r.risk)?'Reducción '+fixedDelta(r.risk-rate)+' · '+r.risk.toFixed(5)+'% → '+rate.toFixed(5)+'% · ≈ '+fmt.format(selected.get(r.key)?.additional||0)+' votos adicionales':safePercent(rate));polygon.bindTooltip(text);}
      }).addTo(instance);
    });
    bounds=overlays[0].getBounds();
    syncing=true;
    pair.forEach(m=>m.invalidateSize({pan:false}));
    const visible=pair.find(m=>m.getContainer().clientWidth>0);
    if(refit&&visible)visible.fitBounds(bounds,{padding:[18,18],maxZoom:11,animate:false});
    if(visible)pair.forEach(m=>{if(m!==visible)m.setView(visible.getCenter(),visible.getZoom(),{animate:false});});
    syncing=false;
    territorySignature=nextTerritory;
    mapSignature=signature;
  }
  runtime.refreshComparisonMaps=scheduleMaps;

  function installMotion(){
    const art=document.querySelector('.hero-art');
    let inView=true;
    const apply=()=>art.classList.toggle('d7-paused',!inView||document.hidden||reduced.matches);
    document.addEventListener('visibilitychange',apply);reduced.addEventListener('change',apply);
    if('IntersectionObserver' in window){
      new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;apply();}).observe(art);
      const reveal=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){entry.target.classList.add('d7-visible');reveal.unobserve(entry.target);}},{threshold:.08});
      document.querySelectorAll('.module-heading,.d6-chart-box,.d6-evidence').forEach(item=>{item.classList.add('d7-reveal');reveal.observe(item);});
      const navigation=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){document.querySelectorAll('.quick-nav a').forEach(link=>{const on=link.hash==='#'+entry.target.id;link.classList.toggle('is-active',on);if(on)link.setAttribute('aria-current','step');else link.removeAttribute('aria-current');});}},{rootMargin:'-20% 0px -60% 0px'});
      document.querySelectorAll('.module').forEach(module=>navigation.observe(module));
      const mapObserver=new IntersectionObserver(entries=>{if(entries.some(entry=>entry.isIntersecting))scheduleMaps();},{rootMargin:'300px'});
      mapObserver.observe($('d7-map-before'));mapObserver.observe($('d7-map-difference'));
    }
    let frame=false;
    window.addEventListener('scroll',()=>{if(frame)return;frame=true;requestAnimationFrame(()=>{const height=document.documentElement.scrollHeight-window.innerHeight;$('scroll-progress-bar').style.transform='scaleX('+(height>0?Math.min(1,window.scrollY/height):0)+')';frame=false;});},{passive:true});
    apply();
  }

  document.addEventListener('umbral:ready',()=>{
    const header=document.querySelector('.site-header'),contextBar=document.querySelector('.d7-context-bar');
    const updateScrollOffset=()=>{
      const sticky=getComputedStyle(header).position==='sticky';
      const offset=sticky?header.getBoundingClientRect().height+contextBar.getBoundingClientRect().height+16:16;
      document.documentElement.style.setProperty('--d7-scroll-offset',offset+'px');
    };
    const headerObserver=new ResizeObserver(updateScrollOffset);
    headerObserver.observe(header);headerObserver.observe(contextBar);updateScrollOffset();
    $('d7-example').onclick=prepareExample;
    $('d7-back-forecast').onclick=()=>{$('map-year').value='2027';$('map-year').dispatchEvent(new Event('change'));};
    $('d7-prepare-plan').onclick=()=>{
      if(!latest?.state.state)return;
      if(latest.state.municipality){$('search').value='';$('search').dispatchEvent(new Event('input',{bubbles:true}));}
      $('action').value='ninguna';update();
      $('paso-3').scrollIntoView({behavior:smooth(),block:'start'});
      $('action').focus({preventScroll:true});
    };
    $('d7-fit-maps').onclick=()=>{if(bounds){syncing=true;pair.forEach(m=>m.fitBounds(bounds,{padding:[18,18],maxZoom:11,animate:false}));syncing=false;}};
    $('d7-map-view').onchange=()=>{
      const previous=pair.find(m=>m.getContainer().clientWidth>0);
      const center=previous?.getCenter(),zoom=previous?.getZoom();
      const difference=$('d7-map-view').value==='difference';
      document.querySelectorAll('[data-d7-map-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.d7MapView===$('d7-map-view').value)));
      $('d7-paired-maps').hidden=difference;$('d7-difference-wrap').hidden=!difference;
      if(center){syncing=true;pair.forEach(m=>{m.invalidateSize({pan:false});m.setView(center,zoom,{animate:false});});syncing=false;}
      mapSignature='';scheduleMaps();
    };
    document.querySelectorAll('[data-d7-map-view]').forEach(button=>button.onclick=()=>{$('d7-map-view').value=button.dataset.d7MapView;$('d7-map-view').dispatchEvent(new Event('change'));});
    document.querySelectorAll('[data-scenario-map]').forEach(link=>link.addEventListener('click',event=>{event.preventDefault();$('paso-1-map').scrollIntoView({behavior:smooth(),block:'start'});}));
    const mapResizeObserver=new ResizeObserver(()=>{territorySignature='';mapSignature='';scheduleMaps();});mapResizeObserver.observe($('d7-map-before'));mapResizeObserver.observe($('d7-map-difference'));
    $('lens-cards').addEventListener('keydown',event=>{
      const keys=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'];
      if(!keys.includes(event.key))return;
      const radios=[...$('lens-cards').querySelectorAll('[role="radio"]')];
      const position=radios.indexOf(document.activeElement);if(position<0)return;
      event.preventDefault();
      const next=event.key==='Home'?0:event.key==='End'?radios.length-1:(position+(event.key==='ArrowLeft'||event.key==='ArrowUp'?-1:1)+radios.length)%radios.length;
      radios[next].click();radios[next].focus();
    });
    installMotion();
    window.Umbral7=Object.freeze({example:prepareExample,refreshMaps:scheduleMaps,get state(){return window.Umbral6.state;},get comparisonMaps(){return pair.map(m=>({zoom:m.getZoom(),lat:m.getCenter().lat,lng:m.getCenter().lng,fitsTerritory:bounds?m.getBounds().contains(bounds):null}));}});
  },{once:true});
})();

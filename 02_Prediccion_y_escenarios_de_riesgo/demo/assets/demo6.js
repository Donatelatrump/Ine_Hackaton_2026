/* Generado por tools/construir_web.py. Editar fuentes, no este archivo. */
(() => {
'use strict';
const analyticsModule={exports:{}};
(function(module){
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.UmbralAnalytics=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const finite=Number.isFinite;
  const methodName=method=>({ridge:'Ridge',hgb:'HistGradientBoosting',lightgbm:'LightGBM',catboost:'CatBoost',baseline:'Referencia de 2021'}[method]||'Referencia de 2021');
  function initialMethod(metadata){return ['ridge','hgb','lightgbm','catboost'].includes(metadata.selected_model)?metadata.selected_model:'baseline';}
  function observation(record,year,method='baseline'){
    if(year===2027)return {rate:finite(record[method])?record[method]:null,
      weight:finite(record.observed)&&record.observed>0?record.observed:0,
      ln:record.ln,ns:record.latest_ns};
    const h=record.history.find(item=>item.year===year);
    // LN = SV + NV + NS. Los históricos exportan LN y NS%, no los conteos SV/NV.
    const weight=h&&finite(h.ln)&&finite(h.ns)?h.ln*(1-h.ns/100):0;
    return {rate:finite(h?.risk)?h.risk:null,weight:weight>0?weight:0,ln:h?.ln,ns:h?.ns};
  }
  function subset(records,state,{municipality=true}={}){
    return records.filter(r=>(!state.state||r.state===state.state)&&
      (!state.stable||r.stable_catalog_state)&&
      (!municipality||!state.municipality||r.key===state.municipality));
  }
  function summary(records,year,method){
    let weighted=0,denominator=0,totalWeight=0,valid=0;
    for(const r of records){
      const item=observation(r,year,method);
      totalWeight+=item.weight;
      if(!finite(item.rate))continue;
      valid++;
      if(item.weight>0){weighted+=item.rate*item.weight;denominator+=item.weight;}
    }
    const rate=denominator>0?weighted/denominator:null;
    return {rate,participation:finite(rate)?100-rate:null,total:records.length,valid,
      missing:records.length-valid,denominator,totalWeight,
      populationCoverage:totalWeight>0?100*denominator/totalWeight:null};
  }
  function series(records,method,maxYear=2027){
    const years=[...new Set(records.flatMap(r=>r.history.map(h=>h.year)))];
    if(maxYear===2027)years.push(2027);
    return years.filter(y=>y<=maxYear).sort((a,b)=>a-b)
      .map(year=>({year,...summary(records,year,method)}));
  }
  function historicalError(metadata,method){
    if(metadata.comparison_report)return metadata.comparison_report.cuts['2021'].models[method==='baseline'?'baseline':method]?.error_absoluto_p90;
    return metadata.checks?.['2021']?.[method==='ridge'?'ridge':'persistencia']?.error_absoluto_p90;
  }
  function csv(records,state,metadata){
    const rows=[['Clave INE','Estado','Municipio','Año','Tipo de dato','Método',
      'Abstención (%)','Participación (%)','Base SV+NV','Lista nominal','NS (%)',
      'Referencia 2021 (%)','Ridge 2027 (%)','Diferencia Ridge - referencia (pp)',
      'HistGradientBoosting 2027 (%)','LightGBM 2027 (%)','CatBoost 2027 (%)',
      'Catálogo constante','Fuente','Nota']];
    for(const r of records){
      const item=observation(r,state.year,state.method);
      rows.push([r.key,r.state_name,r.name,state.year,state.year===2027?'Proyección exploratoria':'Observado',
        state.year===2027?methodName(state.method):'No aplica',item.rate,
        finite(item.rate)?100-item.rate:null,item.weight||null,item.ln,item.ns,
        state.year===2027?r.baseline:null,state.year===2027?r.ridge:null,
        state.year===2027&&finite(r.ridge)&&finite(r.baseline)?r.ridge-r.baseline:null,
        state.year===2027?r.hgb:null,state.year===2027?r.lightgbm:null,state.year===2027?r.catboost:null,
        r.stable_catalog_state?'Sí':'No','INE · CCPC 2009–2024',
        state.year===2027?'SV+NV 2024 como base; electorado 2027 no proyectado. Sin estimación no equivale a cero.':
          'SV+NV reconstruido a partir de LN y NS%. Límites históricos sin armonizar.']);
    }
    const cell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
    return '\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\r\n');
  }
  return {methodName,initialMethod,observation,subset,summary,series,historicalError,csv};
});

})(analyticsModule);
const UmbralAnalytics=analyticsModule.exports;

/* SOURCE: src/demo6/app/runtime.js */
/* Conexiones explícitas; el generador mantiene todo este estado en una clausura privada. */
const runtime={
  views:{},renderProfile:null,startController:null,mapStyles:{},selectMunicipality:null,
  hooks:{beforeUpdate(){},afterUpdate(){},afterExplore(){},afterFocus(){},afterScope(){}}
};
if(typeof window!=='undefined'){
  window._umbralRuntime=runtime;
}


/* SOURCE: src/demo6/app/context.js */
'use strict';
const $=id=>document.getElementById(id), fmt=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0}), pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'Sin estimación';
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const TIER={alta:'🟢 Alta',media:'🟡 Media',baja:'🔴 Baja',sin_datos:'⚪ Sin datos'};
const GROUP_NAME={edad:{'18_29':'Jóvenes 18–29','30_59':'Adultos 30–59','60_mas':'Personas 60+'},sexo:{hombres:'Hombres',mujeres:'Mujeres',no_binario:'No binario'},seccion:{urbana:'Urbana',mixta:'Mixta',rural:'Rural'}};
let records,metadata,perfil,geo,map,layer,filtered=[],view=[],plan,thresholds,thresholdsCache={},stability={},frontier={nucleo:[],frontera:[],fuera:[]},activeKey=null,selectedMap=new Map(),byKey,viewCache={},normCache=new Map();
const colors={bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#8997ab'};
function quantile(values,q){const s=values.slice().sort((a,b)=>a-b),p=(s.length-1)*q,i=Math.floor(p);return s[i]+(s[Math.min(i+1,s.length-1)]-s[i])*(p-i);}
function norm2(v){let x=normCache.get(v);if(x===undefined){x=norm(v);if(normCache.size>6000)normCache.clear();normCache.set(v,x);}return x;}
function matches(r){return (!$('state').value||r.state===$('state').value)&&(!$('stable').checked||r.stable_catalog_state)&&norm2(r.name+' '+r.key).includes(norm2($('search').value.trim()));}


/* SOURCE: src/demo6/map/context.js */
/* Estado privado de las capas y la navegación de demo6. */
let currentMapYear = 2027;
let mapInitialized = false;
let historicalMapEnabled = true;
let municipalityLayer = null;
let stateOverlayLayer = null;
let boundaryLayer = null;
let contextLayer = null;
let activeMapState = null;
let municipalityLayerState = null;
let municipalityRenderer = null;
let stateRenderer = null;



/* SOURCE: src/demo6/map/renderer.js */
/* Renderer local: no modifica L.canvas ni otras APIs de Leaflet. */
function createMapRenderer(options){
  return L.Browser.svg&&typeof L.svg==='function'?L.svg(options):L.canvas(options);
}


/* SOURCE: src/demo6/map/geography.js */
'use strict';
let stateLayer, stateSummaries = new Map(), stateGeographyDirty = true, municipalMapText;
let geographyFocusKey = null;
const geographyHistory = [];
function rememberGeographyView() {
 geographyHistory.push({state:$('state').value,search:$('search').value,
  key:geographyFocusKey,detailKey:activeKey});
}
function goBackGeography() {
 if(geographyFocusKey || $('search').value){
  geographyFocusKey=null;activeKey=null;geographyHistory.length=0;
  $('search').value='';
  update();paintMunicipalityFocus();
  const polygon=stateLayer.getLayers().find(p=>p.feature.properties.state===$('state').value);
  if(polygon)map.fitBounds(polygon.getBounds(),{padding:[12,12],animate:true});
 } else if($('state').value){volverAMexico();}
}
const municipalBaseStyles = new Map();
function paintMunicipalityFocus() {
  if(typeof historicalMapEnabled !== 'undefined' && historicalMapEnabled && activeMapState){
    if(typeof paintMapSelection==='function')paintMapSelection();
    return;
  }
  layer.eachLayer(polygon=>{
  const key = polygon.feature.properties.key, base = municipalBaseStyles.get(key);
  if(!base) return;
  const other = geographyFocusKey && key !== geographyFocusKey;
  const outsideState = $('state').value && byKey.get(key).state !== $('state').value;
  polygon.setStyle({...base, ...(other||outsideState?{fillColor:'#a8b4b0',fillOpacity:.22,color:'#d7dfdb',weight:.3,opacity:.3}:{}),
   ...(other&&!outsideState?{fillOpacity:1,opacity:1}:{}),
   ...(key===geographyFocusKey?{fillOpacity:.95,opacity:1,color:'#10685f',weight:2.5}:{})});
 });
}
function focusMunicipality(key, polygon) {
 if(!$('state').value || byKey.get(key).state !== $('state').value) return;
 const navegacionDemo5 = typeof mapInitialized !== 'undefined' && mapInitialized;
 if(navegacionDemo5){
  // El retroceso sigue niveles territoriales, aunque se visiten varios municipios.
  geographyHistory.length = 0;
  geographyHistory.push({state:$('state').value,search:'',key:null,detailKey:null});
 } else {
  rememberGeographyView();
 }
 const municipality = byKey.get(key);
 if($('search').value !== municipality.name){
  $('search').value = municipality.name;
  update();
 }
 geographyFocusKey = key;
 paintMunicipalityFocus();
 detail(key);
 map.fitBounds(polygon.getBounds(), {padding:[30,30],maxZoom:10,animate:true});
 runtime.hooks.afterFocus();
}
function selectMunicipalityResult(key){
 if(runtime.selectMunicipality)return runtime.selectMunicipality(key);
 const polygon=layer.getLayers().find(p=>p.feature.properties.key===key);
 if(polygon && $('state').value===byKey.get(key)?.state){
  focusMunicipality(key,polygon);
 } else {
  detail(key);
 }
}
function returnToMexico() {
  geographyHistory.length = 0;
  geographyFocusKey = null;
  $('state').value = '';
  $('search').value = '';
  if(typeof activeMapState !== 'undefined') activeMapState = null;
  update();
 map.fitBounds(layer.getBounds(), {padding:[12,12]});
 setTimeout(()=>{ map.invalidateSize(); }, 80);
}
const mapTextSelectors = ["#map-caption", ".map-guide", ".legend", "#confidence-note"];
function reserveGeographyTextSpace() {
 if(!municipalMapText) return;
 const stateText = [
  municipalMapText[0]+' Promedio de municipios con datos por estado.',
  municipalMapText[1],
  municipalMapText[2].replace('Seleccionado</span>', 'Con municipios seleccionados</span>'),
  'La selección del plan se compara entre seis variantes; repetirse no garantiza acierto.'
 ];
 mapTextSelectors.forEach((selector,i)=>{
  const element = document.querySelector(selector), clone = element.cloneNode(false);
  clone.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none;min-height:0;box-sizing:border-box;width:'+element.getBoundingClientRect().width+'px';
  clone.setAttribute('aria-hidden','true');
  element.parentElement.appendChild(clone);
  clone.innerHTML = municipalMapText[i];
  const municipalHeight = clone.getBoundingClientRect().height;
  clone.innerHTML = stateText[i];
  const stateHeight = clone.getBoundingClientRect().height;
  clone.remove();
  element.style.minHeight = Math.ceil(Math.max(municipalHeight,stateHeight))+'px';
 });
}
function initGeography() {
 map.createPane('state-geography');
 map.getPane('state-geography').style.visibility = 'hidden';
 stateLayer = L.geoJSON(window.UMBRAL_STATES, {renderer:createMapRenderer({pane:'state-geography'}),onEachFeature:(feature, polygon)=>{
  polygon.bindTooltip('', {sticky:true});
  polygon.on('click', ()=>{
   rememberGeographyView();
   geographyFocusKey = null;
   $('state').value = feature.properties.state;
   $('search').value = '';
   update();
   map.fitBounds(polygon.getBounds(), {padding:[12,12]});
  });
 }}).addTo(map);  map.on('contextmenu', event=>{
  if(event.originalEvent) L.DomEvent.preventDefault(event.originalEvent);
  goBackGeography();
 });

 let resizeFrame;
 window.addEventListener('resize', ()=>{
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(()=>{
   reserveGeographyTextSpace();
   map.invalidateSize();
   const polygon=geographyFocusKey?layer.getLayers().find(p=>p.feature.properties.key===geographyFocusKey):$('state').value?stateLayer.getLayers().find(p=>p.feature.properties.state===$('state').value):null;
   map.fitBounds(polygon?polygon.getBounds():layer.getBounds(),{padding:[12,12],maxZoom:geographyFocusKey?10:undefined,animate:false});
  });
 });
}
function updateGeography(dataChanged = true) {
  if(typeof mapInitialized!=='undefined' && mapInitialized)return;
  if(typeof historicalMapEnabled !== 'undefined' && historicalMapEnabled && activeMapState) return;
  if(dataChanged){
  stateGeographyDirty = true;   layer.eachLayer(polygon=>{
   const o = polygon.options;
   municipalBaseStyles.set(polygon.feature.properties.key, {color:o.color,weight:o.weight,fillColor:o.fillColor,fillOpacity:o.fillOpacity,opacity:o.opacity});
  });
  paintMunicipalityFocus();
  municipalMapText = mapTextSelectors.map(selector=>document.querySelector(selector).innerHTML);
  reserveGeographyTextSpace();
 }else if(municipalMapText){
  mapTextSelectors.forEach((selector,i)=>{document.querySelector(selector).innerHTML=municipalMapText[i];});
 }
 const statesOn = !$('state').value;
 $('map-title').textContent = statesOn?'Explora los estados':'Explora los municipios';
 $('map').setAttribute('aria-label', statesOn?'Mapa de los estados de México':'Mapa de municipios de México');
 map.getPane('state-geography').style.visibility = statesOn?'visible':'hidden';
 map.getPane('municipal-geography').style.visibility = statesOn?'hidden':'visible';
 if(!statesOn){
  $('confidence').disabled = !simulationActive();
  return;
 }
 // La frecuencia de selección corresponde a municipios, no a entidades.
 $('confidence').disabled = true;
 if(stateGeographyDirty){
 stateSummaries = new Map();
 for(const r of filtered){
  let g = stateSummaries.get(r.state);
  if(!g) stateSummaries.set(r.state, g={name:r.state_name,total:0,valid:0,population:0,weighted:0,additional:0,selected:0});
  g.total++;
  if(!Number.isFinite(r.risk)) continue;
  g.valid++;
  const weight = Number.isFinite(r.observed)&&r.observed>0?r.observed:0;
  g.population += weight;
  g.weighted += r.risk*weight;
  const s = simulationActive()?selectedMap.get(r.key):null;
  if(s){g.selected++;g.additional += s.additional;}
 }
 const mode = $('map-mode').value;
 stateLayer.eachLayer(polygon=>{
  const state = polygon.feature.properties.state, g = stateSummaries.get(state);
  const name = records.find(r=>r.state===state)?.state_name || state;
  const before = g?.population?g.weighted/g.population:null;
  const delta = g?.population?100*g.additional/g.population:0;
  const value = Number.isFinite(before)?before-(mode==='intervencion'?delta:0):null;
  let color = colors[Decision.level(value, thresholds)];
  if(mode==='cambio') color = !Number.isFinite(before)?colors.sin_datos:delta>5?'#135e87':delta>1?'#4b94b8':delta>0?'#9dccdf':'#f6faf9';
  const outsideState = $('state').value && state !== $('state').value;
  polygon.setStyle({color:!outsideState&&$('state').value?'#10685f':g?.selected?'#173c34':'#ffffff',weight:!outsideState&&$('state').value?2.5:g?.selected?2:1,fillColor:color,fillOpacity:outsideState?.12:g?.total?.85:.6,opacity:outsideState?.25:g?.total?1:.75});
  const node = document.createElement('span');
  node.textContent = name+' · '+(mode==='cambio'?(Number.isFinite(before)?delta.toFixed(2)+' pp de reducción':'Sin estimación'):pct(value))+' · '+(g?g.valid+'/'+g.total:0)+' municipios con estimación en el filtro. Pulsa para explorar municipios.';
  polygon.setTooltipContent(node);
 });
 stateGeographyDirty = false;
 }  $('map-caption').textContent += ' Promedio de municipios con estimación por estado.';
 document.querySelector('.legend').innerHTML = document.querySelector('.legend').innerHTML.replace('Seleccionado</span>', 'Con municipios seleccionados</span>');
 $('confidence-note').textContent = 'La selección del plan se compara entre seis variantes; repetirse no garantiza acierto.';
}


/* SOURCE: src/demo6/ui/search.js */
'use strict';
let statePicker, municipalityPicker, pickerState;
function createSearchablePicker(input, menu, toggle, getOptions, choose) {
 let options = [], active = -1;
 const close = ()=>{menu.hidden=true;input.setAttribute('aria-expanded','false');input.removeAttribute('aria-activedescendant');};
 const highlight = ()=>{
  [...menu.children].forEach((node,i)=>{node.setAttribute('aria-selected',i===active?'true':'false');});
  if(active>=0){input.setAttribute('aria-activedescendant',menu.children[active].id);menu.children[active].scrollIntoView({block:'nearest'});}
 };
 const open = (all=false)=>{
  const query = all?'':norm(input.value.trim());
  options=getOptions().filter(option=>norm(option.label+' '+(option.key||'')).includes(query));
  active=-1;
  menu.replaceChildren();
  options.forEach((option,i)=>{
   const node=document.createElement('div');
   node.id=menu.id+'-'+i;node.setAttribute('role','option');node.setAttribute('aria-selected','false');
   node.textContent=option.label;
   node.addEventListener('pointerdown',event=>event.preventDefault());
   node.addEventListener('click',()=>{choose(option);close();input.focus({preventScroll:true});});
   menu.appendChild(node);
  });
  if(!options.length){const empty=document.createElement('p');empty.className='picker-empty';empty.textContent=input.disabled?'Elige primero un estado':'Sin coincidencias';menu.appendChild(empty);}
  menu.hidden=false;input.setAttribute('aria-expanded','true');input.removeAttribute('aria-activedescendant');
 };
 input.addEventListener('input',()=>open());
 input.addEventListener('focus',()=>{input.select();open(true);});
 input.addEventListener('keydown',event=>{
  if(event.key==='Escape'){close();event.preventDefault();}
  if(event.key==='ArrowDown'||event.key==='ArrowUp'){
   event.preventDefault();if(menu.hidden)open(true);
   if(options.length){active=(active+(event.key==='ArrowDown'?1:-1)+options.length)%options.length;highlight();}
  }
  if(event.key==='Enter'&&!menu.hidden&&options.length){event.preventDefault();choose(options[active>=0?active:0]);close();}
 });
 input.addEventListener('blur',close);
 toggle.addEventListener('pointerdown',event=>event.preventDefault());
 toggle.addEventListener('click',()=>{if(input.disabled)return;if(menu.hidden){input.focus({preventScroll:true});input.select();open(true);}else close();});
 document.addEventListener('pointerdown',event=>{if(!input.parentElement.contains(event.target))close();});
 return {close};
}
function initSearchablePickers() {
 statePicker=createSearchablePicker($('state-picker'),$('state-options'),$('state-toggle'),
  ()=>[...$('state').options].map(o=>({key:o.value,label:o.text})),option=>{
   $('state').value=option.key;
   $('search').value='';
   $('state').dispatchEvent(new Event('input',{bubbles:true}));
   $('state').dispatchEvent(new Event('change',{bubbles:true}));
  });
 municipalityPicker=createSearchablePicker($('search'),$('municipality-options'),$('municipality-toggle'),
  ()=>records.filter(r=>r.state===$('state').value).sort((a,b)=>a.name.localeCompare(b.name,'es')).map(r=>({key:r.key,label:r.name})),option=>{
   if(window.Umbral6){window.Umbral6.selectMunicipality(option.key);}
   else { $('search').value=option.label; $('search').dispatchEvent(new Event('input',{bubbles:true})); }
  });
}
function syncSearchablePickers() {
 if(!statePicker)return;
 const state=$('state').value;
 $('state-picker').value=$('state').selectedOptions[0]?.text||'Todo México';
 if(pickerState!==state){
  pickerState=state;
  statePicker.close();municipalityPicker.close();
 }
 $('search').disabled=!state;
 $('municipality-toggle').disabled=!state;
 $('search').placeholder=state?'Escribe o elige un municipio':'Elige primero un estado';
}


/* SOURCE: src/demo6/legacy/scenarios.js */
function preventive(r){
 const p=r.profile,base={responsible:'Área de educación cívica y junta local, responsables propuestos; validar atribuciones y capacidad',resource:'Personas alcanzadas y horas de operación registradas; sin costos monetarios inventados',mechanism:'Hipótesis de reducción de barreras informativas; no efecto causal demostrado'};
 if(!Number.isFinite(r.risk))return {...base,type:'Calidad antes de priorizar',action:'Revisar fuente y antecedentes; no asignar prioridad predictiva',coverage:'Territorio con información insuficiente',conditions:'Resolver NS/antecedentes y verificar comparabilidad',measurement:'Completitud, NS y trazabilidad antes/después de la revisión'};
 if(p.urban_pct<50)return {...base,type:'Cobertura territorial presencial',action:'Sesiones de información electoral accesible en sedes comunitarias verificadas',coverage:'Municipio con menos de 50% de LN urbana; población alcanzada registrada',conditions:'Validar sedes, movilidad, accesibilidad y coordinación local; no inferir barreras solo por ruralidad',measurement:'Personas alcanzadas, cobertura de sedes y conocimiento de requisitos mediante evaluación agregada'};
 if(p.young_pct>=25)return {...base,type:'Información para ciudadanía joven',action:'Talleres sobre requisitos y procedimiento electoral en espacios educativos y comunitarios',coverage:'Municipio con proporción 18–29 ≥25%; atención voluntaria y abierta',conditions:'Verificar espacios y acceso; no asumir desinterés por edad ni seleccionar personas por afinidad',measurement:'Alcance verificable y cambio de conocimiento; participación posterior solo agregada'};
 if(p.older_pct>=25)return {...base,type:'Accesibilidad de información',action:'Material legible y sesiones con canales accesibles',coverage:'Municipio con proporción 60+ ≥25%; oferta abierta',conditions:'Validar necesidades de accesibilidad con usuarios; edad no demuestra una barrera',measurement:'Comprensión de instrucciones, accesibilidad percibida y alcance agregado'};
 return {...base,type:'Información electoral general',action:'Sesiones abiertas y materiales claros sobre cuándo, dónde y cómo votar',coverage:'Población municipal alcanzada según capacidad declarada',conditions:'Verificar pertinencia y canales con el área usuaria antes de implementar',measurement:'Alcance, conocimiento y seguimiento agregado con comparación predefinida'};
}
let rankCache={};
function rankUnder(key,method){const ck=method+'|'+$('lens').value;let hit=rankCache[ck];if(!hit){hit=Decision.rank(filtered.map(x=>({...x,risk:x[method]})),$('lens').value);rankCache[ck]=hit;}return hit.findIndex(x=>x.key===key)+1;}
function clearCaches(){normCache.clear();rankCache={};}
const simulationActive=()=>$('action').value!=='ninguna'&&$('reach').value.trim()!==''&&$('reach').checkValidity();
const smooth=()=>matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth';


/* SOURCE: src/demo6/views/municipality.js */
function perfilCell(key,year,dim,group){try{return perfil.municipios[key][String(year)][dim][group];}catch(e){return null;}}
function perfilRow(key,dim,group,year=2024,minN=500){
 const cell=perfilCell(key,year,dim,group);
 if(!cell||cell.abstencion_pct===null)return `<li>${esc(dim=== 'edad' || dim === 'sexo' || dim === 'seccion' ? (GROUP_NAME[dim]?GROUP_NAME[dim][group]||group:group) : group)}: muestra insuficiente para inferir (n=0)</li>`;
const yearStr=String(year);
let natNac=null;
try{natNac=perfil.nacional[yearStr]&&perfil.nacional[yearStr][dim]&&perfil.nacional[yearStr][dim][group];}catch(e){}
const label=`${GROUP_NAME[dim]?GROUP_NAME[dim][group]||group:group}`;
if(!natNac)return `<li>${esc(label)}: muestra insuficiente para inferir (n=${fmt.format(cell?cell.n:0)})</li>`;
const diff=cell.abstencion_pct-natNac.abstencion_pct,sign=diff>=0?'+':'';
return `<li>${esc(label)}: <strong>${cell.abstencion_pct.toFixed(1)}%</strong> de abstención observada (${sign}${diff.toFixed(1)} pp frente al patrón nacional; n=${fmt.format(cell.n)})</li>`;
}
function detail(key){
activeKey=key;const r=byKey.get(key);
 if(typeof historicalMapEnabled!=='undefined' && historicalMapEnabled && currentMapYear!==2027){
  detailObserved(r,currentMapYear);
  return;
 }
 if(Number.isFinite(r.risk)&&!matches(r)){
  $('detail-name').textContent=r.name;
  $('detail-state').textContent=r.state_name+' · Clave INE '+r.key+' · Estimación disponible pero no coincide con el filtro actual';
  $('detail-content').innerHTML='<div class="missing-message"><strong>Este municipio no coincide con tu filtro actual</strong><p>No aparece en la búsqueda activa por estado, búsqueda o catálogo. Tiene estimación, pero no se incluye en el territorio actual. Cambia la entidad, la búsqueda o el filtro de catálogo para revisarlo.</p></div>';
  return;
 }
 if(!Number.isFinite(r.risk)){
  const p=preventive(r),last=r.history.length?r.history[r.history.length-1]:null;
  $('detail-name').textContent=r.name;
  $('detail-state').textContent=r.state_name+' · Clave INE '+r.key+' · Sin prioridad predictiva';
  $('detail-content').innerHTML=`<div class="missing-message"><strong>Sin estimación para 2027</strong><p>No significa riesgo bajo ni abstención cero. Falta evidencia suficiente con la regla de calidad.</p></div>
   <h3>¿Por qué no se puede estimar?</h3><ul class="why">${(r.exclusion_reasons.length?r.exclusion_reasons:['Revisar disponibilidad y calidad de los antecedentes del método activo.']).map(x=>`<li>${esc(x)}</li>`).join('')}</ul>
   <h3>Qué revisar antes de actuar</h3><p>Comprobar la fuente, completar antecedentes y verificar comparabilidad territorial. No se le asigna puesto en el ranking ni una intervención simulada.</p>
   <h3>Acción propuesta: revisar los datos</h3><p>${esc(p.action)}. Responsable propuesto: ${esc(p.responsible)}.</p>
   <details><summary>Consultar antecedentes disponibles</summary><p>Último proceso: ${last?last.year:'sin antecedente'}. Abstención observada: ${last?pct(last.risk):'Sin tasa calculable'}. Participación no especificada (NS): ${last?pct(last.ns):'Sin dato'}.</p><p>Una tasa histórica disponible no basta para proyectar: se necesitan ambos antecedentes válidos con NS ≤10%.</p></details>`;
  return;
 }
 const ranked=Decision.rank(filtered,$('lens').value),pos=ranked.findIndex(x=>x.key===key)+1,total=ranked.length;
 const s=stability[key]||{count:0,eligible:0,frequency:0,robust:false,members:{}};
 const conf=s.confidence||Decision.confidenceTier(s.count,Decision.variants.length);
 const chosen=selectedMap.get(key);
 const inv=$('action').value==='personalizada'?Decision.inverseScenario(r,chosen?.served||0,Number($('response').value),thresholds):{reason:'La inversión de respuesta solo aplica al escenario personalizado. El efecto del estudio seleccionado permanece fijo; no se ajusta para cambiar el color.'};  const p=preventive(r);
  const refRank=rankUnder(key,'baseline'),ridgeRank=rankUnder(key,$('method').value==='baseline'?'ridge':$('method').value),capacityNow=plan.selected.length;
  const histDemo5 = typeof historicalMapEnabled !== 'undefined' && historicalMapEnabled && currentMapYear !== 2027;
  const yearHist = histDemo5 ? currentMapYear : 2024;
  $('detail-name').textContent=r.name; $('detail-state').textContent=r.state_name+' · Clave INE '+r.key+(simulationActive()?' · Prioridad '+pos+' de '+total:'')+(histDemo5?' · Datos de '+yearHist:'');
 
 const last=r.history.length?r.history[r.history.length-1]:null;
 const reasons=[];
 if(Number.isFinite(r.baseline))reasons.push(`Abstención en la elección comparable (2021): <strong>${pct(r.baseline)}</strong>`);
 if(last&&Number.isFinite(last.risk))reasons.push(`Último proceso (${last.year}): <strong>${pct(last.risk)}</strong>`);
 if(Number.isFinite(r.profile.urban_pct))reasons.push(`Personas registradas en zonas urbanas: ${pct(r.profile.urban_pct)}`);
 if(Number.isFinite(r.latest_ns))reasons.push(`Registros de ${yearHist} sin información sobre si votaron: <strong>${pct(r.latest_ns)}</strong>`);
 const bothHigh=capacityNow>0&&refRank<=capacityNow&&ridgeRank<=capacityNow;
 if(simulationActive())reasons.push(`La referencia de 2021 (puesto ${refRank||'—'}) y la estimación con datos históricos (puesto ${ridgeRank||'—'}): ${bothHigh?'coinciden dentro de la capacidad actual':(refRank<=capacityNow||ridgeRank<=capacityNow)?'solo uno entra en la selección con la capacidad actual':'ninguno entra en la selección con la capacidad actual'}`);
 const mem=s.members||{},any=(vs)=>vs.some(v=>mem[v]);
 const robustez=[
  ['Método comparado (alguna variante)',any(['ridge_5','ridge_10','ridge_20'])],
  ['Referencia (alguna variante)',any(['persistencia_5','persistencia_10','persistencia_20'])],
  ['NS ≤5%',any(['ridge_5','persistencia_5'])],
  ['NS ≤10%',any(['ridge_10','persistencia_10'])],
  ['NS ≤20%',any(['ridge_20','persistencia_20'])],
 ].map(([label,ok])=>`<li>${label}: ${ok?'✅':'—'}</li>`).join('');
 const req=inv.reason?esc(inv.reason):`Para bajar un nivel, objetivo &lt; ${pct(inv.target+1e-6)}: alcance requerido ≈ ${inv.required_reach===null?'imposible con respuesta cero':fmt.format(inv.required_reach)} personas con respuesta ${$('response').value}%. ${inv.feasible_reach?'Cabe en la base observable.':'No cabe en la base observable con esa respuesta.'} Con el alcance actual, respuesta requerida ${pct(inv.required_response)} ${inv.feasible_response?'(≤100%).':'(no factible o sin alcance).'} Requisito algebraico hipotético.`;  const profile=(perfil&&perfil.municipios[key])?`<h3>Perfil CCPC observado ${yearHist} (capa explicativa)</h3><ul class="why">${['18_29','60_mas'].map(g=>perfilRow(key,'edad',g,yearHist)).join('')}${perfilRow(key,'sexo','hombres',yearHist)}${perfilRow(key,'sexo','mujeres',yearHist)}${perfilRow(key,'seccion','urbana',yearHist)}${perfilRow(key,'seccion','rural',yearHist)}</ul><p class="table-note hint">Capa descriptiva posterior: no alimenta a Ridge ni a la prioridad. Las diferencias frente al promedio nacional no son efectos.</p>`:'';
  const detailYear = histDemo5 ? yearHist : 2027;
  const detailLimitText = histDemo5 ? `La cifra de ${yearHist} es observada. No es una proyección.` : `La cifra de 2027 es exploratoria. No sabemos todavía qué tan precisa será; 2024 y 2027 son elecciones de distinto tipo.`;
 $('detail-content').innerHTML=`<div class="detail-comparison"><section><h3>¿Qué ocurrió en elecciones anteriores?</h3><div class="fact-cards">
  <div><span>Dato observado · ${last?last.year:'sin antecedente'}</span><strong>${last?pct(last.risk):'Sin dato'}</strong><small>${last&&Number.isFinite(last.risk)?"Aproximadamente "+Math.round(last.risk)+" de cada 100 personas no votaron":"Sin dato disponible"}</small></div>
  </div></section><section><h3>¿Qué se estima para ${detailYear === 2027 ? '2027' : yearHist}?</h3><div class="fact-cards"><div><span>${histDemo5 ? 'Observado · ' + yearHist : 'Estimación exploratoria · 2027'}</span><strong>${histDemo5 ? pct(r.history.find(h=>h.year===yearHist)?.risk) : pct(r.risk)}</strong><small>${histDemo5 ? 'Abstención observada en ' + yearHist + '.' : 'Aproximadamente ' + Math.round(r.risk) + ' de cada 100 personas podrían no votar. Es una estimación.'}</small></div>
  ${simulationActive()?`<div><span>Con la acción del paso 3</span><strong>${chosen?pct(chosen.after):'Sin asignación'}</strong><small>${chosen?fmt.format(chosen.served)+' personas alcanzadas (supuesto)':'Fuera del plan actual'}</small></div>`:''}</div></section></div><p class="detail-limit">${detailLimitText}</p>
  <details><summary>Antecedentes y calidad de los datos</summary><ul class="why">${reasons.map(x=>`<li>${x}</li>`).join('')}</ul></details>
  ${simulationActive()?`<details><summary>Acción elegida y revisión del plan</summary><h3>Acción del simulador</h3><p>${esc(plan.action.label)}. ${esc(plan.action.unit)}. ${plan.action.source?`<a href="${esc(plan.action.source)}" target="_blank" rel="noopener noreferrer">Fuente original ↗</a>`:"Sin coeficiente externo."}</p>`:''}<details><summary>Qué actividad podría explorarse en este municipio</summary><h3>Recomendación preventiva por validar</h3><p><strong>Acción sugerida: ${esc(p.type)}.</strong> ${esc(p.action)}.</p><p class="hint">Propuesta por validar con la comunidad. ${esc(p.mechanism)}.</p>
  </details>${simulationActive()?`<h3>¿Qué debemos comprobar antes de aplicarla?</h3><p>Este municipio aparece entre los seleccionados en <strong>${s.count} de las 6 formas de comparar los datos</strong>. ${s.robust?'Seleccionado en todas las variantes.':s.count>0?'La selección depende del método o de la calidad.':'No entra en las variantes con la capacidad actual.'} Tiene datos suficientes para ${s.eligible} de esas 6 comparaciones. </p>
  ${r.exclusion_reasons.length?`<div class="evidence-note">${r.exclusion_reasons.map(esc).join('<br>')}</div>`:''}
  <p>${esc(p.conditions)}.</p></details>`:''}
  <details><summary>Consultar el perfil observado por grupos</summary>${profile||'<p>Sin perfil desagregado disponible.</p>'}</details>
  <details><summary>Responsable, cobertura, recurso y evaluación</summary><dl class="prevention">${Object.entries({Responsable:p.responsible,Cobertura:p.coverage,Recurso:p.resource,'Cómo evaluarla':p.measurement}).map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details>
  ${simulationActive()?`<details><summary>Avanzado: qué haría falta para cambiar de color</summary><p>${req}</p></details>`:''}
  ${simulationActive()?`<details><summary>Cómo cambia la selección entre variantes</summary><ul class="why">${robustez}</ul><p>Frecuencia de selección ${s.count}/6. Se usa un número equivalente de municipios; no se recalcula el presupuesto humano por variante.</p></details>`:''}
  <details><summary>Ver elecciones anteriores y límites de la estimación</summary><div class="history">${r.history.map(h=>`<div><span>${h.year}</span><div class="bar-track"><i style="width:${Number.isFinite(h.risk)?h.risk:0}%"></i></div><b>${pct(h.risk)}</b></div>`).join('')}</div><p>${simulationActive()?'La prioridad se comunica con la frecuencia entre variantes. ':''}El rango técnico ${pct(Math.max(0,r.risk-UmbralAnalytics.historicalError(metadata,$('method').value)))}–${pct(Math.min(100,r.risk+UmbralAnalytics.historicalError(metadata,$('method').value)))} (±${UmbralAnalytics.historicalError(metadata,$('method').value).toFixed(2)} pp, p90 retrospectivo de ${UmbralAnalytics.methodName($('method').value)} en 2021) se conserva solo aquí como referencia de error histórico; no es intervalo prospectivo.</p><p>${r.flags.map(esc).join('; ')||'Sin alertas adicionales'}</p></details>`;
}
function detailObserved(r,year){
 const observed=r.history.find(h=>h.year===year);
 const rate=observed?.risk;
 $('detail-name').textContent=r.name;
 $('detail-state').textContent=r.state_name+' · Clave INE '+r.key+' · Elección de '+year;
 const groups=['edad','sexo','seccion'].flatMap(dim=>{
  const available=perfil?.municipios?.[r.key]?.[String(year)]?.[dim];
  return available ? Object.keys(available).map(group=>perfilRow(r.key,dim,group,year)) : [];
 });
 $('detail-content').innerHTML=`<h3>¿Cómo fue la abstención en ${year}?</h3>
  <div class="fact-cards"><div><span>Abstención observada · ${year}</span><strong>${pct(rate)}</strong><small>${Number.isFinite(rate)?'Aproximadamente '+Math.round(rate)+' de cada 100 personas no votaron.':'No hay una tasa observada disponible para este municipio en el año seleccionado.'}</small></div>
  ${Number.isFinite(rate)?`<div><span>Participación observada · ${year}</span><strong>${pct(100-rate)}</strong><small>Sobre las personas con información de voto (SV + NV).</small></div>`:''}</div>
  <p class="detail-limit">Resultados históricos de ${year} a partir de los CCPC del INE.</p>
  <details><summary>Calidad de los datos de ${year}</summary><p>Participación no especificada (NS): <strong>${pct(observed?.ns)}</strong>.</p><p>Una tasa histórica disponible se muestra aunque no haya evidencia suficiente para estimar 2027. Las claves y los límites municipales no están armonizados entre elecciones.</p></details>
  <details><summary>Perfil observado por grupos en ${year}</summary>${groups.length?'<ul class="why">'+groups.join('')+'</ul>':'<p>No hay un perfil desagregado disponible para este año.</p>'}</details>
  <details><summary>Comparar elecciones anteriores</summary><div class="history">${r.history.filter(h=>h.year<=year).map(h=>`<div><span>${h.year}</span><div class="bar-track"><i style="width:${Number.isFinite(h.risk)?h.risk:0}%"></i></div><b>${pct(h.risk)}</b></div>`).join('')}</div></details>`;
}


/* SOURCE: src/demo6/legacy/scenario-controls.js */
function simulationMunicipalities(){
 const previous=$('simulation-municipality').value;
 $('simulation-municipality').replaceChildren();
 for(const r of records.filter(r=>r.state===$('simulation-state').value).sort((a,b)=>a.name.localeCompare(b.name,'es')))$('simulation-municipality').add(new Option(r.name+' · '+r.key,r.key));
 if([...$('simulation-municipality').options].some(o=>o.value===previous))$('simulation-municipality').value=previous;
}
function applySimulationScope(){
 const scope=$('simulation-scope').value;
 $('simulation-state-wrap').hidden=scope==='pais';
 $('simulation-municipality-wrap').hidden=scope!=='municipio';
 $('state').value=scope==='pais'?'':$('simulation-state').value;
 const row=records.find(r=>r.key===$('simulation-municipality').value);
 $('search').value=scope==='municipio'&&row?row.key:'';
 geographyFocusKey=null;geographyHistory.length=0;
 update();
 runtime.hooks.afterScope();
}
function syncSimulationTerritory(){
 const state=$('state').value;
 const exact=state?records.find(r=>r.state===state&&(r.key===$('search').value||r.name===$('search').value)):null;
 if(state&&$('simulation-state').value!==state){$('simulation-state').value=state;simulationMunicipalities();}
 $('simulation-scope').value=exact?'municipio':state?'estado':'pais';
 if(exact)$('simulation-municipality').value=exact.key;
 $('simulation-state-wrap').hidden=!state;
 $('simulation-municipality-wrap').hidden=!exact;
}
// Actualizar resultados de exploración sin repintar ni reencuadrar el mapa histórico.


/* SOURCE: src/demo6/app/exploration.js */
function renderExplorationAnalysis(){
 syncSearchablePickers();
 syncSimulationTerritory();
 clearCaches();
 const method=$('method').value;
 view=viewCache[method]||(viewCache[method]=records.map(r=>({...r,risk:r[method]})));
 byKey=new Map(view.map(r=>[r.key,r]));
 filtered=view.filter(matches);
 thresholds=thresholdsCache[method]||(thresholdsCache[method]=(()=>{
  const rates=view.map(r=>r.risk).filter(Number.isFinite);
  return {low:quantile(rates,1/3),high:quantile(rates,2/3)};
 })());
 const observedMode=typeof historicalMapEnabled!=='undefined' && historicalMapEnabled && currentMapYear!==2027;
 const rate=r=>observedMode?r.history.find(h=>h.year===currentMapYear)?.risk:r.risk;
 const eligible=filtered.filter(r=>Number.isFinite(rate(r)));
 const missing=filtered.filter(r=>!Number.isFinite(rate(r)));
 $('analysis-eligible-label').textContent=observedMode?'Con dato observado en '+currentMapYear:'Con estimación en tu búsqueda';
 $('analysis-missing-label').textContent=observedMode?'Sin dato observado en '+currentMapYear:'Sin estimación en tu búsqueda';
 $('analysis-ranking-label').textContent=observedMode?'No votaron en '+currentMapYear:'Podrían no votar en 2027';
 $('analysis-missing-title').textContent=observedMode?'Municipios sin dato observado en '+currentMapYear:'¿Por qué algunos municipios no tienen estimación?';
 $('analysis-missing-note').textContent=observedMode?'El color gris indica que no hay una tasa observada disponible en el año seleccionado. Un dato ausente no equivale a 0% de abstención.':'El color gris indica que no hay evidencia histórica suficiente o la participación no especificada supera el 10%, según la regla de calidad metodológica.';
 $('analysis-description').textContent=observedMode?'Consulta los resultados observados de '+currentMapYear+', la participación y la calidad de los datos del municipio seleccionado.':'Consulta la ficha del municipio, el ranking y la calidad de la estimación. Ridge se contrasta con la referencia de la elección previa; 2021 selecciona el método y 2024 revisa su transferencia.';
 $('eligible').textContent=fmt.format(eligible.length);
 $('coverage').textContent='De '+fmt.format(filtered.length)+' municipios que coinciden con tus filtros';
 $('filter-summary').textContent=fmt.format(filtered.length)+' municipios incluidos.'+($('stable').checked?' Filtro activo: catálogo municipal constante.':'');
 $('show-all').hidden=!$('stable').checked;
 $('missing-count').textContent=fmt.format(missing.length);
 $('list-count').textContent=fmt.format(eligible.length)+(observedMode?' con dato observado':' con estimación');
 const ranked=observedMode?eligible.slice().sort((a,b)=>rate(b)-rate(a)||a.key.localeCompare(b.key)):Decision.rank(eligible,'tasa');
 $('ranking').innerHTML=ranked.slice(0,25).map(r=>`<tr><td><button type="button" data-key="${r.key}" class="row-button">${esc(r.name)}</button><small>${esc(r.state_name)} · ${r.key}</small></td><td>${pct(rate(r))}</td></tr>`).join('')||'<tr><td colspan="2">No hay datos disponibles en esta búsqueda.</td></tr>';
 $('missing-list').innerHTML=missing.slice(0,12).map(r=>`<button class="missing-row" type="button" data-key="${r.key}"><strong>${esc(r.name)}</strong><span>${esc(r.state_name)} · ${r.key}</span><small>${esc(observedMode?'Sin tasa observada para '+currentMapYear:r.exclusion_reasons[0]||'Revisar antecedentes y calidad')}</small></button>`).join('')||'<p>No hay municipios sin datos en este filtro.</p>';
 if(activeKey&&!filtered.some(r=>r.key===activeKey))activeKey=null;
 if(!activeKey&&filtered.length===1)activeKey=filtered[0].key;
 if(activeKey)detail(activeKey);
 else{
  $('detail-name').textContent='Selecciona un municipio';
  $('detail-state').textContent='Elige tu estado y municipio o abre uno en el mapa para consultar sus datos.';
  $('detail-content').innerHTML='';
 }
}

function updateExplorationAnalysis(){
  try{return renderExplorationAnalysis();}
  finally{runtime.hooks.afterExplore();}
}


/* SOURCE: src/demo6/app/render.js */
function renderApplication(){
  syncSearchablePickers();
 syncSimulationTerritory();
 clearCaches();
 const reach=Number($('reach').value),response=Number($('response').value),lens=$('lens').value,method=$('method').value,minConf=$('min-confidence').value;
 $('response-out').textContent=response+'%';
 view=viewCache[method]||(viewCache[method]=records.map(r=>({...r,risk:r[method]})));byKey=new Map(view.map(r=>[r.key,r]));filtered=view.filter(matches);if($('simulation-scope').value==='municipio')filtered=filtered.filter(r=>r.key===$('simulation-municipality').value);
 thresholds=thresholdsCache[method]||(thresholdsCache[method]=(()=>{const rates=view.map(r=>r.risk).filter(Number.isFinite);return {low:quantile(rates,1/3),high:quantile(rates,2/3)};})());
 const action=Decision.interventions[$('action').value],simOn=action.id!=='ninguna';
 const budgetValid=$('reach').value.trim()!==''&&$('reach').checkValidity();
 const hasResults=simOn&&budgetValid;
 $('reach').setAttribute('aria-invalid',simOn&&!budgetValid?'true':'false');
 $('simulation-inputs').hidden=!simOn;$('simulation-results').hidden=!hasResults;
 $('simulation-empty').hidden=hasResults;$('simulation-prompt').hidden=hasResults;
 $('simulation-prompt').textContent=simOn&&!budgetValid?'Introduce un número entero de personas entre 0 y 100,000,000 para calcular el escenario.':'Elige una acción para configurar la cobertura y comparar los resultados.';
 $('simulation-empty').querySelector('h3').textContent=simOn&&!budgetValid?'Revisa la cobertura':'¿Qué podría cambiar?';
 $('simulation-empty').querySelector('p').textContent=simOn&&!budgetValid?'Los resultados están pendientes hasta corregir el número de personas. Puedes seguir consultando el mapa y las fichas.':'Los resultados aparecerán al elegir una acción. Puedes seguir consultando municipios sin configurar este paso.';
 $('simulation-map-controls').hidden=!hasResults;
 $('confidence-note').hidden=!hasResults;
 if(!hasResults){$('map-mode').value='base';$('confidence').checked=false;}
 for(const option of $('map-mode').options)option.disabled=!hasResults&&option.value!=='base';
 renderActionEvidence(action);
 const select=pool=>Decision.planIntervention(pool,{capacity:1,budget:budgetValid?reach:0,reach:budgetValid?reach:0,response,lens,action:action.id,distribution:$('distribution').value});
 try{
  let pool=filtered;
  if(minConf!=='todas'){const probe=select(pool),stab0=Decision.selectionStability(filtered,probe.selected.length,lens);const min=minConf==='alta'?5/6:3/6;pool=filtered.filter(r=>{const s=stab0[r.key];return s&&s.frequency>=min;});}
  plan=select(pool);
 }catch(e){$('effect-range').textContent='';$('status').textContent='Corrige el alcance o las personas (valores válidos); resultados pendientes.';$('scenario-assumptions').textContent='Corrige los valores para volver a comparar los escenarios.';$('export').disabled=true;for(const id of ['eligible','coverage','selected','additional','served','before','after','reduction','missing-count','list-count','agreement'])$(id).textContent='—';$('ranking').innerHTML='<tr><td colspan="4">Corrige los parámetros para recalcular.</td></tr>';$('entity-table').innerHTML='';$('plan-summary').innerHTML='';$('frontier-table').innerHTML='';$('frontier-summary').textContent='—';$('pilot-note').textContent='';$('detail-content').innerHTML='';$('map').style.visibility='hidden';return;}
 stability=Decision.selectionStability(filtered,plan.selected.length,lens);
 $('map').style.visibility='visible';selectedMap=new Map(plan.selected.map(r=>[r.key,r]));
 const n=plan.selected.length;frontier=Decision.decisionFrontier(filtered,n,lens,stability);
 const territory=Decision.territorialScenario(filtered,plan);
 const scope=$('simulation-scope').value,scopeName=scope==='pais'?'México: municipios con estimación incluidos':scope==='estado'?$('simulation-state').selectedOptions[0]?.text:$('simulation-municipality').selectedOptions[0]?.text;
 const universe=view.filter(r=>scope==='pais'||(r.state===$('simulation-state').value&&(scope!=='municipio'||r.key===$('simulation-municipality').value)));
 $('scope-coverage').textContent=`Cobertura de datos: ${territory.municipalities} de ${universe.length} municipios del territorio con estimación incluidos. ${filtered.filter(r=>!Number.isFinite(r.risk)).length} sin estimación dentro del filtro; ${universe.length-filtered.length} fuera de los filtros activos. El promedio no representa los territorios excluidos.`;
 $('distribution-help').textContent=plan.distribution==='proporcional'?'Reparte según las personas con registro de voto en 2024. El redondeo por mayor resto conserva el total de personas; no garantiza mayor impacto.':'Atiende primero al municipio con mayor prioridad y después al siguiente. Puede concentrar toda la cobertura en uno solo; no garantiza mayor impacto.';
 $('scenario-assumptions').textContent=`Territorio: ${scopeName}. ${territory.municipalities} municipios con estimación, ${n} atendidos. Cobertura total: ${fmt.format(plan.served)} de ${fmt.format(reach)} personas previstas, Distribución: ${plan.distribution==='proporcional'?'proporcional a SV+NV 2024':'focalizada por prioridad'}. Acción: ${action.label}. ${action.id==='personalizada'?`Respuesta supuesta: ${response}%.`:`Efecto de referencia: ${action.effect_pp} pp (${action.estimand}).`} Base territorial observable: ${fmt.format(territory.population)} personas. Excluye municipios sin estimación y territorios fuera del filtro de catálogo activo. Transferencia hipotética a México.`;
 $('effect-range').textContent=plan.additional_low!==null?`Rango trasladado del estudio: ${plan.additional_low.toFixed(2)}–${plan.additional_high.toFixed(2)} votos adicionales; reducción territorial ${territory.population?(100*plan.additional_low/territory.population).toFixed(5):'0'}–${territory.population?(100*plan.additional_high/territory.population).toFixed(5):'0'} pp. No es un intervalo validado para México.`:action.id==='ninguna'?'Sin acción: la estimación base se conserva.':action.id==='personalizada'?'Sin intervalo de evidencia: efecto supuesto por el usuario.':action.uncertainty;

 const topRate=Decision.rank(filtered,'tasa').slice(0,n),topVol=Decision.rank(filtered,'volumen').slice(0,n),topChange=Decision.rank(filtered,'deterioro').slice(0,n);
 $('agreement').textContent=`Solapamiento con la lista por tasa: volumen ${Decision.overlap(topRate,topVol)}/${topRate.length}; deterioro ${Decision.overlap(topRate,topChange)}/${topRate.length}.`;
 $('status').textContent='';
 $('eligible').textContent=fmt.format(filtered.filter(r=>Number.isFinite(r.risk)).length);$('coverage').textContent='De '+fmt.format(filtered.length)+' municipios que coinciden con tus filtros';
 const territoryCount=view.filter(r=>(!$('state').value||r.state===$('state').value)&&norm2(r.name+' '+r.key).includes(norm2($('search').value.trim()))).length;
 $('filter-summary').textContent=$('stable').checked?`${fmt.format(filtered.length)} de ${fmt.format(territoryCount)} municipios incluidos. Filtro activo: solo estados cuyo listado municipal no cambió.`:`${fmt.format(filtered.length)} municipios incluidos. Se incluyen estados con y sin cambios en su listado municipal.`;
 $('show-all').hidden=!$('stable').checked;
 const missing=filtered.filter(r=>!Number.isFinite(r.risk));$('missing-count').textContent=fmt.format(missing.length);
 $('missing-list').innerHTML=missing.slice(0,12).map(r=>`<button class="missing-row" type="button" data-key="${r.key}"><strong>${esc(r.name)}</strong><span>${esc(r.state_name)} · ${r.key}</span><small>${esc(r.exclusion_reasons[0]||'Revisar antecedentes y calidad')}</small></button>`).join('')||'<p>No hay municipios sin estimación en este filtro.</p>';
 $('selected').textContent=n;$('additional').textContent='≈ '+(plan.additional>0&&plan.additional<1?plan.additional.toFixed(2):fmt.format(plan.additional));$('served').textContent=fmt.format(plan.served)+' · '+action.unit;
 $('before').textContent=territory.population?territory.before.toFixed(2)+'%':'Sin estimación';$('after').textContent=territory.population?territory.after.toFixed(2)+'%':'Sin estimación';$('export').disabled=!n||!hasResults;$('list-count').textContent=fmt.format(filtered.filter(r=>Number.isFinite(r.risk)).length)+' con estimación';
 const change=territory.before-territory.after,smallChange=change>0&&change<.01;
 $('reduction').textContent=territory.population?(smallChange?'Menos de 0.01':change.toFixed(2)):'Sin estimación';
 $('reduction').classList.toggle('small-change',smallChange);
 $('rounding-note').hidden=!(change>0&&territory.before.toFixed(2)===territory.after.toFixed(2));
 $('rounding-note').textContent='El cambio es pequeño: ambas tasas se ven iguales al redondear a dos decimales. Consulta las cifras completas en los supuestos del cálculo.';
 $('precise-results').textContent=territory.population?`Cifras completas: sin acción ${territory.before.toFixed(5)}%; con acción ${territory.after.toFixed(5)}%; reducción ${change.toFixed(5)} puntos porcentuales.`:'Sin población con estimación para comparar.';
 const robust=plan.selected.filter(r=>stability[r.key]&&stability[r.key].robust).length,review=n-robust,entityCount=new Set(plan.selected.map(r=>r.state)).size;
 $('plan-summary').innerHTML=[['Municipios',fmt.format(n)],['Entidades',fmt.format(entityCount)],['Base observable SV+NV 2024',fmt.format(plan.reference_population)],['Prioridad núcleo robusto',fmt.format(robust)],['Requieren revisión',fmt.format(review)],['Personas alcanzadas (supuesto)',fmt.format(plan.served)],['Base de municipios atendidos',n?pct(plan.before):'—'],['Escenario de municipios atendidos',n?pct(plan.after):'—']].map(([k,v])=>`<div><span>${k}</span><strong>${v}</strong></div>`).join('');
 const nuc=frontier.nucleo.length,fro=frontier.frontera.length;
 $('frontier-summary').innerHTML=`<strong>Núcleo robusto:</strong> ${fmt.format(nuc)} municipios entran en la selección bajo las 6/6 variantes. <strong>Frontera de decisión:</strong> ${fmt.format(fro)} cambian según método, calidad o criterio. <strong>Fuera:</strong> ${fmt.format(frontier.fuera.length)} nunca entran con esta capacidad.`;
 $('frontier-table').innerHTML=[['Núcleo robusto (6/6)',nuc,'#1'],['Frontera de decisión (1/6–5/6)',fro,'depende'],['Fuera de la selección',frontier.fuera.length,'—']].map(([k,v,tag])=>`<div><span>${k}</span><strong>${fmt.format(v)}</strong><small>${tag}</small></div>`).join('');
 $('pilot-note').textContent=fro>0?`Si solo existen recursos para atender una fracción de la frontera (por ejemplo, 12 de ${fmt.format(fro)} municipios), una asignación aleatoria dentro de esa zona —con balance por entidad, tamaño, calidad y contexto— permitiría construir un piloto evaluable. La cercanía del score no acredita equivalencia.`:'Con la capacidad actual no hay una zona de frontera: la selección es estable bajo las variantes o el filtro la vació.';
 $('ranking').innerHTML=Decision.rank(filtered,'tasa').slice(0,25).map(r=>`<tr><td><button type="button" data-key="${r.key}" class="row-button">${esc(r.name)}</button><small>${esc(r.state_name)} · ${r.key}</small></td><td>${pct(r.risk)}</td></tr>`).join('')||'<tr><td colspan="2">No hay municipios con estimación en esta búsqueda. Puedes consultar los municipios grises del mapa.</td></tr>';
 if(!$('state').value)$('confidence').checked=false;
 const mode=$('map-mode').value;
 const legend=$('confidence').checked?'<span><i style="background:#176b58"></i>Núcleo 6/6</span><span><i style="background:#ddb263"></i>Revisión</span>':mode==='cambio'?'<span><i style="background:#f6faf9;border:1px solid #ddd"></i>0 pp</span><span><i style="background:#9dccdf"></i>0–1 pp</span><span><i style="background:#4b94b8"></i>1–5 pp</span><span><i style="background:#135e87"></i>&gt;5 pp</span>':'<span><i class="low"></i>Menor abstención</span><span><i class="medium"></i>Intermedia</span><span><i class="high"></i>Mayor abstención</span>';
 document.querySelector('.legend').innerHTML=legend+'<span><i class="missing"></i>Sin estimación</span>'+(hasResults?'<span><i class="chosen"></i>Seleccionado</span>':'')+'<span>Atenuado: fuera del filtro</span>';
 $('map-caption').textContent=$('confidence').checked?'Veces que un municipio aparece entre los seleccionados: verde = 6 de 6 comparaciones; ámbar = menos de 6.':mode==='cambio'?'Reducción simulada: blanco = sin reducción; azul más oscuro = mayor reducción.':`Porcentaje de personas que ${mode==='intervencion'?'no votarían con la acción elegida':'podrían no votar en 2027'}. Gris = sin estimación válida.'`;
 document.querySelector('.map-guide').textContent=$('confidence').checked?'Repetirse en las seis comparaciones no garantiza que la estimación sea correcta. Ámbar incluye municipios que nunca entran en la selección. Gris = sin estimación.':mode==='cambio'?'El cambio se expresa en puntos porcentuales: bajar de 60% a 58% equivale a 2 puntos. Solo los municipios incluidos en la simulación pueden mostrar una reducción. Gris = sin estimación.':'Los colores comparan la abstención estimada. Gris: datos insuficientes. Atenuado: fuera de tu filtro.';
 $('map-reading-text').textContent=`Menor abstención: menos de ${thresholds.low.toFixed(1)}%; mayor: desde ${thresholds.high.toFixed(1)}%. Los límites de color se mantienen al cambiar de escenario. El promedio estatal se pondera por las personas con registro de voto en 2024 (SV+NV); los municipios sin estimación quedan fuera y no cuentan como cero. La cobertura puede ser parcial. La cartografía está simplificada y sirve como referencia visual. Los colores no califican a los habitantes.`;
 $('confidence-note').textContent=$('confidence').checked?'Vista estabilidad: verde = seleccionado en 6/6 variantes; ámbar = revisión; gris = sin estimación. Frecuencia descriptiva; las variantes pueden equivocarse juntas.':'Vista riesgo/cambio. La estabilidad de selección se informa como dimensión separada en lista y ficha.';
 const groups=new Map();for(const r of filtered){let g=groups.get(r.state);if(!g)groups.set(r.state,g=[]);g.push(r);}
 const selByState=new Map();for(const r of plan.selected){let g=selByState.get(r.state);if(!g)selByState.set(r.state,g=[]);g.push(r);}
 const states=[...groups.keys()].sort();
 $('entity-table').innerHTML=states.map(state=>{const all=groups.get(state),valid=all.filter(r=>Number.isFinite(r.risk)),sel=selByState.get(state)||[],obs=valid.reduce((a,r)=>a+r.observed,0),before=obs?valid.reduce((a,r)=>a+r.risk*r.observed,0)/obs:null,add=sel.reduce((a,r)=>a+r.additional,0);return `<tr><td>${esc(all[0].state_name)}</td><td>${valid.length}/${all.length}</td><td>${sel.length}</td><td>${pct(before)}</td><td>${pct(obs?before-100*add/obs:null)}</td><td>${fmt.format(sel.reduce((a,r)=>a+r.served,0))}</td></tr>`;}).join('');
 updateGeography();
 if(activeKey&&!filtered.some(r=>r.key===activeKey))activeKey=null;
 if(!activeKey&&filtered.length===1)activeKey=filtered[0].key;
 if(activeKey)detail(activeKey);
 else{$('detail-name').textContent='Selecciona un municipio';$('detail-state').textContent='Elige tu estado y municipio o abre uno en el mapa para consultar sus datos.';$('detail-content').innerHTML='';}
}

function update(){
  runtime.hooks.beforeUpdate();
  try{return renderApplication();}
  finally{runtime.hooks.afterUpdate();}
}


/* SOURCE: src/demo6/legacy/scenario-export.js */
function exportPlan(){
 const LENS_LABEL={tasa:'Mayor porcentaje',volumen:'Mayor volumen',deterioro:'Mayor deterioro'},METHOD_LABEL={ensamble:'Ensamble adaptativo (+8.2% precisión)',ridge:'Ridge',hgb:'HistGradientBoosting',lightgbm:'LightGBM',catboost:'CatBoost',baseline:'Referencia: elección de 2021'};
 const headers=['Puesto','Clave INE','Entidad','Municipio','No votarían (estimado 2027, %)','No votarían (con acción, %)','Reducción (pp)','Personas alcanzadas (supuesto)','Respuesta supuesta (%)','Personas adicionales que votarían (supuesto)','Base observable 2024 (SV+NV)','Lista nominal 2024','Sin dato de voto (%)','Confianza de prioridad','Aparece en variantes (de 6)','Variantes con datos (de 6)','Núcleo robusto (6/6)','Catálogo constante','Criterio de prioridad','Tipo de acción','Acción propuesta','Responsable propuesto','Condiciones de validación','Recursos','Cómo evaluarla','Nota metodológica','Acción simulada','Estimador del estudio','Unidad de cobertura','Efecto de referencia (pp)','Fuente bibliográfica','URL fuente','Incertidumbre del estudio','Votos adicionales límite inferior','Votos adicionales límite superior','Distribución de cobertura'];
 const titleCase=v=>String(v).toLowerCase().replace(/(^|[\s\-])([a-záéíóúüñ])/g,(m,p,c)=>p+c.toUpperCase()),num=v=>Number.isFinite(v)?String(Math.round(v)):'',dec=v=>Number.isFinite(v)?v.toFixed(4):'',bool=v=>v?'Sí':'No';
 const ranked=Decision.rank(filtered,$('lens').value),response=Number($('response').value),action=plan.action;
 const lines=plan.selected.map((r,i)=>{const s=stability[r.key]||{count:0,eligible:0,robust:false},c=s.confidence||Decision.confidenceTier(s.count,6),p=preventive(r);return [i+1,r.key,titleCase(r.state_name),titleCase(r.name),dec(r.risk),dec(r.after),dec(r.risk-r.after),num(r.served),action.id==='personalizada'?response:'',r.additional.toFixed(4),num(r.observed),num(r.ln),dec(r.latest_ns),TIER[c.tier],s.count,s.eligible,bool(s.robust),bool(r.stable_catalog_state),LENS_LABEL[$('lens').value],p.type,p.action,p.responsible,p.conditions,p.resource,p.measurement,'Hipótesis no causal; la frecuencia no es probabilidad; base observable histórica (SV+NV 2024), sin NS; límites sin armonizar',action.label,action.estimand,action.unit,action.effect_pp??'',action.citation||'Sin fuente causal: supuesto del usuario',action.source||'',action.uncertainty||'No disponible',r.additional_low??'',r.additional_high??'',plan.distribution];});
 const cell=v=>{let s=String(v??'');if(typeof v==='string'&&/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
 const dic={'Puesto':'Orden en la prioridad del plan actual','Clave INE':'Clave de municipio del catálogo INE','Entidad':'Estado','Municipio':'Nombre del municipio','No votarían (estimado 2027, %)':'Estimación exploratoria del método activo','No votarían (con acción, %)':'Escenario hipotético tras la acción simulada','Reducción (pp)':'Estimación menos escenario, en puntos porcentuales','Personas alcanzadas (supuesto)':'Contacto simulado, limitado por la base observable','Respuesta supuesta (%)':'Cambio de decisión supuesto entre alcanzados que no votarían','Personas adicionales que votarían (supuesto)':'Evidencia: cobertura por efecto pp/100, limitada por abstención esperada cubierta. Personalizado: cobertura por tasa por respuesta. Transferencia hipotética.','Base observable 2024 (SV+NV)':'Personas con registro de si votaron en 2024; denominador y tope de alcance','Lista nominal 2024':'Lista nominal electoral 2024','Sin dato de voto (%)':'Participación no especificada (NS) en 2024','Confianza de prioridad':'Frecuencia de selección entre seis variantes, agrupada','Aparece en variantes (de 6)':'Variantes que lo seleccionan','Variantes con datos (de 6)':'Variantes con datos suficientes para evaluarlo','Núcleo robusto (6/6)':'Seleccionado en las seis variantes','Catálogo constante':'Estado con listado municipal sin cambios entre cortes','Criterio de prioridad':'Lente activa al exportar','Tipo de acción':'Tipología preventiva sugerida por perfil municipal','Acción propuesta':'Actividad concreta para validar con el área usuaria','Responsable propuesto':'Instancia propuesta; validar atribuciones y capacidad','Condiciones de validación':'Qué comprobar antes de implementar','Recursos':'Recursos registrables; sin costos inventados','Cómo evaluarla':'Métricas de seguimiento sugeridas','Nota metodológica':'Límites que aplican a toda la tabla'};
 Object.assign(dic,{'Distribución de cobertura':'Regla propia del proyecto: prioridad por ranking o proporcional a SV+NV 2024 con mayor resto','Acción simulada':'Acción elegida en el simulador; distinta de la recomendación preventiva por perfil','Estimador del estudio':'ITT sobre asignados o ATT ajustado por contacto; supuesto en personalizado','Unidad de cobertura':'Denominador correspondiente al estimador','Efecto de referencia (pp)':'Aumento publicado de participación; no respuesta entre abstencionistas','Fuente bibliográfica':'Publicación original del coeficiente','URL fuente':'Enlace DOI a la publicación','Incertidumbre del estudio':'Intervalo o error estándar original; no incertidumbre de transferencia','Votos adicionales límite inferior':'Cobertura por límite inferior publicado; vacío si no disponible','Votos adicionales límite superior':'Cobertura por límite superior publicado; vacío si no disponible'});
 const territorial=Decision.territorialScenario(filtered,plan);
 const leeme=[['Distribución','Regla',plan.distribution],['Distribución','Criterio','Prioridad concentra por ranking; proporcional reparte por SV+NV 2024 con mayor resto y desempate por clave. Reglas propias de planeación, no hallazgos causales.'],['Territorio','Escala',$('simulation-scope').value],['Territorio','Estado',$('simulation-scope').value==='pais'?'Todo México':$('simulation-state').selectedOptions[0]?.text],['Territorio','Municipio',$('simulation-scope').value==='municipio'?$('simulation-municipality').selectedOptions[0]?.text:'Todos en el filtro'],['Territorio','Cobertura total prevista',Number($('reach').value)],['Territorio','Base observable del territorio',territorial.population],['Territorio','Abstención territorial sin acción',territorial.before],['Territorio','Abstención territorial con acción',territorial.after],['Territorio','Reducción territorial (pp)',territorial.before-territorial.after],['Documento','Qué es','Plan de priorización municipal de la demo local de Umbral (aguas.exe · Reto 2 INE). Acompaña a Umbral_plan_municipios.csv: una fila por municipio seleccionado.'],['Documento','Fecha de generación',new Date().toLocaleString('es-MX')],['Documento','Nota central','Las cifras de 2027 son estimaciones exploratorias, no resultados; la acción simulada es una hipótesis, no un efecto medido.'],['Filtros aplicados','Entidad',$('state').selectedOptions[0]?.text||'Todo México'],['Filtros aplicados','Búsqueda',$('search').value.trim()||'(sin búsqueda)'],['Filtros aplicados','Solo catálogo constante',bool($('stable').checked)],['Filtros aplicados','Método de estimación',METHOD_LABEL[$('method').value]],['Filtros aplicados','Criterio de prioridad',LENS_LABEL[$('lens').value]],['Filtros aplicados','Estabilidad mínima exigida',$('min-confidence').selectedOptions[0]?.text||'Todas'],['Simulación','Modo de capacidad','Cobertura total de personas en el territorio elegido'],['Simulación','Capacidad declarada',fmt.format(Number($('reach').value))+' personas en total'],['Simulación','Cobertura total prevista',fmt.format(Number($('reach').value))+' personas'],['Simulación','Respuesta supuesta',action.id==='personalizada'?response+'% de quienes no votarían':'No aplica al efecto en pp del estudio'],['Evidencia','Acción simulada',action.label],['Evidencia','Estimador y unidad',action.estimand+'; '+action.unit],['Evidencia','Efecto (pp)',action.effect_pp??'Supuesto del usuario'],['Evidencia','Fuente',action.citation||'Sin fuente causal'],['Evidencia','URL',action.source||''],['Evidencia','Localización',action.locator||'No aplica'],['Evidencia','Incertidumbre',action.uncertainty||'No disponible'],['Evidencia','Límites',action.limits],['Evidencia','Transferencia','Aplicación hipotética a México; intervalo original no incluye incertidumbre de transferencia ni del predictor. No se suman acciones.'],['Resumen del plan','Municipios seleccionados',fmt.format(plan.selected.length)],['Resumen del plan','Entidades',fmt.format(new Set(plan.selected.map(r=>r.state)).size)],['Resumen del plan','Base observable total (SV+NV 2024)',fmt.format(plan.reference_population)],['Resumen del plan','Personas alcanzadas (supuesto)',fmt.format(plan.served)],['Resumen del plan','Personas adicionales que votarían (supuesto)',plan.additional.toFixed(4)],['Resumen del plan','No votarían sin acción (ponderado)',pct(plan.before)],['Resumen del plan','No votarían con acción (ponderado)',pct(plan.after)],['Resumen del plan','Reducción (puntos porcentuales)',(plan.before-plan.after).toFixed(3)+' pp'],...Object.entries(dic).map(([k,v])=>['Diccionario de columnas',k,v]),['Limitaciones','Frecuencia no es probabilidad','Que un municipio aparezca en 6 de 6 variantes no garantiza acierto: las variantes comparten datos y pueden equivocarse juntas.'],['Limitaciones','Hipótesis no causal','La simulación no demuestra que una intervención aumente la participación.'],['Limitaciones','Base observable','Los escenarios usan SV+NV 2024; la participación no especificada queda fuera. No es electorado proyectado de 2027.'],['Limitaciones','Territorio','Claves INE con polígonos de referencia; límites históricos sin armonizar.']];
 const toCsv=rows=>new Blob(['\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});
 const trigger=(blob,name)=>{const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 trigger(toCsv([headers,...lines]),'Umbral_plan_municipios.csv');
 setTimeout(()=>trigger(toCsv([['Sección','Elemento','Detalle'],...leeme]),'Umbral_plan_leeme.csv'),450);
}


/* SOURCE: src/demo6/ui/lenses.js */
function initLensCards(){
 const cards=[...document.querySelectorAll('.lens-card')],select=$('lens');
 const apply=value=>{
  if(select.value!==value){select.value=value;update();}
  for(const c of cards){const on=c.dataset.lens===value;c.classList.toggle('active',on);c.setAttribute('aria-checked',on?'true':'false');c.tabIndex=on?0:-1;}
 };
 for(const card of cards){
  card.addEventListener('click',()=>apply(card.dataset.lens));
  card.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();apply(card.dataset.lens);}});
 }
 select.addEventListener('change',()=>apply(select.value));
 apply(select.value);
}


/* SOURCE: src/demo6/legacy/scenario-evidence.js */
function renderActionEvidence(a){
 $('custom-response').hidden=a.id!=='personalizada';
 $('response').disabled=a.id!=='personalizada';
 $('reach-label').textContent=a.estimand==='ITT'?'¿A cuántas personas planeas enviar el SMS en total?':a.estimand==='ATT'?'¿Con cuántas personas completarías la llamada en total?':'Personas que alcanzarías en total';
 $('coverage-help').textContent=a.estimand==='ITT'?'Cuenta personas distintas a quienes enviarías el SMS, no mensajes ni lectores.':a.estimand==='ATT'?'Cuenta conversaciones completadas sobre el plan de votación, no intentos de llamada.':'Introduce tu capacidad total de contacto. Es un supuesto proporcionado por ti.';
 if($('action-evidence').dataset.action===a.id)return;
 $('action-evidence').dataset.action=a.id;
 $('action-evidence').innerHTML=a.source?`<strong>${a.effect_pp} puntos porcentuales de aumento en el estudio</strong><p>Aplicación hipotética a México; requiere revisar si la población y el contexto son comparables.</p><details><summary>Consultar estudio, fuente y límites</summary><p>${esc(a.country)} · ${esc(a.election)}. ${esc(a.population)}</p><p>Efecto: ${a.effect_pp} pp · Estimador: ${esc(a.estimand)}. ${esc(a.unit)}</p><p>${esc(a.uncertainty)} ${esc(a.limits)}</p><p><a href="${esc(a.source)}" target="_blank" rel="noopener noreferrer">${esc(a.citation)}</a> ${esc(a.locator)}.${a.fulltext?` <a href="${esc(a.fulltext)}" target="_blank" rel="noopener noreferrer">Texto completo ↗</a>`:''}</p><p>Transferencia hipotética a México; no calibrada con CCPC. Un punto porcentual no es una respuesta porcentual entre abstencionistas.</p></details>`:`<strong>${esc(a.label)}</strong><p>${esc(a.limits)}</p>`;
}


/* SOURCE: src/demo6/app/bootstrap.js */
function load(){
 for(const a of Object.values(Decision.interventions))$('action').add(new Option(a.label,a.id));
 if(!window.UMBRAL_DATA||!window.UMBRAL_GEO)throw Error('Faltan datos incrustados');records=window.UMBRAL_DATA.municipios;metadata=window.UMBRAL_DATA.metadata;perfil=window.UMBRAL_PERFIL;geo=window.UMBRAL_GEO;
 const states=new Map(records.map(r=>[r.state,r.state_name]));for(const [key,name] of [...states].sort())$('state').add(new Option(name,key));
 for(const [key,name] of [...states].sort())$('simulation-state').add(new Option(name,key));
 simulationMunicipalities();
 $('simulation-scope').onchange=()=>applySimulationScope();
 $('simulation-state').onchange=()=>{simulationMunicipalities();applySimulationScope();};
 $('simulation-municipality').onchange=applySimulationScope;
map=L.map('map',{preferCanvas:true,attributionControl:true,dragging:false,zoomControl:false,scrollWheelZoom:false,doubleClickZoom:false,touchZoom:false,boxZoom:false,keyboard:false,zoomSnap:.25}).setView([23.7,-102.5],5);map.attributionControl.addAttribution('INE · mayo 2024 simplificado, límites no armonizados');
map.createPane('municipal-geography');
layer=L.geoJSON(geo,{renderer:createMapRenderer({pane:'municipal-geography'}),onEachFeature:(f,l)=>{const r=records.find(r=>r.key===f.properties.key),node=document.createElement('span');node.textContent=r.name+' · '+r.key;l.bindTooltip(node);l.on('click',()=>{focusMunicipality(r.key,l);});}}).addTo(map);
 initGeography();
 initSearchablePickers();
 $('show-all').onclick=()=>{$('stable').checked=false;update();};
 document.querySelectorAll('a[href="#planning-settings"]').forEach(a=>a.addEventListener('click',()=>{$('planning-settings').open=true;}));
document.querySelectorAll('[data-scenario-map]').forEach(a=>a.addEventListener('click',()=>{$('map-mode').value=a.dataset.scenarioMap;$('confidence').checked=false;update();}));
  document.querySelectorAll('a[href="#sin-estimacion"]').forEach(a=>a.addEventListener('click',()=>{$('sin-estimacion').open=true;}));
 for(const id of ['state','search','stable','min-confidence','reach','response','action','distribution','method','lens','map-mode','confidence'])$(id).addEventListener('input',()=>{if(id==='state'||id==='search'){geographyFocusKey=null;geographyHistory.length=0;$('simulation-scope').value=$('state').value?'estado':'pais';if($('state').value){$('simulation-state').value=$('state').value;simulationMunicipalities();const exact=records.find(r=>r.state===$('state').value&&(r.key===$('search').value||r.name===$('search').value));if(exact){$('simulation-scope').value='municipio';$('simulation-municipality').value=exact.key;}}$('simulation-state-wrap').hidden=$('simulation-scope').value==='pais';$('simulation-municipality-wrap').hidden=$('simulation-scope').value!=='municipio';}update();});
 $('state').addEventListener('change',()=>{
  if(typeof historicalMapEnabled!=='undefined' && historicalMapEnabled && typeof selectMapState==='function'){
   selectMapState($('state').value);
   return;
  }
  const layers=layer.getLayers().filter(l=>!$('state').value||byKey.get(l.feature.properties.key).state===$('state').value);
  if(layers.length)map.fitBounds(L.featureGroup(layers).getBounds(),{padding:[12,12]});
  if(typeof selectMapState==='function'){selectMapState($('state').value);}
 });
 $('ranking').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){selectMunicipalityResult(b.dataset.key);if(window.innerWidth<=1050)$('detail').scrollIntoView({behavior:smooth(),block:'start'});}});$('export').onclick=exportPlan;
 $('missing-list').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){selectMunicipalityResult(b.dataset.key);$('detail').scrollIntoView({behavior:smooth(),block:'start'});}});
 initLensCards();
 if(perfil&&perfil.nacional){$('perfil-nacional').innerHTML=['edad','sexo','seccion'].flatMap(dim=>Object.keys(perfil.nacional['2024'][dim]).map(g=>{const c=perfil.nacional['2024'][dim][g];return `<tr><td>${esc((GROUP_NAME[dim]&&GROUP_NAME[dim][g])||g)}</td><td>${c.abstencion_pct===null?'—':c.abstencion_pct.toFixed(2)+'%'}</td><td>${fmt.format(c.n)}</td></tr>`;})).join('');}
 $('metrics').innerHTML=Object.entries(metadata.checks).flatMap(([year,c])=>['persistencia','ridge'].map(method=>{const m=c[method];return `<tr><td>${year} · ${method}<small>n=${fmt.format(m.n)}</small></td><td>${m.mae.toFixed(2)} pp</td><td>${m.mae_ponderado.toFixed(2)} pp</td><td>${Math.round(m.precision_top*m.top_k)}/${m.top_k}</td></tr>`;})).join('');
 const ad=metadata.additional_evaluation;
 $('additional-metrics').innerHTML=Object.entries(ad.cuts).flatMap(([year,c])=>Object.entries(c).map(([method,m])=>`<tr><td>${year} · ${method}</td><td>${m.spearman.toFixed(3)}</td><td>${pct(100*m.precision_rojo)}</td><td>${pct(100*m.recobrado_rojo)}</td><td>${m.rojos_predichos}</td><td>${pct(100*m.precision_rojo_vs_tercio_observado_test)}</td></tr>`)).join('');
 $('size-errors').innerHTML=Object.entries(ad.error_by_size).flatMap(([cut,bins])=>Object.entries(bins).map(([size,m])=>`<tr><td>${esc(cut)}</td><td>${esc(size)}</td><td>${m.n}</td><td>${m.mae.toFixed(2)} pp</td><td>${m.p90_abs_error_pp.toFixed(2)} pp</td></tr>`)).join('');
 $('method-note').textContent='Al probar el modelo con elecciones pasadas, funcionó mejor que usar la elección anterior comparable en 2021, pero peor en 2024. Por eso, la cifra de 2027 sirve para explorar y requiere revisión. Una simulación no demuestra que una actividad vaya a aumentar el voto.';
 $('methodology').innerHTML='<p>MAE ponderado usa SV+NV del objetivo histórico. El umbral rojo de evaluación se aprende del entrenamiento y se congela por corte; precisión y recobrado usan ese mismo umbral. La última columna compara rojos predichos contra el tercio alto observado del test, solo retrospectivamente. Los umbrales de la demo 2027 son tercios de estimaciones base y quedan fijos entre sus tres modos.</p><p>Bandas por tamaño: SV+NV del último antecedente, bins &lt;10 mil, 10–100 mil y ≥100 mil. P90 de error retrospectivo no es intervalo futuro. Estabilidad de prioridad: frecuencia entre referencia/método comparado × NS 5/10/20 (seis variantes). No es probabilidad calibrada. La incertidumbre de ranking se informa con esta frecuencia y se distingue del rango retrospectivo de cada método, que se conserva como referencia de error histórico.</p><p>2021 se usa para seleccionar, no es prueba independiente posterior. 2024 es presidencial, no valida 2027. Solo seis ocasiones, tres intermedias. NS y límites históricos restringen inferencia.</p>';  update();map.fitBounds(layer.getBounds(),{padding:[12,12]});
}



/* SOURCE: src/demo6/ui/motion.js */
(() => {
  const root = document.documentElement;
  const progress = document.getElementById('scroll-progress-bar');
  const sections = [...document.querySelectorAll('.module')];
  const navLinks = [...document.querySelectorAll('.quick-nav a')];

  root.classList.add('motion-ready');

  const revealItems = document.querySelectorAll('.module-heading, .module-one-grid, .module-two-grid, .module-three-grid, .module-footer, .closing');
  revealItems.forEach((item, index) => {
    item.classList.add('reveal');
    if (index % 3) item.classList.add(`reveal-delay-${index % 3}`);
  });

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    revealItems.forEach(item => revealObserver.observe(item));

    const sectionObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        const active = `#${entry.target.id}`;
        navLinks.forEach(link => link.classList.toggle('is-active', link.getAttribute('href') === active));
      });
    }, { rootMargin: '-38% 0px -48% 0px' });
    sections.forEach(section => sectionObserver.observe(section));
  } else {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }

  let frame = 0;
  const updateProgress = () => {
    if (frame) return;
    frame = window.requestAnimationFrame(() => {
      const scrollable = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = scrollable > 0 ? window.scrollY / scrollable : 0;
      progress.style.width = `${Math.min(100, Math.max(0, ratio * 100))}%`;
      frame = 0;
    });
  };
  window.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();
})();


/* SOURCE: src/demo6/map/years.js */
function getAvailableYears(){
  const years = new Set();
  if(typeof records === 'undefined' || !records) return [2027];
  for(const r of records){
    for(const h of (r.history||[])){
      if(Number.isFinite(h.year)){
        years.add(h.year);
      }
    }
  }
  years.add(2027);
  return [...years].sort((a,b)=>a-b);
}

function populateMapYearSelector(){
  const sel = $('map-year');
  if(!sel){return;}
  sel.replaceChildren();
  const years = getAvailableYears();
  for(const y of years){
    sel.add(new Option(String(y),String(y)));
  }
  if(years.length){sel.value = String(currentMapYear);}
  console.log('Umbral map: años disponibles:', years);
}



/* SOURCE: src/demo6/map/styles.js */
function estiloMunicipal(year,stateKey){return runtime.mapStyles.municipality(year,stateKey);}
function estiloEstado(year){return runtime.mapStyles.state(year);}



/* SOURCE: src/demo6/map/layers.js */
function removeMapLayers(){
  if(contextLayer){
    map.removeLayer(contextLayer);
    contextLayer=null;
  }
  if(municipalityLayer){
    try{map.removeLayer(municipalityLayer);}catch(e){}
    municipalityLayer = null;
  }
  if(stateOverlayLayer){
    try{map.removeLayer(stateOverlayLayer);}catch(e){}
    stateOverlayLayer = null;
  }
  if(boundaryLayer){
    try{map.removeLayer(boundaryLayer);}catch(e){}
    boundaryLayer = null;
  }
}

function limpiarPaneMunicipalNativo(){
  if(typeof map==='undefined' || !map) return;
  const paneMun = map.getPane && map.getPane('municipal-geography');
  if(paneMun) paneMun.style.visibility = 'visible';
}

function limpiarPaneEstadoNativo(){
  if(typeof map==='undefined' || !map) return;
  const paneState = map.getPane && map.getPane('state-geography');
  if(paneState) paneState.style.visibility = 'visible';
}

function cerrarPickers(){
  if(typeof statePicker!=='undefined' && statePicker && typeof statePicker.close==='function'){statePicker.close();}
  if(typeof municipalityPicker!=='undefined' && municipalityPicker && typeof municipalityPicker.close==='function'){municipalityPicker.close();}
}

function sincronizarSelectores(stateKey){
  const selEstado = $('state');
  if(!selEstado) return;
  if(selEstado.value !== stateKey){
    selEstado.value = stateKey;
  }
  cerrarPickers();
  const searchInput = $('search');
  const munToggle = $('municipality-toggle');
  if(searchInput){
    searchInput.disabled = !stateKey;
    searchInput.placeholder = stateKey ? 'Escribe o elige un municipio' : 'Elige primero un estado';
  }
  if(munToggle){munToggle.disabled = !stateKey;}
  const statePickerInput = $('state-picker');
  if(typeof pickerState==='undefined' || pickerState !== stateKey){
    pickerState = stateKey;
    if(statePickerInput && statePickerInput.value != (stateKey?'—':'Todo México')){
      statePickerInput.value = stateKey ? (records.find(r=>r.state===stateKey)?.state_name || stateKey) : 'Todo México';
      if(typeof statePicker!=='undefined' && statePicker && typeof statePicker.close==='function'){statePicker.close();}
    }
  }
  if(stateKey && searchInput){
    const exact = records.find(r=>r.state===stateKey && (r.key===searchInput.value || r.name===searchInput.value));
    if(!exact && searchInput.value) searchInput.value = '';
  }
  if(stateKey){
    const planPanel = $('state-plan-panel');
    if(planPanel){planPanel.hidden = false;}
    renderStatePlan(stateKey);
  } else {
    const planPanel = $('state-plan-panel');
    if(planPanel){planPanel.hidden = true;}
  }
  const mapYear = $('map-year');
  if(mapYear){mapYear.disabled = false;}
  if(stateKey && mapInitialized && historicalMapEnabled){ update(); }
}

function crearLayerMunicipioEstado(year, estadoSeleccionado){
  if(!municipalityRenderer){
    municipalityRenderer = L.svg({pane:'municipal-geography'});
  }
  return L.geoJSON(window.UMBRAL_GEO,{
    filter:f=>byKey.get(f.properties.key)?.state === estadoSeleccionado,
    noClip:true,
    bubblingMouseEvents:false,
    renderer: municipalityRenderer,
    onEachFeature:(f,l)=>{
      const r=byKey.get(f.properties.key);
      if(!r) return;
      const node=document.createElement('span');
      node.textContent=r.name+' · '+r.key;
      l.bindTooltip(node);
      l.on('click',(ev)=>{
        L.DomEvent.stopPropagation(ev);
        const clave = f.properties.key;
        const mun = byKey.get(clave);
        map.stop();
        // focusMunicipality guarda la vista anterior antes de seleccionar el municipio.
        if(typeof focusMunicipality==='function'){
          focusMunicipality(clave,l);
        } else {
          if(mun && $('search')){ $('search').value = mun.name; }
          map.fitBounds(l.getBounds(),{padding:[30,30],maxZoom:10,animate:true});
        }
      });
    },
    style: estiloMunicipal(year, estadoSeleccionado)
  });
}

function paintMapSelection(){
  if(!municipalityLayer) return;
  const base=estiloMunicipal(currentMapYear,activeMapState);
  municipalityLayer.eachLayer(polygon=>{
    const key=polygon.feature.properties.key;
    const selected=key===geographyFocusKey;
    polygon.setStyle({...base(polygon.feature),
      ...(selected?{fillOpacity:1,opacity:1,weight:2}: {})});
    const path=polygon.getElement();
    if(path){
      path.classList.toggle('municipality-out-of-focus',!!geographyFocusKey && !selected);
    }
    if(selected)polygon.bringToFront();
  });
}

function ocultarCapasMunicipalesNativasEnPane(paneMun){
  if(typeof map==='undefined' || !map) return;
  if(!paneMun) return;
  map.eachLayer(l=>{
    if(l && l.options && l.options.pane === paneMun && l !== municipalityLayer && l !== boundaryLayer){
      try{ l.setStyle({fillOpacity:0,opacity:0,color:'#000000',weight:0}); }catch(e){}
    }
  });
}

function ocultarCapasMunicipalesNativas(){
  const paneMun = map.getPane && map.getPane('municipal-geography');
  ocultarCapasMunicipalesNativasEnPane(paneMun);
}

function reconstruirMapa(year, {encuadrar=true}={}){
  if(typeof map === 'undefined' || !map ||
     typeof byKey === 'undefined' || !byKey ||
     typeof thresholds === 'undefined' ||
     typeof window === 'undefined' || !window.UMBRAL_GEO ||
     !window.UMBRAL_STATES){
    console.warn('Umbral map: dependencias no listas');
    return;
  }
  const esPrediccion2027 = (year === 2027);  const enEstado = activeMapState;
  layer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});
  stateLayer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});

  /* Control de panes originales ANTES de tocar capas, para que no se pinte sobre lo viejo */
  const paneMun = map.getPane && map.getPane('municipal-geography');
  const paneState = map.getPane && map.getPane('state-geography');
  if(enEstado){
    if(paneState) paneState.style.visibility = 'hidden';
    if(paneMun) paneMun.style.visibility = 'visible';
  } else {
    if(paneState) paneState.style.visibility = 'visible';
    if(paneMun) paneMun.style.visibility = 'hidden';
  }

  if(enEstado){
    /* Reutilizar los municipios mientras siga seleccionada la misma entidad. */
    if(!municipalityLayer || !map.hasLayer(municipalityLayer) || municipalityLayerState !== enEstado){
      if(municipalityLayer && map.hasLayer(municipalityLayer)){ try{map.removeLayer(municipalityLayer);}catch(e){} municipalityLayer=null; }
      if(contextLayer){map.removeLayer(contextLayer);}
      if(!municipalityRenderer){municipalityRenderer=L.svg({pane:'municipal-geography'});}
      contextLayer=L.geoJSON(window.UMBRAL_STATES,{
        filter:f=>f.properties.state!==enEstado,
        renderer:municipalityRenderer,
        noClip:true,
        interactive:false,
        className:'state-out-of-focus',
        style:estiloEstado(year)
      }).addTo(map);
      municipalityLayer = crearLayerMunicipioEstado(year, enEstado).addTo(map);
      municipalityLayerState = enEstado;
      ocultarCapasMunicipalesNativas();
    } else {
      municipalityLayer.setStyle(estiloMunicipal(year, enEstado));
      if(contextLayer){contextLayer.setStyle(estiloEstado(year));}
    }

    paintMapSelection();
    if(!boundaryLayer){
      boundaryLayer = L.geoJSON(window.UMBRAL_STATES,{
        noClip:true,
        renderer: municipalityRenderer,
        style: {color:'#000000',weight:1.2,fillOpacity:0,opacity:.7,clickable:false},
        interactive:false
      }).addTo(map);
    }
    boundaryLayer.eachLayer(polygon=>{
      polygon.getElement()?.classList.toggle('state-out-of-focus',polygon.feature.properties.state!==enEstado);
    });

    const polyEstado = stateLayer ? stateLayer.getLayers().find(p=>p.feature.properties.state===enEstado) : null;
    if(polyEstado && encuadrar){ map.stop(); map.fitBounds(polyEstado.getBounds(),{padding:[12,12],maxZoom:9,animate:true,duration:.25}); }
  } else {
    if(municipalityLayer){map.removeLayer(municipalityLayer);municipalityLayer=null;}
    if(contextLayer){map.removeLayer(contextLayer);contextLayer=null;}
    if(boundaryLayer){map.removeLayer(boundaryLayer);boundaryLayer=null;}
    if(!stateRenderer){stateRenderer=L.svg({pane:'state-geography'});}

    /* VISTA NACIONAL: capa de estados + límites */
    if(!stateOverlayLayer){
    stateOverlayLayer = L.geoJSON(window.UMBRAL_STATES,{
      noClip:true,
      renderer: stateRenderer,
      onEachFeature:(f,l)=>{
        const state=f.properties.state;
        const name = records.find(r=>r.state===state)?.state_name || state;
      l.bindTooltip(name+' · '+state);
      l.on('click',(ev)=>{
        L.DomEvent.stopPropagation(ev);
        activeMapState = state;
        geographyFocusKey=null;activeKey=null;
        $('search').value='';
        sincronizarSelectores(state);
        reconstruirMapa(currentMapYear);
      });
      },
      style: estiloEstado(year)
    });    stateOverlayLayer.addTo(map);
    }
    stateOverlayLayer.bringToFront();
    stateOverlayLayer.setStyle(estiloEstado(year));
    if(encuadrar){map.fitBounds(stateOverlayLayer.getBounds(),{padding:[12,12],animate:true});}

    /* En vista nacional el pane municipal permanece oculto: solo se muestran los colores promedio de estado. */
    limpiarPaneEstadoNativo();
  }

  /* Actualizar textos */
  if($('map-caption')){
    $('map-caption').textContent = esPrediccion2027 ?
      'Estimación exploratoria para 2027. Colores por tercios del método activo. Gris = sin estimación.' :
      'Abstención observada en la elección de ' + year + '. Colores por tercios del método activo. Gris = sin dato en ese año.';
  }
  const legend = document.querySelector('.legend');
  if(legend){
    legend.innerHTML =
      '<span><i class="low" style="background:'+colors.bajo+'"></i>Menor abstención</span>' +
      '<span><i class="medium" style="background:'+colors.medio+'"></i>Intermedia</span>' +
      '<span><i class="high" style="background:'+colors.alto+'"></i>Mayor abstención</span>' +
      '<span><i class="missing"></i>'+(esPrediccion2027?'Sin estimación':'Sin dato en '+year)+'</span>';
  }
  const guide = document.querySelector('.map-guide');
  if(guide){
    guide.textContent = esPrediccion2027 ?
      'Mapa de estimación 2027: los estados se colorean con su abstención promedio estimada para 2027. Click en un estado para ver municipios.' :
      'Mapa histórico: los estados se colorean con su abstención promedio observada en '+year+'. Click en un estado para explorar municipios.';
  }
  console.log('Umbral map: mapa reconstruido para año', year, esPrediccion2027 ? '(estimación 2027)' : '(histórico)', enEstado ? 'estado:'+enEstado : 'nacional');
}



/* SOURCE: src/demo6/map/navigation.js */
function volverAMexico(){
  geographyFocusKey=null;activeKey=null;geographyHistory.length=0;
  activeMapState = null;
  if($('state')){$('state').value='';}
  if($('search')){$('search').value='';}
  const mapYear=$('map-year');
  if(mapYear){mapYear.disabled=false;}
  sincronizarSelectores(null);
  update();
  reconstruirMapa(currentMapYear);
}

/* Cambiar de entidad desde el buscador tiene que rehacer las capas y los paneles del modo histórico.
   El buscador solo actualiza el <select> y dispara input/change; en modo histórico update() y
   updateGeography() se saltan el cambio de nivel, así que sin este paso la escala quedaba nacional
   con el panel municipal visible (divisiones por municipio sobre todo el país) y la bandera obsoleta. */
function selectMapState(stateKey){
  activeMapState = stateKey || null;
  geographyFocusKey=null;activeKey=null;
  if($('search')){ $('search').value = ''; }
  sincronizarSelectores(activeMapState);
  /* En modo histórico el nivel del mapa (paneles y encuadre) lo decide demo5; tras una
     simulación manda la app base, que ya ajusta paneles y encuadre por su cuenta. */
  if(typeof historicalMapEnabled !== 'undefined' && historicalMapEnabled){ reconstruirMapa(currentMapYear); }
}

/* Red de seguridad de la vuelta atras (clic derecho): el nivel del mapa tiene que coincidir con el
   selector de estado. Si un clic derecho termina a escala nacional pero la capa de municipios sigue
   a la vista, se ven las divisiones por municipio sobre los estados; aqui se reconstruye el nivel. */
function syncMapLevel(){
  if(typeof map === 'undefined' || !map) return;
  if(typeof historicalMapEnabled === 'undefined' || !historicalMapEnabled) return;  /* en modo simulacion manda la app base */
  const esperado = $('state') ? ($('state').value || '') : '';
  const paneMunicipal = map.getPane && map.getPane('municipal-geography');
  const municipiosALaVista = !!(paneMunicipal && paneMunicipal.style.visibility === 'visible');
  if(esperado === (activeMapState || '') && (esperado || !municipiosALaVista)) return;
  activeMapState = esperado || null;
  sincronizarSelectores(activeMapState);
  if(!esperado){
    if($('search')){$('search').value = '';}
    const mapYear = $('map-year');
    if(mapYear){mapYear.disabled = false;}
  }
  reconstruirMapa(currentMapYear);
}

function renderStatePlan(){if($('state-plan-panel'))$('state-plan-panel').hidden=true;}



/* SOURCE: src/demo6/map/start.js */
function initMapLayers(){
  if(mapInitialized){return;}
  mapInitialized = true;
  map.attributionControl.addAttribution('Islas: INEGI · Marco Geoestadístico 2025');
  // Evitar la escala temporal del SVG: Leaflet reproyecta los trazos al finalizar
  // y produce un salto visible en los bordes y en la geometría simplificada.
  const fitBoundsDemo5 = map.fitBounds.bind(map);
  let transicionVista = null;
  map.fitBounds = function(bounds, options = {}){
    map.stop();
    if(transicionVista){
      transicionVista.cancel();
      transicionVista = null;
    }
    const resultado = fitBoundsDemo5(bounds, {...options, animate:false});
    // Animar la aparición de la nueva vista, sin escalar los trazos del SVG.
    // El encuadre se aplica de inmediato para mantener sincronizada la navegación.
    const pane = map.getPane('mapPane');
    if(pane && pane.animate && options.animate !== false &&
       !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      transicionVista = pane.animate(
        [{opacity:0}, {opacity:1}],
        {duration:260, easing:'ease-out'}
      );
    }
    return resultado;
  };
  console.log('Umbral map: inicializando');
  populateMapYearSelector();
  const sel = $('map-year');
  if(sel){
    sel.addEventListener('change',()=>{
      const y = Number(sel.value);
      if(!isNaN(y)){
        historicalMapEnabled = true;
        currentMapYear = y;
        activeMapState = $('state').value || null;
        updateExplorationAnalysis();
        renderStatePlan(activeMapState);
        if(!activeMapState && $('state-plan-panel')){$('state-plan-panel').hidden=true;}
        reconstruirMapa(y,{encuadrar:false});
      }
    });
  }
  if($('search')){
    $('search').addEventListener('input',()=>{
      const exact = records.find(r=>r.state===activeMapState && (r.key===$('search').value||r.name===$('search').value));
      if(exact && activeMapState){
        renderStatePlan(activeMapState);
      }
    });
  }
  const stateInput=$('state-picker');
  if(stateInput){
    stateInput.addEventListener('input',()=>{  if(activeMapState&&historicalMapEnabled&&$('state').value){
        renderStatePlan(activeMapState);
      }
    });
  }
  map.on('contextmenu', syncMapLevel);
  reconstruirMapa(currentMapYear);
  console.log('Umbral map: listo');
}



/* SOURCE: src/demo6/map/decorations.js */
function initMapDecorations(){
  const mapElement = document.getElementById('map');
  if (!mapElement || typeof map === 'undefined') return;

  // Keep the ocean texture outside the country silhouette. The electoral
  // polygons intentionally use partial opacity, so give them an opaque land base.
  if (window.UMBRAL_STATES && map.createPane) {
    const municipalPane = map.getPane('municipal-geography');
    const statePane = map.getPane('state-geography');
    if (municipalPane) municipalPane.style.zIndex = '410';
    if (statePane) statePane.style.zIndex = '420';

    map.createPane('demo4-land-mask');
    const landPane = map.getPane('demo4-land-mask');
    landPane.style.zIndex = '399';
    landPane.style.pointerEvents = 'none';
    L.geoJSON(window.UMBRAL_STATES, {
      pane: 'demo4-land-mask',
      renderer: L.Browser.svg
        ? L.svg({ pane: 'demo4-land-mask' })
        : L.canvas({ pane: 'demo4-land-mask' }),
      interactive: false,
      noClip: true,
      style: {
        color: '#bac7bd',
        weight: 0.7,
        opacity: 0.8,
        fillColor: '#f4f1e9',
        fillOpacity: 1
      }
    }).addTo(map);
  }

  const coordinates = document.createElement('div');
  coordinates.className = 'map-coordinates';
  coordinates.setAttribute('aria-hidden', 'true');
  coordinates.textContent = 'N ↑   MUEVE EL CURSOR';
  mapElement.append(coordinates);

  const formatCoordinate = (value, positive, negative) => {
    const direction = value < 0 ? negative : positive;
    return `${Math.abs(value).toFixed(4)}° ${direction}`;
  };

  map.on('mousemove', ({ latlng }) => {
    coordinates.textContent = `${formatCoordinate(latlng.lat, 'N', 'S')} · ${formatCoordinate(latlng.lng, 'E', 'O')}`;
  });
  map.on('mouseout', () => {
    coordinates.textContent = 'N ↑   MUEVE EL CURSOR';
  });

}


/* SOURCE: src/demo6/domain/state-plans.js */
/* Planes de acción por entidad federativa para mejorar la participación y reducir la abstención.
   Datos estructurados derivados de docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md.
   Claves de entidad coinciden con fichas_estatales.js (01-32).
   Información descriptiva: ejes, acciones, actores e indicadores. Sin cálculos de impacto. */
const STATE_PLANS = {
  '01': { key: '01', name: 'Aguascalientes', priority: 'Campañas en zonas urbanas con menor participación histórica.',
    axes: ['Acceso al voto', 'Juventud y primer voto', 'Información cívica'],
    actions: [
      'Campaña de información cívica en cabecera municipal y delegaciones.',
      'Puntos móviles de atención para trámite de credencial en zonas con baja cobertura registral.',
      'Jornadas de simulación de voto en bachilleratos y universidades.',
    ],
    actors: ['INE junta local', 'OPL de Aguascalientes', 'Ayuntamiento de la capital', 'Instituciones educativas'],
    indicators: ['Credenciales vigentes en lista nominal', 'Asistencia a casillas', 'Mensajes de información entregados'],
  },
  '02': { key: '02', name: 'Baja California', priority: 'Revalidación de domicilio en zonas fronterizas.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña dirigida a residentes con domicilio en el estado ausentes temporalmente (revalidación de domicilio).',
      'Casillas estratégicas en zonas fronterizas y de alto tránsito.',
      'Mensajes en español e inglés en medios locales y redes sociales.',
    ],
    actors: ['INE junta local', 'OPL de Baja California', 'Ayuntamientos', 'Consulados'],
    indicators: ['Actualización de domicilio en credencial', 'Casillas instaladas', 'Participación por sección'],
  },
  '03': { key: '03', name: 'Baja California Sur', priority: 'Cobertura de casillas en zonas rurales y alejadas.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Mapa de casillas con cobertura territorial priorizando zonas rurales y cabeceras.',
      'Difusión radiofónica en zonas con baja conectividad digital.',
      'Apoyo logístico de traslado a casillas en comunidades alejadas.',
    ],
    actors: ['INE junta local', 'OPL de Baja California Sur', 'Ayuntamientos', 'Autoridades comunitarias'],
    indicators: ['Casillas con acceso reportado', 'Participación rural vs urbana', 'Alcance de difusión radiofónica'],
  },
  '04': { key: '04', name: 'Campeche', priority: 'Campaña bilingüe en municipios con población indígena.',
    axes: ['Información cívica', 'Confianza institucional', 'Acceso al voto'],
    actions: [
      'Campaña bilingüe (español y lenguas mayas) de información electoral.',
      'Casillas con intérpretes y materiales traducidos en municipios con población indígena.',
      'Articulación con autoridades tradicionales para convocatoria al voto.',
    ],
    actors: ['INE junta local', 'OPL de Campeche', 'Ayuntamientos', 'Autoridades indígenas y comunitarias'],
    indicators: ['Materiales en lenguas indígenas', 'Casillas con intérprete', 'Participación en municipios rurales'],
  },
  '05': { key: '05', name: 'Coahuila de Zaragoza', priority: 'Centros laborales con turnos extendidos.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña en centros laborales (maquiladoras, minería) con información sobre horarios y permiso para votar.',
      'Casillas con horarios accesibles para turnos laborales.',
      'Difusión en radios locales y sindicatos.',
    ],
    actors: ['INE junta local', 'OPL de Coahuila', 'Ayuntamientos', 'Sector privado', 'Sindicatos'],
    indicators: ['Centros laborales alcanzados', 'Casillas con horario extendido', 'Participación en zonas industriales'],
  },
  '06': { key: '06', name: 'Colima', priority: 'Campaña digital y recordatorios a jóvenes.',
    axes: ['Juventud y primer voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Campaña digital segmentada por edad y sección electoral.',
      'Recordatorios vía SMS y redes sociales en días previos a la elección.',
      'Simulacros de voto en instituciones educativas de la capital.',
    ],
    actors: ['INE junta local', 'OPL de Colima', 'Ayuntamientos', 'Instituciones educativas'],
    indicators: ['Alcance de campaña digital', 'Recordatorios enviados', 'Participación juvenil'],
  },
  '07': { key: '07', name: 'Chiapas', priority: 'Municipios con baja participación histórica y zonas de difícil acceso.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Red de casillas con cobertura prioritaria en municipios con baja participación histórica.',
      'Campaña cívica en lenguas tsotsil, tseltal, chol y español.',
      'Brigadas de información casa por casa en zonas de difícil acceso.',
      'Capacitación de funcionarios de casilla con sensibilidad cultural.',
    ],
    actors: ['INE junta local', 'OPL de Chiapas', 'Ayuntamientos', 'Organizaciones de la sociedad civil', 'Autoridades comunitarias'],
    indicators: ['Casillas en municipios prioritarios', 'Materiales en lenguas originarias', 'Brigadas realizadas', 'Participación municipal'],
  },
  '08': { key: '08', name: 'Chihuahua', priority: 'Zonas serranas y municipios rurales con menor cobertura.',
    axes: ['Acceso al voto', 'Información cívica', 'Juventud y primer voto'],
    actions: [
      'Campaña segmentada por zona (urbana en Chihuahua/Juárez; rural en serranía).',
      'Puntos de información en cabeceras municipales y ferias locales.',
      'Transporte de apoyo en zonas serranas el día de elección.',
    ],
    actors: ['INE junta local', 'OPL de Chihuahua', 'Ayuntamientos', 'Transporte público estatal/municipal'],
    indicators: ['Participación por municipio', 'Puntos de información instalados', 'Servicios de traslado'],
  },
  '09': { key: '09', name: 'Ciudad de México', priority: 'Secciones de menor participación por alcaldía.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Plan territorial por alcaldía con foco en secciones de menor participación histórica.',
      'Campaña masiva en transporte público (metro, metrobús), espacios comerciales y universidades.',
      'Casillas adicionales en zonas de alta densidad poblacional.',
      'Difusión digital segmentada por grupo de edad y alcaldía.',
    ],
    actors: ['INE junta local', 'OPL de la Ciudad de México', 'Alcaldías', 'Transporte público', 'Instituciones educativas'],
    indicators: ['Participación por sección y alcaldía', 'Casillas instaladas', 'Cobertura en transporte público', 'Alcance digital'],
  },
  '10': { key: '10', name: 'Durango', priority: 'Juventudes 18–29 y zonas mineras/rurales.',
    axes: ['Juventud y primer voto', 'Acceso al voto', 'Información cívica'],
    actions: [
      'Campaña dirigida a juventudes basada en la investigación local de participación política y electoral.',
      'Casillas con cobertura en zonas mineras y rurales.',
      'Talleres de educación cívica en secundaria y bachillerato.',
    ],
    actors: ['INE junta local', 'OPL de Durango', 'Ayuntamientos', 'Instituciones educativas', 'Investigadores locales'],
    indicators: ['Participación juvenil 18–29', 'Talleres realizados', 'Casillas en zonas rurales/mineras'],
  },
  '11': { key: '11', name: 'Guanajuato', priority: 'Municipios rurales del norte y sur del estado.',
    axes: ['Confianza institucional', 'Información cívica', 'Acceso al voto'],
    actions: [
      'Campaña en plazas públicas y eventos comunitarios con líderes locales de opinión.',
      'Información cívica en parroquias y centros comunitarios (sin partidismo).',
      'Casillas con cobertura en municipios rurales del norte y sur del estado.',
    ],
    actors: ['INE junta local', 'OPL de Guanajuato', 'Ayuntamientos', 'Líderes comunitarios'],
    indicators: ['Participación municipal', 'Eventos comunitarios', 'Casillas rurales'],
  },
  '12': { key: '12', name: 'Guerrero', priority: 'Regiones indígenas y zonas con desafíos de seguridad.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Casillas con medidas de seguridad y acceso acordadas con autoridades locales.',
      'Campaña bilingüe en regiones indígenas (náhuatl, mixteco, tlapaneco, amuzgo).',
      'Difusión en radios comunitarias y altoparlantes municipales.',
    ],
    actors: ['INE junta local', 'OPL de Guerrero', 'Ayuntamientos', 'Autoridades comunitarias', 'Radios comunitarias'],
    indicators: ['Casillas operativas', 'Materiales en lenguas indígenas', 'Municipios cubiertos por radio comunitaria'],
  },
  '13': { key: '13', name: 'Hidalgo', priority: 'Municipios indígenas y zonas de la sierra.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en otomí, náhuatl y español en municipios con población indígena.',
      'Casillas con cobertura en zonas de la sierra y huasteca hidalguense.',
      'Talleres de educación cívica en telebachilleratos y CECyTE.',
    ],
    actors: ['INE junta local', 'OPL de Hidalgo', 'Ayuntamientos', 'Instituciones educativas', 'Autoridades indígenas'],
    indicators: ['Participación en municipios indígenas', 'Talleres realizados', 'Casillas en zonas rurales'],
  },
  '14': { key: '14', name: 'Jalisco', priority: 'Zonas de baja participación en Guadalajara y conurbados.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña metropolitana con enfoque en zonas de baja participación de Guadalajara y zona conurbada.',
      'Casillas adicionales en municipios con alta densidad.',
      'Difusión digital y en medios masivos segmentada por grupo de edad.',
    ],
    actors: ['INE junta local', 'OPL de Jalisco', 'Ayuntamientos', 'Medios de comunicación'],
    indicators: ['Participación por sección metropolitana', 'Casillas instaladas', 'Alcance digital'],
  },
  '15': { key: '15', name: 'Estado de México', priority: 'Secciones con menor participación histórica y zonas conurbadas.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Plan territorial por sección con foco en secciones con menor participación histórica.',
      'Campaña masiva en transporte público y espacios comerciales.',
      'Casillas adicionales en zonas de alta densidad poblacional.',
      'Brigadas de información en municipios conurbados con CDMX.',
    ],
    actors: ['INE junta local', 'OPL del Estado de México', 'Ayuntamientos', 'Transporte público', 'Comercio organizado'],
    indicators: ['Participación por sección', 'Casillas instaladas', 'Cobertura de campaña en transporte público'],
  },
  '16': { key: '16', name: 'Michoacán de Ocampo', priority: 'Regiones indígenas y meseta purépecha.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Campaña en purépecha y español en regiones con población indígena.',
      'Información dirigida a migrantes y familias con residencia temporal (revalidación de credencial).',
      'Casillas con cobertura en zonas rurales de la meseta purépecha.',
    ],
    actors: ['INE junta local', 'OPL de Michoacán', 'Ayuntamientos', 'Autoridades indígenas', 'Organizaciones de migrantes'],
    indicators: ['Participación en zonas indígenas', 'Revalidaciones de credencial', 'Casillas rurales'],
  },
  '17': { key: '17', name: 'Morelos', priority: 'Zonas urbanas y adultas mayores.',
    axes: ['Información cívica', 'Juventud y primer voto', 'Acceso al voto'],
    actions: [
      'Campaña digital y en espacios públicos de Cuernavaca y municipios conurbados.',
      'Recordatorios de elección vía redes sociales y SMS.',
      'Casillas con accesibilidad en zonas con población adulta mayor.',
    ],
    actors: ['INE junta local', 'OPL de Morelos', 'Ayuntamientos', 'Centros de atención al adulto mayor'],
    indicators: ['Participación urbana', 'Recordatorios enviados', 'Casillas accesibles'],
  },
  '18': { key: '18', name: 'Nayarit', priority: 'Zonas serranas y costeras con población indígena.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      "Campaña en lenguas wixárika, náayeri, o'dam y español.",
      'Casillas con cobertura en zonas serranas y costeras.',
      'Articulación con autoridades tradicionales para convocatoria.',
    ],
    actors: ['INE junta local', 'OPL de Nayarit', 'Ayuntamientos', 'Autoridades indígenas'],
    indicators: ['Materiales en lenguas originarias', 'Participación en municipios serranos/costeros', 'Casillas con intérprete'],
  },
  '19': { key: '19', name: 'Nuevo León', priority: 'Secciones de baja participación en zona metropolitana.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en zona metropolitana con foco en secciones de baja participación.',
      'Información en centros laborales e industriales sobre permiso para votar.',
      'Casillas con horario accesible para turnos laborales.',
      'Difusión digital segmentada por edad y sección.',
    ],
    actors: ['INE junta local', 'OPL de Nuevo León', 'Ayuntamientos', 'Sector privado', 'Sindicatos'],
    indicators: ['Participación metropolitana', 'Centros laborales alcanzados', 'Casillas con horario extendido'],
  },
  '20': { key: '20', name: 'Oaxaca', priority: 'Municipios de la sierra y costa con baja participación.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Campaña multilingüe (zapoteco, mixteco, mazateco, chinanteco, entre otros) y español.',
      'Red de casillas con cobertura prioritaria en municipios de la sierra y costa.',
      'Brigadas casa por casa con intérpretes comunitarios.',
      'Capacitación de funcionarios de casilla con sensibilidad cultural.',
    ],
    actors: ['INE junta local', 'OPL de Oaxaca', 'Ayuntamientos', 'Autoridades comunitarias e indígenas', 'OSC'],
    indicators: ['Materiales en lenguas indígenas', 'Casillas en municipios prioritarios', 'Brigadas realizadas', 'Participación municipal'],
  },
  '21': { key: '21', name: 'Puebla', priority: 'Sierra norte y mixteca poblana.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña en náhuatl, totonaco y español en municipios con población indígena.',
      'Casillas con cobertura en zonas de la sierra norte y mixteca poblana.',
      'Difusión en medios locales y redes comunitarias.',
    ],
    actors: ['INE junta local', 'OPL de Puebla', 'Ayuntamientos', 'Autoridades indígenas', 'Medios locales'],
    indicators: ['Participación en municipios indígenas', 'Casillas rurales', 'Materiales en lenguas originarias'],
  },
  '22': { key: '22', name: 'Querétaro', priority: 'Zonas de reciente crecimiento urbano y fraccionamientos.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en zonas de reciente crecimiento urbano y fraccionamientos.',
      'Información sobre trámite de credencial para nuevos residentes.',
      'Casillas con cobertura en zonas de alta densidad nueva.',
    ],
    actors: ['INE junta local', 'OPL de Querétaro', 'Ayuntamientos', 'Desarrolladores habitacionales'],
    indicators: ['Credenciales tramitadas por nuevos residentes', 'Participación en zonas nuevas', 'Casillas instaladas'],
  },
  '23': { key: '23', name: 'Quintana Roo', priority: 'Residentes temporales y zonas rurales de la selva.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña dirigida a residentes con domicilio en el estado (revalidación de credencial y domicilio).',
      'Casillas en zonas turísticas y comunidades rurales de la selva.',
      'Difusión en medios locales y puntos de atención turística.',
    ],
    actors: ['INE junta local', 'OPL de Quintana Roo', 'Ayuntamientos', 'Sector turístico'],
    indicators: ['Actualización de domicilio', 'Participación en zonas turísticas/rurales', 'Casillas instaladas'],
  },
  '24': { key: '24', name: 'San Luis Potosí', priority: 'Regiones huasteca y media con población indígena.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña en náhuatl, tenek y español en regiones huasteca y media.',
      'Casillas con cobertura en municipios rurales y serranos.',
      'Difusión en radios comunitarias de la huasteca.',
    ],
    actors: ['INE junta local', 'OPL de San Luis Potosí', 'Ayuntamientos', 'Radios comunitarias', 'Autoridades indígenas'],
    indicators: ['Participación en municipios rurales', 'Materiales en lenguas indígenas', 'Cobertura radiofónica'],
  },
  '25': { key: '25', name: 'Sinaloa', priority: 'Zonas agrícolas y trabajadores del campo.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña en zonas agrícolas con información adaptada a jornadas laborales del campo.',
      'Casillas con horario accesible para trabajadores agrícolas.',
      'Difusión en radios locales y centros de acopio/comunidades agrícolas.',
    ],
    actors: ['INE junta local', 'OPL de Sinaloa', 'Ayuntamientos', 'Organizaciones agrícolas', 'Radios locales'],
    indicators: ['Participación en zonas agrícolas', 'Casillas con horario extendido', 'Centros de acopio alcanzados'],
  },
  '26': { key: '26', name: 'Sonora', priority: 'Zonas fronterizas, desérticas y regiones indígenas.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Campaña en zonas fronterizas y desérticas con cobertura de transporte a casillas.',
      'Campaña bilingüe en regiones indígenas (yaqui, mayo, seri, pápago).',
      'Casillas con cobertura en zonas de baja densidad poblacional.',
    ],
    actors: ['INE junta local', 'OPL de Sonora', 'Ayuntamientos', 'Autoridades indígenas', 'Transporte público'],
    indicators: ['Participación en zonas fronterizas/desérticas', 'Materiales en lenguas indígenas', 'Servicios de traslado'],
  },
  '27': { key: '27', name: 'Tabasco', priority: 'Zonas propensas a inundación y municipios rurales.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Plan de contingencia para casillas en zonas propensas a inundación.',
      'Campaña en municipios rurales y zonas urbanas de Villahermosa.',
      'Difusión en radios locales y altoparlantes municipales.',
    ],
    actors: ['INE junta local', 'OPL de Tabasco', 'Ayuntamientos', 'Protección civil', 'Radios locales'],
    indicators: ['Casillas con plan de contingencia', 'Participación municipal', 'Cobertura de difusión'],
  },
  '28': { key: '28', name: 'Tamaulipas', priority: 'Zonas fronterizas y ciudades industriales.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en zonas fronterizas y ciudades industriales.',
      'Información sobre revalidación de domicilio para residentes temporales.',
      'Casillas con cobertura en zonas rurales y fronterizas.',
    ],
    actors: ['INE junta local', 'OPL de Tamaulipas', 'Ayuntamientos', 'Sector privado', 'Consulados'],
    indicators: ['Participación fronteriza/urbana', 'Revalidaciones de domicilio', 'Casillas instaladas'],
  },
  '29': { key: '29', name: 'Tlaxcala', priority: 'Municipios rurales y bachilleratos.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en plazas municipales y centros comunitarios.',
      'Casillas con cobertura en municipios rurales.',
      'Talleres de educación cívica en bachilleratos.',
    ],
    actors: ['INE junta local', 'OPL de Tlaxcala', 'Ayuntamientos', 'Instituciones educativas'],
    indicators: ['Participación municipal', 'Talleres realizados', 'Casillas rurales'],
  },
  '30': { key: '30', name: 'Veracruz de Ignacio de la Llave', priority: 'Municipios de baja participación histórica en sierra y costa.',
    axes: ['Acceso al voto', 'Información cívica', 'Confianza institucional'],
    actions: [
      'Campaña multilingüe (náhuatl, totonaco, huasteco, zapoteco, entre otros) y español.',
      'Red de casillas con cobertura prioritaria en municipios de baja participación histórica.',
      'Brigadas de información casa por casa en zonas rurales y costas.',
      'Difusión en radios comunitarias de la sierra y costa.',
    ],
    actors: ['INE junta local', 'OPL de Veracruz', 'Ayuntamientos', 'Autoridades comunitarias e indígenas', 'Radios comunitarias', 'OSC'],
    indicators: ['Participación por municipio', 'Materiales en lenguas indígenas', 'Brigadas realizadas', 'Casillas en municipios prioritarios'],
  },
  '31': { key: '31', name: 'Yucatán', priority: 'Municipios con población maya y zona conurbada de Mérida.',
    axes: ['Información cívica', 'Acceso al voto', 'Juventud y primer voto'],
    actions: [
      'Campaña en maya y español en municipios con población maya.',
      'Casillas con intérpretes mayas en zonas rurales.',
      'Campaña digital en Mérida y zona conurbada.',
      'Talleres de educación cívica en instituciones educativas.',
    ],
    actors: ['INE junta local', 'OPL de Yucatán', 'Ayuntamientos', 'Autoridades mayas', 'Instituciones educativas'],
    indicators: ['Participación en municipios mayas', 'Casillas con intérprete', 'Alcance digital', 'Talleres realizados'],
  },
  '32': { key: '32', name: 'Zacatecas', priority: 'Zonas mineras, rurales y migrantes.',
    axes: ['Información cívica', 'Acceso al voto', 'Confianza institucional'],
    actions: [
      'Campaña en zonas mineras y rurales con información adaptada a jornadas laborales.',
      'Información dirigida a migrantes y familias con residencia temporal.',
      'Casillas con cobertura en municipios rurales y serranos.',
    ],
    actors: ['INE junta local', 'OPL de Zacatecas', 'Ayuntamientos', 'Organizaciones de migrantes', 'Sector minero'],
    indicators: ['Participación en zonas rurales/mineras', 'Revalidaciones de credencial', 'Casillas instaladas'],
  },
};

function getStatePlan(stateKey){
  return STATE_PLANS[String(stateKey).padStart(2,'0')] || null;
}

if(typeof window!=='undefined'){
  window.STATE_PLANS = STATE_PLANS;
  window.getStatePlan = getStatePlan;
}


/* SOURCE: src/demo6/views/state-profile.js */
/* Ficha descriptiva: conserva siempre el alcance estatal de las fuentes. */
(() => {
  'use strict';
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0});
  const percent=value=>Number.isFinite(value)?value.toFixed(2)+'%':'Sin dato';
  const sourceLink=path=>'../../'+path.split('/').map(encodeURIComponent).join('/');
  const latestObservedRate=(rows)=>{
    for(const year of [2024,2021,2018,2015]){
      const s=UmbralAnalytics.summary(rows,year,'baseline');
      if(Number.isFinite(s.rate)) return {rate:s.rate,year,denominator:s.denominator};
    }
    return null;
  };

  function renderActionPlan(stateKey){
    const title=document.getElementById('d6-action-plan-title');
    const content=document.getElementById('d6-action-plan-content');
    const plan=typeof window!=='undefined'&&window.getStatePlan?window.getStatePlan(stateKey):null;
    if(!title||!content)return;
    if(!plan){
      title.textContent='Plan de acción recomendado';
      content.innerHTML='<p class="d6-note">Selecciona un estado para ver su plan de acción recomendado.</p>';
      return;
    }
    title.textContent=`Plan de acción recomendado · ${escape(plan.name)}`;
    content.innerHTML=`
      <div class="d6-action-plan-body">
        <div class="d6-action-field"><span class="d6-action-label">Prioridad:</span><strong>${plan.priority.charAt(0).toUpperCase()+plan.priority.slice(1)}</strong></div>
        <div class="d6-action-field"><span class="d6-action-label">Ejes estratégicos:</span>${plan.axes.map(a=>`<span class="d6-action-chip">${escape(a)}</span>`).join('')}</div>
        <div class="d6-action-field"><span class="d6-action-label">Enfoque recomendado:</span><p>${escape(plan.priority)}</p></div>
        <div class="d6-action-field"><span class="d6-action-label">Acciones prioritarias:</span><ul class="d6-action-list">${plan.actions.map(a=>`<li>${escape(a)}</li>`).join('')}</ul></div>
        <div class="d6-action-field"><span class="d6-action-label">Actores sugeridos:</span>${plan.actors.map(a=>`<span class="d6-action-chip">${escape(a)}</span>`).join('')}</div>
        <div class="d6-action-field"><span class="d6-action-label">Indicadores de seguimiento:</span>${plan.indicators.map(i=>`<span class="d6-action-chip">${escape(i)}</span>`).join('')}</div>
      </div>
    `;
  }

  if(typeof window!=='undefined'&&window._umbralRuntime){
    window._umbralRuntime.renderProfile=function(selection,records){
      const host=document.getElementById('d6-state-profile');
      const data=window.UMBRAL_FICHAS_ESTATALES;
      if(!host||!data)return;
      const key=selection.state?String(selection.state).padStart(2,'0'):'';
      if(!key){
        host.innerHTML='<div class="d6-profile-empty"><span class="eyebrow">CONTEXTO ANTES DE SIMULAR</span><h3>Consulta la ficha de tu estado</h3><p>Selecciona un estado en el mapa para ver sus antecedentes, contexto poblacional y documentos de referencia. Al entrar a un municipio se conserva la ficha estatal.</p><a href="#modulo-1">Elegir estado en el mapa ↑</a></div>';
        document.getElementById('d6-action-plan-title').textContent='Plan de acción recomendado';
        document.getElementById('d6-action-plan-content').innerHTML='<p class="d6-note">Selecciona un estado para ver su plan de acción recomendado.</p>';
        return;
      }
      const rows=records.filter(r=>String(r.state).padStart(2,'0')===key);
      const info=data.states[key];
      const name=rows[0]?.state_name||info?.name||key;
      const municipality=selection.municipality&&rows.find(r=>r.key===selection.municipality);
      const card=(label,value,note)=>`<article><span>${escape(label)}</span><strong>${escape(value)}</strong><small>${escape(note)}</small></article>`;
      const history=[2015,2018,2021,2024].map(year=>{
        const s=UmbralAnalytics.summary(rows,year,'baseline');
        return `<tr><td>${year}</td><td>${percent(s.rate)}</td><td>${s.valid} / ${s.total}</td></tr>`;
      }).join('');
      const latest=latestObservedRate(rows);
      host.innerHTML=`<div class="d6-profile-heading"><div><span class="eyebrow">FICHA INFORMATIVA ESTATAL · ${escape(key)}</span><h3>${escape(name)}</h3></div><span class="d6-profile-badge">Datos y fuentes</span></div>
        <p class="d6-profile-scope">${municipality?`Estás consultando ${escape(municipality.name)}. Esta ficha corresponde a todo ${escape(name)}; sus cifras no son las del municipio.`:'Contexto de toda la entidad, independiente del filtro de municipios con proyección.'}</p>
        <div class="d6-profile-stats">${card('Población · 2024',info?.population?.['2024']?number.format(info.population['2024']):'Sin dato','Serie demográfica aportada; no lista nominal')}${card('Población · 2027',info?.population?.['2027']?number.format(info.population['2027']):'Sin dato','Proyección demográfica; no electores esperados')}${card('Municipios en la serie · 2027',info?.municipalities?.['2027']??'Sin dato','Cobertura del archivo demográfico')}</div>
        <div class="d6-profile-body"><section><h4>Antecedentes observados del estado</h4><div class="table-wrap"><table><thead><tr><th>Elección</th><th>Abstención</th><th>Municipios con dato</th></tr></thead><tbody>${history}</tbody></table></div><p class="d6-note">Promedios ponderados por SV + NV del año. Se usan todos los registros de la entidad, incluidos los que no tienen proyección para 2027. Presidenciales e intermedias tienen contextos distintos.</p></section><section><h4>Qué permiten conocer estas fuentes</h4><p>Los conteos describen lo ocurrido y las series demográficas aportan contexto poblacional. Los documentos complementan la lectura con metodología, cultura cívica y antecedentes institucionales.</p><p>No identifican por sí solos por qué una persona no votó ni demuestran qué acción funcionaría en este estado.</p><p class="d6-note">${escape(data.population_definition)}</p></section></div>
        <details class="d6-profile-sources"><summary>Documentos revisados y alcance de cada fuente</summary><div class="d6-source-grid">${data.sources.map(s=>`<article><span class="eyebrow">${escape(s.scope)}</span><h4>${escape(s.title)}</h4><p>${escape(s.note)}</p><a href="${sourceLink(s.path)}" target="_blank" rel="noopener">Consultar fuente local ↗</a></article>`).join('')}</div><p class="d6-note">También se revisaron los seis CSV de Bases_de_datos_explicativos. No se suman archivos solapados: la población mostrada procede únicamente de pobproy_ggrupos.csv. Las series de defunciones no se interpretan como motivos de abstención.</p><a href="data/fichas_estatales.json" download>Descargar datos, inventario y huellas de las fuentes ↓</a></details>`;
      renderActionPlan(key);
    };
    runtime.renderProfile=window._umbralRuntime.renderProfile;
  }
})();


/* SOURCE: src/demo6/views/state-context.js */
/* Ficha descriptiva: conserva siempre el alcance estatal de las fuentes. */
(() => {
  'use strict';
  const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const number=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0});
  const percent=value=>Number.isFinite(value)?value.toFixed(2)+'%':'Sin dato';
  const sourceLink=path=>'../../'+path.split('/').map(encodeURIComponent).join('/');
  runtime.renderProfile=function(selection,records){
    const host=document.getElementById('d6-state-profile');
    const data=window.UMBRAL_FICHAS_ESTATALES;
    if(!host||!data)return;
    const key=selection.state?String(selection.state).padStart(2,'0'):'';
    if(!key){
      host.innerHTML='<div class="d6-profile-empty"><span class="eyebrow">CONTEXTO ANTES DE SIMULAR</span><h3>Consulta la ficha de tu estado</h3><p>Selecciona un estado en el mapa para ver sus antecedentes, contexto poblacional y documentos de referencia. Al entrar a un municipio se conserva la ficha estatal.</p><a href="#modulo-1">Elegir estado en el mapa ↑</a></div>';
      return;
    }
    const rows=records.filter(r=>String(r.state).padStart(2,'0')===key);
    const info=data.states[key];
    const name=rows[0]?.state_name||info?.name||key;
    const municipality=selection.municipality&&rows.find(r=>r.key===selection.municipality);
    const card=(label,value,note)=>`<article><span>${escape(label)}</span><strong>${escape(value)}</strong><small>${escape(note)}</small></article>`;
    const history=[2015,2018,2021,2024].map(year=>{
      const s=UmbralAnalytics.summary(rows,year,'baseline');
      return `<tr><td>${year}</td><td>${percent(s.rate)}</td><td>${s.valid} / ${s.total}</td></tr>`;
    }).join('');
    host.innerHTML=`<div class="d6-profile-heading"><div><span class="eyebrow">FICHA INFORMATIVA ESTATAL · ${escape(key)}</span><h3>${escape(name)}</h3></div><span class="d6-profile-badge">Datos y fuentes</span></div>
      <p class="d6-profile-scope">${municipality?`Estás consultando ${escape(municipality.name)}. Esta ficha corresponde a todo ${escape(name)}; sus cifras no son las del municipio.`:'Contexto de toda la entidad, independiente del filtro de municipios con proyección.'}</p>
      <div class="d6-profile-stats">${card('Población · 2024',info?.population?.['2024']?number.format(info.population['2024']):'Sin dato','Serie demográfica aportada; no lista nominal')}${card('Población · 2027',info?.population?.['2027']?number.format(info.population['2027']):'Sin dato','Proyección demográfica; no electores esperados')}${card('Municipios en la serie · 2027',info?.municipalities?.['2027']??'Sin dato','Cobertura del archivo demográfico')}</div>
      <section class="d6-action-plan" id="d6-action-plan" aria-labelledby="d6-action-plan-title">
        <h4 id="d6-action-plan-title">Plan de acción recomendado</h4>
        <div id="d6-action-plan-content"></div>
      </section>
      <div class="d6-profile-body"><section><h4>Antecedentes observados del estado</h4><div class="table-wrap"><table><thead><tr><th>Elección</th><th>Abstención</th><th>Municipios con dato</th></tr></thead><tbody>${history}</tbody></table></div><p class="d6-note">Promedios ponderados por SV + NV del año. Se usan todos los registros de la entidad, incluidos los que no tienen proyección para 2027. Presidenciales e intermedias tienen contextos distintos.</p></section><section><h4>Qué permiten conocer estas fuentes</h4><p>Los conteos describen lo ocurrido y las series demográficas aportan contexto poblacional. Los documentos complementan la lectura con metodología, cultura cívica y antecedentes institucionales.</p><p>No identifican por sí solos por qué una persona no votó ni demuestran qué acción funcionaría en este estado.</p><p class="d6-note">${escape(data.population_definition)}</p></section></div>
      <details class="d6-profile-sources"><summary>Documentos revisados y alcance de cada fuente</summary><div class="d6-source-grid">${data.sources.map(s=>`<article><span class="eyebrow">${escape(s.scope)}</span><h4>${escape(s.title)}</h4><p>${escape(s.note)}</p><a href="${sourceLink(s.path)}" target="_blank" rel="noopener">Consultar fuente local ↗</a></article>`).join('')}</div><p class="d6-note">También se revisaron los seis CSV de Bases_de_datos_explicativos. No se suman archivos solapados: la población mostrada procede únicamente de pobproy_ggrupos.csv. Las series de defunciones no se interpretan como motivos de abstención.</p><a href="data/fichas_estatales.json" download>Descargar datos, inventario y huellas de las fuentes ↓</a></details>`;
  };
})();


/* SOURCE: src/demo6/views/summary.js */
/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  runtime.views=runtime.views||{};
  runtime.views.renderSummary=function({A,state,selectedRecords,territoryLabel,records,view,name,$,pct,fmt,esc}){
  function metricCard(label,value,note){
    return `<article><span>${esc(label)}</span><strong>${value}</strong><small>${esc(note)}</small></article>`;
  }
    const rows=selectedRecords();
    const s=A.summary(rows,state.year,state.method);
    const model=state.year===2027?'Proyección · '+name(state.method):'Datos observados';
    $('d6-selection-label').textContent=territoryLabel()+' · '+state.year+' · '+model;
    $('d6-summary').innerHTML=metricCard('Abstención',pct(s.rate),'Promedio ponderado por SV + NV')+
      metricCard('Participación',pct(s.participation),state.year===2027?'Proyección complementaria':'Entre personas con dato de voto')+
      metricCard('Municipios con dato',fmt.format(s.valid)+' / '+fmt.format(s.total),s.missing+' sin dato o sin estimación')+
      metricCard('Cobertura de población',pct(s.populationCoverage),'Sobre la base observable del filtro');
    $('d6-summary-note').textContent='Base con tasa disponible: '+fmt.format(s.denominator)+' personas. '+
      (state.year===2027?'Se usa SV+NV 2024; no representa el electorado proyectado de 2027.':'SV+NV del año seleccionado, reconstruido desde LN y NS%.')+
      ' Los municipios sin dato no se cuentan como cero. La cobertura describe el filtro actual.';
    const stateRows=A.subset(view.length?view:records,state,{municipality:false});
    const st=A.summary(stateRows,state.year,state.method);
    const delta=Number.isFinite(s.rate)&&Number.isFinite(st.rate)?s.rate-st.rate:null;
    $('d6-context').hidden=!state.municipality;
    $('d6-context').innerHTML=`<span>Promedio de ${esc(records.find(r=>r.state===state.state)?.state_name||'la entidad')}: <strong>${pct(st.rate)}</strong></span><span>Brecha del municipio: <strong>${Number.isFinite(delta)?(delta>=0?'+':'')+delta.toFixed(2)+' pp':'Sin comparación'}</strong></span>`;
    $('d6-export').disabled=!rows.length;
  };
})();


/* SOURCE: src/demo6/views/history.js */
/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  runtime.views=runtime.views||{};
  runtime.views.renderHistory=function({A,state,selectedRecords,territoryLabel,view,$,pct,fmt,esc}){
  function segments(points,kind){
    let result='',previous=null;
    for(const p of points){
      if(!Number.isFinite(p.rate)){previous=null;continue;}
      if(previous)result+=`<path class="${p.year===2027?'d6-forecast':kind}" d="M${previous.x},${previous.y} L${p.x},${p.y}"/>`;
      previous=p;
    }
    return result;
  }
    const rows=selectedRecords();
    const values=A.series(rows,state.method,state.year);
    const years=values.map(v=>v.year);
    const reference=state.municipality?A.series(A.subset(view,state,{municipality:false}),state.method,state.year):[];
    const x=year=>58+(year-2009)/18*610,y=rate=>234-rate*2;
    const points=values.map(v=>({...v,x:x(v.year),y:y(v.rate)}));
    const ref=reference.map(v=>({...v,x:x(v.year),y:y(v.rate)}));
    const grid=[0,25,50,75,100].map(n=>`<line class="d6-axis" x1="58" x2="668" y1="${y(n)}" y2="${y(n)}"/><text x="48" y="${y(n)+4}" text-anchor="end">${n}%</text>`).join('');
    const dots=points.filter(p=>Number.isFinite(p.rate)).map(p=>`<circle cx="${p.x}" cy="${p.y}" r="5" fill="${p.year===2027?'#fffdf8':'#10685f'}" stroke="#10685f" stroke-width="2"><title>${p.year}: ${pct(p.rate)} · ${p.valid}/${p.total} municipios</title></circle>`).join('');
    $('d6-history-chart').innerHTML=`<svg class="d6-chart" viewBox="0 0 720 280" role="img" aria-label="Evolución de la abstención de ${esc(territoryLabel())}">${grid}${segments(ref,'d6-reference')}${segments(points,'d6-observed')}${dots}${years.map(year=>`<text x="${x(year)}" y="260" text-anchor="middle">${year}</text>`).join('')}</svg>`;
    $('d6-reference-legend').hidden=!state.municipality;
    $('d6-forecast-legend').hidden=state.year!==2027;
    $('d6-history-table').innerHTML=values.map(v=>`<tr><td>${v.year}${v.year===2027?' · Proyección':''}</td><td>${pct(v.rate)}</td><td>${v.valid}/${v.total}</td><td>${fmt.format(v.denominator)}</td></tr>`).join('');
  };
})();


/* SOURCE: src/demo6/views/evidence.js */
/* Vista descriptiva; dependencias recibidas explícitamente. */
(() => {
  'use strict';
  runtime.views=runtime.views||{};
  runtime.views.renderEvidence=function({state,metadata,name,$,fmt,esc}){
    const rows=[];
    const comparison=metadata.comparison_report;
    for(const [year,cut] of Object.entries(comparison.cuts)){
      for(const key of ['baseline','ridge','hgb','lightgbm','catboost']){
        const v=cut.models[key],timing=v.timing;
        rows.push(`<tr><td>${year}</td><td>${key==='baseline'?'Referencia homóloga':name(key)}</td><td>${fmt.format(v.n)}</td><td>${v.mae.toFixed(2)}</td><td>${v.mae_ponderado.toFixed(2)}</td><td>${Math.round(v.precision_top*v.top_k)}/${v.top_k}</td><td>${timing?(timing.fit_seconds_median*1000).toFixed(1):'No aplica'}</td><td>${timing?(timing.predict_seconds_median*1000).toFixed(2):'No medido'}</td></tr>`);
      }
    }
    $('d6-metrics').innerHTML=rows.join('');
    const selected=comparison.aggregates[comparison.selected_model];
    $('d6-model-note').textContent=`Comparamos cuatro modelos con las mismas 15 variables y cohortes. Seleccionado: ${name(comparison.selected_model)}, MAE medio ${selected.mean_mae.toFixed(3)} pp y ponderado ${selected.mean_weighted_mae.toFixed(3)} pp entre 2021 y 2024. LightGBM y HistGradientBoosting quedaron dentro de 0.05 pp de MAE; el desempate favoreció el menor error ponderado de HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva y no valida 2027. En 2024 la referencia conserva más aciertos top50 que el ganador.`;
    $('d6-method-note').textContent=state.year===2027?name(state.method)+'. '+
      (state.method==='baseline'?'Repite la abstención de 2021, última intermedia observada.':'Ajusta la referencia con antecedentes y variables agregadas. No garantiza una mejora en todas las elecciones.'):
      'Los porcentajes históricos son observados. El método no modifica los resultados de '+state.year+'.';
    const labels={abstencion_mismo_tipo:'Abstención en elección homóloga',abstencion_ultimo_proceso:'Abstención del último proceso',diferencia_ultimo_mismo:'Diferencia entre antecedentes',log_lista_nominal:'Tamaño de lista nominal (log)',proporcion_18_29:'Proporción de 18–29 años',proporcion_60_mas_sin_extremos:'Proporción de 60 años o más',proporcion_urbana:'Proporción urbana',eleccion_intermedia:'Tipo de elección'};
    const factors=metadata.coefficients_standardized.filter(v=>Number.isFinite(v.coefficient)).slice().sort((a,b)=>Math.abs(b.coefficient)-Math.abs(a.coefficient)).slice(0,8);
    const max=Math.max(1,...factors.map(v=>Math.abs(v.coefficient)));
    $('d6-factors').innerHTML=factors.map(v=>`<div class="d6-factor"><span>${esc(labels[v.feature]||v.feature.replaceAll('_',' '))}</span><div class="d6-factor-track"><i class="${v.coefficient<0?'negative':''}" style="width:${Math.abs(v.coefficient)/max*100}%"></i></div><strong>${v.coefficient>0?'+':''}${v.coefficient.toFixed(2)}</strong></div>`).join('');
  };
})();


/* SOURCE: src/demo6/controller.js */
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
    runtime.renderProfile?.(state,records);
    $('method').disabled=state.year!==2027;
    $('modulo-3').hidden=state.year!==2027;
    $('d6-historical-notice').hidden=state.year===2027;
    const nav=document.querySelector('.quick-nav a[href="#modulo-3"]');
    if(nav)nav.hidden=state.year!==2027;
    const historical=state.year!==2027;
    $('analysis-eligible-label').textContent=historical?'Con dato observado en '+state.year:'Con estimación en tu búsqueda';
    $('analysis-missing-label').textContent=historical?'Sin dato observado en '+state.year:'Sin estimación en tu búsqueda';
    $('analysis-ranking-label').textContent=historical?'No votaron en '+state.year:'Podrían no votar en 2027';
    $('analysis-description').textContent=historical?'Resultados observados de '+state.year+', participación y calidad de los datos del territorio seleccionado.':'Consulta antecedentes, proyección exploratoria de 2027 y diferencias entre métodos. La comparación con el estado usa el mismo método y filtro de catálogo.';
    $('map-year-hint').textContent=historical?'Datos observados de '+state.year+'. Puedes cambiar de año conservando la selección.':'Proyección exploratoria de 2027. Compara Ridge con la referencia de 2021.';
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
      const content=A.csv(selectedRecords(),state,metadata);
      const url=URL.createObjectURL(new Blob([content],{type:'text/csv;charset=utf-8'}));
      const a=document.createElement('a');a.href=url;a.download='Umbral_consulta_'+(state.municipality||state.state||'Mexico')+'_'+state.year+'.csv';
      a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
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


/* SOURCE: src/demo6/app/start.js */
/* Arranque síncrono después de cargar datos y definiciones; sin sondeos por intervalos. */
try{
  load();
  initMapDecorations();
  initMapLayers();
  if(!runtime.startController())throw Error('No se pudo iniciar el controlador de demo6');
  document.dispatchEvent(new CustomEvent('umbral:ready'));
}catch(error){
  $('status').textContent='No se pudo iniciar la aplicación. Revisa los recursos locales.';
  console.error(error);
}


})();

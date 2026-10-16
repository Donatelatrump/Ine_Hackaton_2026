'use strict';
let stateLayer, stateSummaries = new Map(), stateGeographyDirty = true, municipalMapText;
let geographyFocusKey = null;
const geographyHistory = [];
function rememberGeographyView() {
 geographyHistory.push({state:$('state').value,search:$('search').value,
  key:geographyFocusKey,detailKey:activeKey});
}
function goBackGeography() {
 const previous = geographyHistory.pop();
 console.log('LOG pop', JSON.stringify(previous), '| resto', geographyHistory.length, '| stateGuardado', $('state').value, '| focus', geographyFocusKey, '| activo', (typeof demo5EstadoActivo!=='undefined'?demo5EstadoActivo:'-'));
 if(!previous){
  if(geographyFocusKey){
   geographyFocusKey = null;
   paintMunicipalityFocus();
   const statePolygon = stateLayer.getLayers().find(p=>p.feature.properties.state===$('state').value);
   map.fitBounds(statePolygon?statePolygon.getBounds():layer.getBounds(),{padding:[12,12]});
  }else if($('state').value){returnToMexico();}
  console.log('LOG rama returnToMexico (sin historial y con estado)');
  return;
 }
  $('state').value = previous.state;
  $('search').value = previous.search;
  geographyFocusKey = previous.key;
  activeKey = previous.detailKey;
  if(typeof demo5EstadoActivo !== 'undefined' && previous.state === '') demo5EstadoActivo = null;
  console.log('LOG restaura state', $('state').value, '| search', $('search').value, '| key', previous.key, '| activo', (typeof demo5EstadoActivo!=='undefined'?demo5EstadoActivo:'-'));
  update();  const polygon = previous.key?layer.getLayers().find(p=>p.feature.properties.key===previous.key):
  previous.state?stateLayer.getLayers().find(p=>p.feature.properties.state===previous.state):null;
 const bounds = polygon?(polygon.getBounds()):(layer.getBounds());
 console.log('LOG bounds: poligono hallado', !!polygon, '| ext', (bounds.getNorth()-bounds.getSouth()).toFixed(1), '| state', $('state').value);
 map.fitBounds(bounds,{padding:[12,12],maxZoom:previous.key?10:undefined});
}
const municipalBaseStyles = new Map();
function paintMunicipalityFocus() {
  if(typeof demo5ModoHistorico !== 'undefined' && demo5ModoHistorico && demo5EstadoActivo) return;
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
  rememberGeographyView();
 const municipality = byKey.get(key);
 if($('search').value !== municipality.name){
  $('search').value = municipality.name;
  update();
 }
 geographyFocusKey = key;
 paintMunicipalityFocus();
 detail(key);
 map.fitBounds(polygon.getBounds(), {padding:[30,30],maxZoom:10});
}
function returnToMexico() {
  geographyHistory.length = 0;
  geographyFocusKey = null;
  $('state').value = '';
  $('search').value = '';
  if(typeof demo5EstadoActivo !== 'undefined') demo5EstadoActivo = null;
  update();
 map.fitBounds(layer.getBounds(), {padding:[12,12]});
 setTimeout(()=>{ map.invalidateSize(); }, 80);
 if(typeof focusMunicipality==='function'){ focusMunicipality=null; }
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
 stateLayer = L.geoJSON(window.UMBRAL_STATES, {renderer:L.canvas({pane:'state-geography'}),onEachFeature:(feature, polygon)=>{
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
  console.log('LOG updateGeography dataChanged', dataChanged, '| state', $('state').value, '| activo', (typeof demo5EstadoActivo!=='undefined'?demo5EstadoActivo:'-'), '| modoHistorico', (typeof demo5ModoHistorico!=='undefined'?demo5ModoHistorico:'-'));
  if(typeof demo5ModoHistorico !== 'undefined' && demo5ModoHistorico && demo5EstadoActivo) return;
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
  console.log('LOG paneles %s | estados %s | municipios %s', $('state').value, statesOn?'visible':'hidden', statesOn?'hidden':'visible');
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

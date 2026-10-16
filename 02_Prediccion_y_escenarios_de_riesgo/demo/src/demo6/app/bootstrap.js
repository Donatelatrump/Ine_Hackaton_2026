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


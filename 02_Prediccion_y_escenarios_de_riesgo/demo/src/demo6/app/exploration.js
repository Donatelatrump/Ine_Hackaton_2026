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

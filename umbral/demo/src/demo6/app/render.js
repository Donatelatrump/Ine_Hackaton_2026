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
 $('simulation-prompt').textContent=simOn&&!budgetValid?'Introduce un número entero de personas entre 0 y 200,000,000 para calcular el escenario.':'Elige una acción para configurar la cobertura y comparar los resultados.';
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

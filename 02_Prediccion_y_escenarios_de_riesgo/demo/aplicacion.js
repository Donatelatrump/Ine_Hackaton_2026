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
function perfilCell(key,year,dim,group){try{return perfil.municipios[key][String(year)][dim][group];}catch(e){return null;}}
function perfilRow(key,dim,group,minN=500){
 const cell=perfilCell(key,2024,dim,group),natNac=perfil.nacional['2024'][dim][group];
 const label=`${GROUP_NAME[dim]?GROUP_NAME[dim][group]||group:group}`;
 if(!cell||cell.abstencion_pct===null||cell.n<minN)return `<li>${esc(label)}: muestra insuficiente para inferir (n=${fmt.format(cell?cell.n:0)})</li>`;
 const diff=cell.abstencion_pct-natNac.abstencion_pct,sign=diff>=0?'+':'';
 return `<li>${esc(label)}: <strong>${cell.abstencion_pct.toFixed(1)}%</strong> de abstención observada (${sign}${diff.toFixed(1)} pp frente al patrón nacional; n=${fmt.format(cell.n)})</li>`;
}
function detail(key){
 activeKey=key;const r=byKey.get(key);
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
 const inv=$('action').value==='personalizada'?Decision.inverseScenario(r,chosen?.served||0,Number($('response').value),thresholds):{reason:'La inversión de respuesta solo aplica al escenario personalizado. El efecto del estudio seleccionado permanece fijo; no se ajusta para cambiar el color.'};
 const p=preventive(r);
 const refRank=rankUnder(key,'baseline'),ridgeRank=rankUnder(key,'ridge'),capacityNow=plan.selected.length;
 $('detail-name').textContent=r.name;$('detail-state').textContent=r.state_name+' · Clave INE '+r.key+(simulationActive()?' · Prioridad '+pos+' de '+total:'');
 const last=r.history.length?r.history[r.history.length-1]:null;
 const reasons=[];
 if(Number.isFinite(r.baseline))reasons.push(`Abstención en la elección comparable (2021): <strong>${pct(r.baseline)}</strong>`);
 if(last&&Number.isFinite(last.risk))reasons.push(`Último proceso (${last.year}): <strong>${pct(last.risk)}</strong>`);
 if(Number.isFinite(r.profile.urban_pct))reasons.push(`Personas registradas en zonas urbanas: ${pct(r.profile.urban_pct)}`);
 if(Number.isFinite(r.latest_ns))reasons.push(`Registros de 2024 sin información sobre si votaron: <strong>${pct(r.latest_ns)}</strong>`);
 const bothHigh=capacityNow>0&&refRank<=capacityNow&&ridgeRank<=capacityNow;
 if(simulationActive())reasons.push(`La referencia de 2021 (puesto ${refRank||'—'}) y la estimación con datos históricos (puesto ${ridgeRank||'—'}): ${bothHigh?'coinciden dentro de la capacidad actual':(refRank<=capacityNow||ridgeRank<=capacityNow)?'solo uno entra en la selección con la capacidad actual':'ninguno entra en la selección con la capacidad actual'}`);
 const mem=s.members||{},any=(vs)=>vs.some(v=>mem[v]);
 const robustez=[
  ['Ridge (alguna variante)',any(['ridge_5','ridge_10','ridge_20'])],
  ['Referencia (alguna variante)',any(['persistencia_5','persistencia_10','persistencia_20'])],
  ['NS ≤5%',any(['ridge_5','persistencia_5'])],
  ['NS ≤10%',any(['ridge_10','persistencia_10'])],
  ['NS ≤20%',any(['ridge_20','persistencia_20'])],
 ].map(([label,ok])=>`<li>${label}: ${ok?'✅':'—'}</li>`).join('');
 const req=inv.reason?esc(inv.reason):`Para bajar un nivel, objetivo &lt; ${pct(inv.target+1e-6)}: alcance requerido ≈ ${inv.required_reach===null?'imposible con respuesta cero':fmt.format(inv.required_reach)} personas con respuesta ${$('response').value}%. ${inv.feasible_reach?'Cabe en la base observable.':'No cabe en la base observable con esa respuesta.'} Con el alcance actual, respuesta requerida ${pct(inv.required_response)} ${inv.feasible_response?'(≤100%).':'(no factible o sin alcance).'} Requisito algebraico hipotético.`;
 const profile=(perfil&&perfil.municipios[key])?`<h3>Perfil CCPC observado 2024 (capa explicativa)</h3><ul class="why">${['18_29','60_mas'].map(g=>perfilRow(key,'edad',g)).join('')}${perfilRow(key,'sexo','hombres')}${perfilRow(key,'sexo','mujeres')}${perfilRow(key,'seccion','urbana')}${perfilRow(key,'seccion','rural')}</ul><p class="table-note hint">Capa descriptiva posterior: no alimenta a Ridge ni a la prioridad. Las diferencias frente al promedio nacional no son efectos.</p>`:'';
 $('detail-content').innerHTML=`<h3>¿Qué ocurrió en elecciones anteriores?</h3><div class="fact-cards">
  <div><span>Dato observado · ${last?last.year:'sin antecedente'}</span><strong>${last?pct(last.risk):'Sin dato'}</strong><small>${last&&Number.isFinite(last.risk)?"Aproximadamente "+Math.round(last.risk)+" de cada 100 personas no votaron":"Sin dato disponible"}</small></div>
  </div><h3>¿Qué se estima para 2027?</h3><div class="fact-cards"><div><span>Estimación exploratoria · 2027</span><strong>${pct(r.risk)}</strong><small>Aproximadamente ${Math.round(r.risk)} de cada 100 personas podrían no votar. Es una estimación.</small></div>
  ${simulationActive()?`<div><span>Con la acción del paso 3</span><strong>${chosen?pct(chosen.after):'Sin asignación'}</strong><small>${chosen?fmt.format(chosen.served)+' personas alcanzadas (supuesto)':'Fuera del plan actual'}</small></div>`:''}</div><p class="detail-limit">La cifra de 2027 es exploratoria. No sabemos todavía qué tan precisa será; 2024 y 2027 son elecciones de distinto tipo.</p>
  <details><summary>Antecedentes y calidad de los datos</summary><ul class="why">${reasons.map(x=>`<li>${x}</li>`).join('')}</ul></details>
  ${simulationActive()?`<details><summary>Acción elegida y revisión del plan</summary><h3>Acción del simulador</h3><p>${esc(plan.action.label)}. ${esc(plan.action.unit)}. ${plan.action.source?`<a href="${esc(plan.action.source)}" target="_blank" rel="noopener noreferrer">Fuente original ↗</a>`:"Sin coeficiente externo."}</p>`:''}<details><summary>Qué actividad podría explorarse en este municipio</summary><h3>Recomendación preventiva por validar</h3><p><strong>Acción sugerida: ${esc(p.type)}.</strong> ${esc(p.action)}.</p><p class="hint">Propuesta por validar con la comunidad. ${esc(p.mechanism)}.</p>
  </details>${simulationActive()?`<h3>¿Qué debemos comprobar antes de aplicarla?</h3><p>Este municipio aparece entre los seleccionados en <strong>${s.count} de las 6 formas de comparar los datos</strong>. ${s.robust?'Seleccionado en todas las variantes.':s.count>0?'La selección depende del método o de la calidad.':'No entra en las variantes con la capacidad actual.'} Tiene datos suficientes para ${s.eligible} de esas 6 comparaciones. </p>
  ${r.exclusion_reasons.length?`<div class="evidence-note">${r.exclusion_reasons.map(esc).join('<br>')}</div>`:''}
  <p>${esc(p.conditions)}.</p></details>`:''}
  <details><summary>Consultar el perfil observado por grupos</summary>${profile||'<p>Sin perfil desagregado disponible.</p>'}</details>
  <details><summary>Responsable, cobertura, recurso y evaluación</summary><dl class="prevention">${Object.entries({Responsable:p.responsible,Cobertura:p.coverage,Recurso:p.resource,'Cómo evaluarla':p.measurement}).map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details>
  ${simulationActive()?`<details><summary>Avanzado: qué haría falta para cambiar de color</summary><p>${req}</p></details>`:''}
  ${simulationActive()?`<details><summary>Cómo cambia la selección entre variantes</summary><ul class="why">${robustez}</ul><p>Frecuencia de selección ${s.count}/6. Se usa un número equivalente de municipios; no se recalcula el presupuesto humano por variante.</p></details>`:''}
  <details><summary>Ver elecciones anteriores y límites de la estimación</summary><div class="history">${r.history.map(h=>`<div><span>${h.year}</span><div class="bar-track"><i style="width:${Number.isFinite(h.risk)?h.risk:0}%"></i></div><b>${pct(h.risk)}</b></div>`).join('')}</div><p>${simulationActive()?'La prioridad se comunica con la frecuencia entre variantes. ':''}El rango técnico ${pct(r.range_low)}–${pct(r.range_high)} (±21.05 pp, p90 retrospectivo de Ridge 2021) se conserva solo aquí como referencia de error histórico; no es intervalo prospectivo.</p><p>${r.flags.map(esc).join('; ')||'Sin alertas adicionales'}</p></details>`;
}
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
function update(){
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
 const confOn=$('confidence').checked;layer.setStyle(f=>{const r=byKey.get(f.properties.key),s=hasResults?selectedMap.get(r.key):null,visible=matches(r),after=s?s.after:r.risk,delta=s?r.risk-s.after:0;let color=colors[Decision.level(mode==='intervencion'?after:r.risk,thresholds)];if(mode==='cambio')color=!Number.isFinite(r.risk)?colors.sin_datos:delta>5?'#135e87':delta>1?'#4b94b8':delta>0?'#9dccdf':'#f6faf9';if(confOn&&Number.isFinite(r.risk)&&visible)color=stability[r.key]?.robust?'#176b58':'#ddb263';return {color:s?'#173c34':'#ffffff',weight:s?1.7:.3,fillColor:color,fillOpacity:visible?.85:!Number.isFinite(r.risk)?.6:.25,opacity:visible?1:.65};});
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
function exportPlan(){
 const LENS_LABEL={tasa:'Mayor porcentaje',volumen:'Mayor volumen',deterioro:'Mayor deterioro'},METHOD_LABEL={ensamble:'Ensamble adaptativo (+8.2% precisión)',ridge:'Estimación regularizada (Ridge)',baseline:'Referencia: elección de 2021'};
 const headers=['Puesto','Clave INE','Entidad','Municipio','No votarían (estimado 2027, %)','No votarían (con acción, %)','Reducción (pp)','Personas alcanzadas (supuesto)','Respuesta supuesta (%)','Personas adicionales que votarían (supuesto)','Base observable 2024 (SV+NV)','Lista nominal 2024','Sin dato de voto (%)','Confianza de prioridad','Aparece en variantes (de 6)','Variantes con datos (de 6)','Núcleo robusto (6/6)','Catálogo constante','Criterio de prioridad','Tipo de acción','Acción propuesta','Responsable propuesto','Condiciones de validación','Recursos','Cómo evaluarla','Nota metodológica','Acción simulada','Estimador del estudio','Unidad de cobertura','Efecto de referencia (pp)','Fuente bibliográfica','URL fuente','Incertidumbre del estudio','Votos adicionales límite inferior','Votos adicionales límite superior','Distribución de cobertura'];
 const titleCase=v=>String(v).toLowerCase().replace(/(^|[\s\-])([a-záéíóúüñ])/g,(m,p,c)=>p+c.toUpperCase()),num=v=>Number.isFinite(v)?String(Math.round(v)):'',dec=v=>Number.isFinite(v)?v.toFixed(4):'',bool=v=>v?'Sí':'No';
 const ranked=Decision.rank(filtered,$('lens').value),response=Number($('response').value),action=plan.action;
 const lines=plan.selected.map((r,i)=>{const s=stability[r.key]||{count:0,eligible:0,robust:false},c=s.confidence||Decision.confidenceTier(s.count,6),p=preventive(r);return [i+1,r.key,titleCase(r.state_name),titleCase(r.name),dec(r.risk),dec(r.after),dec(r.risk-r.after),num(r.served),action.id==='personalizada'?response:'',r.additional.toFixed(4),num(r.observed),num(r.ln),dec(r.latest_ns),TIER[c.tier],s.count,s.eligible,bool(s.robust),bool(r.stable_catalog_state),LENS_LABEL[$('lens').value],p.type,p.action,p.responsible,p.conditions,p.resource,p.measurement,'Hipótesis no causal; la frecuencia no es probabilidad; base observable histórica (SV+NV 2024), sin NS; límites sin armonizar',action.label,action.estimand,action.unit,action.effect_pp??'',action.citation||'Sin fuente causal: supuesto del usuario',action.source||'',action.uncertainty||'No disponible',r.additional_low??'',r.additional_high??'',plan.distribution];});
 const cell=v=>{let s=String(v??'');if(typeof v==='string'&&/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
 const dic={'Puesto':'Orden en la prioridad del plan actual','Clave INE':'Clave de municipio del catálogo INE','Entidad':'Estado','Municipio':'Nombre del municipio','No votarían (estimado 2027, %)':'Estimación exploratoria del método activo','No votarían (con acción, %)':'Escenario hipotético tras la acción simulada','Reducción (pp)':'Estimación menos escenario, en puntos porcentuales','Personas alcanzadas (supuesto)':'Contacto simulado, limitado por la base observable','Respuesta supuesta (%)':'Cambio de decisión supuesto entre alcanzados que no votarían','Personas adicionales que votarían (supuesto)':'Evidencia: cobertura por efecto pp/100, limitada por abstención esperada cubierta. Personalizado: cobertura por tasa por respuesta. Transferencia hipotética.','Base observable 2024 (SV+NV)':'Personas con registro de si votaron en 2024; denominador y tope de alcance','Lista nominal 2024':'Lista nominal electoral 2024','Sin dato de voto (%)':'Participación no especificada (NS) en 2024','Confianza de prioridad':'Frecuencia de selección entre seis variantes, agrupada','Aparece en variantes (de 6)':'Variantes que lo seleccionan','Variantes con datos (de 6)':'Variantes con datos suficientes para evaluarlo','Núcleo robusto (6/6)':'Seleccionado en las seis variantes','Catálogo constante':'Estado con listado municipal sin cambios entre cortes','Criterio de prioridad':'Lente activa al exportar','Tipo de acción':'Tipología preventiva sugerida por perfil municipal','Acción propuesta':'Actividad concreta para validar con el área usuaria','Responsable propuesto':'Instancia propuesta; validar atribuciones y capacidad','Condiciones de validación':'Qué comprobar antes de implementar','Recursos':'Recursos registrables; sin costos inventados','Cómo evaluarla':'Métricas de seguimiento sugeridas','Nota metodológica':'Límites que aplican a toda la tabla'};
 Object.assign(dic,{'Distribución de cobertura':'Regla propia del proyecto: prioridad por ranking o proporcional a SV+NV 2024 con mayor resto','Acción simulada':'Acción elegida en el simulador; distinta de la recomendación preventiva por perfil','Estimador del estudio':'ITT sobre asignados o ATT ajustado por contacto; supuesto en personalizado','Unidad de cobertura':'Denominador correspondiente al estimador','Efecto de referencia (pp)':'Aumento publicado de participación; no respuesta entre abstencionistas','Fuente bibliográfica':'Publicación original del coeficiente','URL fuente':'Enlace DOI a la publicación','Incertidumbre del estudio':'Intervalo o error estándar original; no incertidumbre de transferencia','Votos adicionales límite inferior':'Cobertura por límite inferior publicado; vacío si no disponible','Votos adicionales límite superior':'Cobertura por límite superior publicado; vacío si no disponible'});
 const territorial=Decision.territorialScenario(filtered,plan);
 const leeme=[['Distribución','Regla',plan.distribution],['Distribución','Criterio','Prioridad concentra por ranking; proporcional reparte por SV+NV 2024 con mayor resto y desempate por clave. Reglas propias de planeación, no hallazgos causales.'],['Territorio','Escala',$('simulation-scope').value],['Territorio','Estado',$('simulation-scope').value==='pais'?'Todo México':$('simulation-state').selectedOptions[0]?.text],['Territorio','Municipio',$('simulation-scope').value==='municipio'?$('simulation-municipality').selectedOptions[0]?.text:'Todos en el filtro'],['Territorio','Cobertura total prevista',Number($('reach').value)],['Territorio','Base observable del territorio',territorial.population],['Territorio','Abstención territorial sin acción',territorial.before],['Territorio','Abstención territorial con acción',territorial.after],['Territorio','Reducción territorial (pp)',territorial.before-territorial.after],['Documento','Qué es','Plan de priorización municipal de la demo local de Umbral (Tecnocalidos · Reto 2 INE). Acompaña a Umbral_plan_municipios.csv: una fila por municipio seleccionado.'],['Documento','Fecha de generación',new Date().toLocaleString('es-MX')],['Documento','Nota central','Las cifras de 2027 son estimaciones exploratorias, no resultados; la acción simulada es una hipótesis, no un efecto medido.'],['Filtros aplicados','Entidad',$('state').selectedOptions[0]?.text||'Todo México'],['Filtros aplicados','Búsqueda',$('search').value.trim()||'(sin búsqueda)'],['Filtros aplicados','Solo catálogo constante',bool($('stable').checked)],['Filtros aplicados','Método de estimación',METHOD_LABEL[$('method').value]],['Filtros aplicados','Criterio de prioridad',LENS_LABEL[$('lens').value]],['Filtros aplicados','Estabilidad mínima exigida',$('min-confidence').selectedOptions[0]?.text||'Todas'],['Simulación','Modo de capacidad','Cobertura total de personas en el territorio elegido'],['Simulación','Capacidad declarada',fmt.format(Number($('reach').value))+' personas en total'],['Simulación','Cobertura total prevista',fmt.format(Number($('reach').value))+' personas'],['Simulación','Respuesta supuesta',action.id==='personalizada'?response+'% de quienes no votarían':'No aplica al efecto en pp del estudio'],['Evidencia','Acción simulada',action.label],['Evidencia','Estimador y unidad',action.estimand+'; '+action.unit],['Evidencia','Efecto (pp)',action.effect_pp??'Supuesto del usuario'],['Evidencia','Fuente',action.citation||'Sin fuente causal'],['Evidencia','URL',action.source||''],['Evidencia','Localización',action.locator||'No aplica'],['Evidencia','Incertidumbre',action.uncertainty||'No disponible'],['Evidencia','Límites',action.limits],['Evidencia','Transferencia','Aplicación hipotética a México; intervalo original no incluye incertidumbre de transferencia ni del predictor. No se suman acciones.'],['Resumen del plan','Municipios seleccionados',fmt.format(plan.selected.length)],['Resumen del plan','Entidades',fmt.format(new Set(plan.selected.map(r=>r.state)).size)],['Resumen del plan','Base observable total (SV+NV 2024)',fmt.format(plan.reference_population)],['Resumen del plan','Personas alcanzadas (supuesto)',fmt.format(plan.served)],['Resumen del plan','Personas adicionales que votarían (supuesto)',plan.additional.toFixed(4)],['Resumen del plan','No votarían sin acción (ponderado)',pct(plan.before)],['Resumen del plan','No votarían con acción (ponderado)',pct(plan.after)],['Resumen del plan','Reducción (puntos porcentuales)',(plan.before-plan.after).toFixed(3)+' pp'],...Object.entries(dic).map(([k,v])=>['Diccionario de columnas',k,v]),['Limitaciones','Frecuencia no es probabilidad','Que un municipio aparezca en 6 de 6 variantes no garantiza acierto: las variantes comparten datos y pueden equivocarse juntas.'],['Limitaciones','Hipótesis no causal','La simulación no demuestra que una intervención aumente la participación.'],['Limitaciones','Base observable','Los escenarios usan SV+NV 2024; la participación no especificada queda fuera. No es electorado proyectado de 2027.'],['Limitaciones','Territorio','Claves INE con polígonos de referencia; límites históricos sin armonizar.']];
 const toCsv=rows=>new Blob(['\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});
 const trigger=(blob,name)=>{const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 trigger(toCsv([headers,...lines]),'Umbral_plan_municipios.csv');
 setTimeout(()=>trigger(toCsv([['Sección','Elemento','Detalle'],...leeme]),'Umbral_plan_leeme.csv'),450);
}
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
function renderActionEvidence(a){
 $('custom-response').hidden=a.id!=='personalizada';
 $('response').disabled=a.id!=='personalizada';
 $('reach-label').textContent=a.estimand==='ITT'?'¿A cuántas personas planeas enviar el SMS en total?':a.estimand==='ATT'?'¿Con cuántas personas completarías la llamada en total?':'Personas que alcanzarías en total';
 $('coverage-help').textContent=a.estimand==='ITT'?'Cuenta personas distintas a quienes enviarías el SMS, no mensajes ni lectores.':a.estimand==='ATT'?'Cuenta conversaciones completadas sobre el plan de votación, no intentos de llamada.':'Introduce tu capacidad total de contacto. Es un supuesto proporcionado por ti.';
 if($('action-evidence').dataset.action===a.id)return;
 $('action-evidence').dataset.action=a.id;
 $('action-evidence').innerHTML=a.source?`<strong>${a.effect_pp} puntos porcentuales de aumento en el estudio</strong><p>Aplicación hipotética a México; requiere revisar si la población y el contexto son comparables.</p><details><summary>Consultar estudio, fuente y límites</summary><p>${esc(a.country)} · ${esc(a.election)}. ${esc(a.population)}</p><p>Efecto: ${a.effect_pp} pp · Estimador: ${esc(a.estimand)}. ${esc(a.unit)}</p><p>${esc(a.uncertainty)} ${esc(a.limits)}</p><p><a href="${esc(a.source)}" target="_blank" rel="noopener noreferrer">${esc(a.citation)}</a> ${esc(a.locator)}.${a.fulltext?` <a href="${esc(a.fulltext)}" target="_blank" rel="noopener noreferrer">Texto completo ↗</a>`:''}</p><p>Transferencia hipotética a México; no calibrada con CCPC. Un punto porcentual no es una respuesta porcentual entre abstencionistas.</p></details>`:`<strong>${esc(a.label)}</strong><p>${esc(a.limits)}</p>`;
}
function load(){
 for(const a of Object.values(Decision.interventions))$('action').add(new Option(a.label,a.id));
 if(!window.UMBRAL_DATA||!window.UMBRAL_GEO)throw Error('Faltan datos incrustados');records=window.UMBRAL_DATA.municipios;metadata=window.UMBRAL_DATA.metadata;perfil=window.UMBRAL_PERFIL;geo=window.UMBRAL_GEO;
 const states=new Map(records.map(r=>[r.state,r.state_name]));for(const [key,name] of [...states].sort())$('state').add(new Option(name,key));
 for(const [key,name] of [...states].sort())$('simulation-state').add(new Option(name,key));
 simulationMunicipalities();
 $('simulation-scope').onchange=applySimulationScope;
 $('simulation-state').onchange=()=>{simulationMunicipalities();applySimulationScope();};
 $('simulation-municipality').onchange=applySimulationScope;
map=L.map('map',{preferCanvas:true,attributionControl:true,dragging:false,zoomControl:false,scrollWheelZoom:false,doubleClickZoom:false,touchZoom:false,boxZoom:false,keyboard:false,zoomSnap:.25}).setView([23.7,-102.5],5);map.attributionControl.addAttribution('INE · mayo 2024 simplificado, límites no armonizados');
map.createPane('municipal-geography');
layer=L.geoJSON(geo,{renderer:L.canvas({pane:'municipal-geography'}),onEachFeature:(f,l)=>{const r=records.find(r=>r.key===f.properties.key),node=document.createElement('span');node.textContent=r.name+' · '+r.key;l.bindTooltip(node);l.on('click',()=>{focusMunicipality(r.key,l);});}}).addTo(map);
 initGeography();
 initSearchablePickers();
 $('show-all').onclick=()=>{$('stable').checked=false;update();};
 document.querySelectorAll('a[href="#planning-settings"]').forEach(a=>a.addEventListener('click',()=>{$('planning-settings').open=true;}));
document.querySelectorAll('[data-scenario-map]').forEach(a=>a.addEventListener('click',()=>{$('map-mode').value=a.dataset.scenarioMap;$('confidence').checked=false;update();}));
  document.querySelectorAll('a[href="#sin-estimacion"]').forEach(a=>a.addEventListener('click',()=>{$('sin-estimacion').open=true;}));
 for(const id of ['state','search','stable','min-confidence','reach','response','action','distribution','method','lens','map-mode','confidence'])$(id).addEventListener('input',()=>{if(id==='state'||id==='search'){geographyFocusKey=null;geographyHistory.length=0;$('simulation-scope').value=$('state').value?'estado':'pais';if($('state').value){$('simulation-state').value=$('state').value;simulationMunicipalities();const exact=records.find(r=>r.state===$('state').value&&(r.key===$('search').value||r.name===$('search').value));if(exact){$('simulation-scope').value='municipio';$('simulation-municipality').value=exact.key;}}$('simulation-state-wrap').hidden=$('simulation-scope').value==='pais';$('simulation-municipality-wrap').hidden=$('simulation-scope').value!=='municipio';}update();});
 $('state').addEventListener('change',()=>{const layers=layer.getLayers().filter(l=>!$('state').value||byKey.get(l.feature.properties.key).state===$('state').value);if(layers.length)map.fitBounds(L.featureGroup(layers).getBounds(),{padding:[12,12]});});
 $('ranking').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){detail(b.dataset.key);if(window.innerWidth<=1050)$('detail').scrollIntoView({behavior:smooth(),block:'start'});}});$('export').onclick=exportPlan;
 $('missing-list').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){detail(b.dataset.key);$('detail').scrollIntoView({behavior:smooth(),block:'start'});}});
 initLensCards();
 if(perfil&&perfil.nacional){$('perfil-nacional').innerHTML=['edad','sexo','seccion'].flatMap(dim=>Object.keys(perfil.nacional['2024'][dim]).map(g=>{const c=perfil.nacional['2024'][dim][g];return `<tr><td>${esc((GROUP_NAME[dim]&&GROUP_NAME[dim][g])||g)}</td><td>${c.abstencion_pct===null?'—':c.abstencion_pct.toFixed(2)+'%'}</td><td>${fmt.format(c.n)}</td></tr>`;})).join('');}
 $('metrics').innerHTML=Object.entries(metadata.checks).flatMap(([year,c])=>['persistencia','ridge'].map(method=>{const m=c[method];return `<tr><td>${year} · ${method}<small>n=${fmt.format(m.n)}</small></td><td>${m.mae.toFixed(2)} pp</td><td>${m.mae_ponderado.toFixed(2)} pp</td><td>${Math.round(m.precision_top*m.top_k)}/${m.top_k}</td></tr>`;})).join('');
 const ad=metadata.additional_evaluation;
 $('additional-metrics').innerHTML=Object.entries(ad.cuts).flatMap(([year,c])=>Object.entries(c).map(([method,m])=>`<tr><td>${year} · ${method}</td><td>${m.spearman.toFixed(3)}</td><td>${pct(100*m.precision_rojo)}</td><td>${pct(100*m.recobrado_rojo)}</td><td>${m.rojos_predichos}</td><td>${pct(100*m.precision_rojo_vs_tercio_observado_test)}</td></tr>`)).join('');
 $('size-errors').innerHTML=Object.entries(ad.error_by_size).flatMap(([cut,bins])=>Object.entries(bins).map(([size,m])=>`<tr><td>${esc(cut)}</td><td>${esc(size)}</td><td>${m.n}</td><td>${m.mae.toFixed(2)} pp</td><td>${m.p90_abs_error_pp.toFixed(2)} pp</td></tr>`)).join('');
 $('method-note').textContent='Al probar el modelo con elecciones pasadas, funcionó mejor que usar la elección anterior comparable en 2021, pero peor en 2024. Por eso, la cifra de 2027 sirve para explorar y requiere revisión. Una simulación no demuestra que una actividad vaya a aumentar el voto.';
 $('methodology').innerHTML='<p>MAE ponderado usa SV+NV del objetivo histórico. El umbral rojo de evaluación se aprende del entrenamiento y se congela por corte; precisión y recobrado usan ese mismo umbral. La última columna compara rojos predichos contra el tercio alto observado del test, solo retrospectivamente. Los umbrales de la demo 2027 son tercios de estimaciones base y quedan fijos entre sus tres modos.</p><p>Bandas por tamaño: SV+NV del último antecedente, bins &lt;10 mil, 10–100 mil y ≥100 mil. P90 de error retrospectivo no es intervalo futuro. Estabilidad de prioridad: frecuencia entre persistencia/Ridge × NS 5/10/20 (seis variantes). No es probabilidad calibrada. La incertidumbre de ranking se informa con esta frecuencia y no con el rango ±21.05 pp, que se conserva solo como error histórico.</p><p>2021 se usa para seleccionar, no es prueba independiente posterior. 2024 es presidencial, no valida 2027. Solo seis ocasiones, tres intermedias. NS y límites históricos restringen inferencia.</p>';
 update();map.fitBounds(layer.getBounds(),{padding:[12,12]});
}
try{load();}catch(e){$('effect-range').textContent='';$('status').textContent='Faltan recursos locales o hubo un error de carga. Revisa que la carpeta demo esté completa.';console.error(e);}

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
 const stateSelection={state:r.state,method:$('method').value,stable:$('stable').checked};
 const stateRows=records.filter(row=>row.state===r.state&&(!stateSelection.stable||row.stable_catalog_state)).map(row=>({...row,risk:row[stateSelection.method]}));
 const stateBaseline=UmbralAnalytics.summary(stateRows,2027,stateSelection.method);
 const statePlan=stateBaseline.denominator?runtime.createStateScenario?.(stateRows,stateSelection,stateBaseline):null;
 const stateAssignment=statePlan?.selected.find(row=>row.key===key);
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
 const req=inv.reason?esc(inv.reason):`Para bajar un nivel, objetivo &lt; ${pct(inv.target+1e-6)}: alcance requerido ≈ ${inv.required_reach===null?'imposible con respuesta cero':fmt.format(inv.required_reach)} personas con respuesta ${$('response').value}%. ${inv.feasible_reach?'Cabe en la base observable.':'No cabe en la base observable con esa respuesta.'} Con el alcance actual, respuesta requerida ${pct(inv.required_response)} ${inv.feasible_response?'(≤100%).':'(no factible o sin alcance).'} Requisito algebraico hipotético.`;  const profile=(perfil&&perfil.municipios[key])?`<h3>Perfil CCPC observado ${yearHist} (capa explicativa)</h3><ul class="why">${['18_29','60_mas'].map(g=>perfilRow(key,'edad',g,yearHist)).join('')}${perfilRow(key,'sexo','hombres',yearHist)}${perfilRow(key,'sexo','mujeres',yearHist)}${perfilRow(key,'seccion','urbana',yearHist)}${perfilRow(key,'seccion','rural',yearHist)}</ul><p class="table-note hint">Ficha descriptiva de contexto. El modelo usa proporciones agregadas históricas de edad y urbanización; esta visualización no es una explicación causal. Las diferencias frente al promedio nacional no son efectos.</p>`:'';
  const detailYear = histDemo5 ? yearHist : 2027;
  const detailLimitText = histDemo5 ? `La cifra de ${yearHist} es observada. No es una proyección.` : `La cifra de 2027 es exploratoria. No sabemos todavía qué tan precisa será; 2024 y 2027 son elecciones de distinto tipo.`;
 $('detail-content').innerHTML=`<div class="detail-comparison"><section><h3>¿Qué ocurrió en elecciones anteriores?</h3><div class="fact-cards">
  <div><span>Dato observado · ${last?last.year:'sin antecedente'}</span><strong>${last?pct(last.risk):'Sin dato'}</strong><small>${last&&Number.isFinite(last.risk)?"Aproximadamente "+Math.round(last.risk)+" de cada 100 personas no votaron":"Sin dato disponible"}</small></div>
  </div></section><section><h3>¿Qué se estima para ${detailYear === 2027 ? '2027' : yearHist}?</h3><div class="fact-cards"><div><span>${histDemo5 ? 'Observado · ' + yearHist : 'Estimación exploratoria · 2027'}</span><strong>${histDemo5 ? pct(r.history.find(h=>h.year===yearHist)?.risk) : pct(r.risk)}</strong><small>${histDemo5 ? 'Abstención observada en ' + yearHist + '.' : 'Aproximadamente ' + Math.round(r.risk) + ' de cada 100 personas podrían no votar. Es una estimación.'}</small></div>
  ${statePlan?`<div id="municipal-state-scenario" data-after="${stateAssignment?.after??r.risk}" data-served="${stateAssignment?.served??0}" data-state-served="${statePlan.served}"><span>Con el plan estatal · 2027</span><strong>${pct(stateAssignment?.after??r.risk)}</strong><small>${fmt.format(stateAssignment?.served??0)} personas asignadas a este municipio, de ${fmt.format(statePlan.served)} en ${esc(r.state_name)}. Reparto proporcional del alcance estatal del 10 %; efecto supuesto de 1.5 pp entre personas alcanzadas. Corresponde al plan estatal del apartado 03 y no cambia al ajustar el simulador SMS.</small><a href="#d6-state-plan">Ver el plan estatal</a></div>`:''}</div></section></div><p class="detail-limit">${detailLimitText}</p>
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

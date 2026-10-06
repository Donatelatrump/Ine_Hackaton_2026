'use strict';
const $=id=>document.getElementById(id), fmt=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0}), pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'Sin estimación';
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const TIER={alta:'🟢 Alta',media:'🟡 Media',baja:'🔴 Baja',sin_datos:'⚪ Sin datos'};
const GROUP_NAME={edad:{'18_29':'Jóvenes 18–29','30_59':'Adultos 30–59','60_mas':'Personas 60+'},sexo:{hombres:'Hombres',mujeres:'Mujeres',no_binario:'No binario'},seccion:{urbana:'Urbana',mixta:'Mixta',rural:'Rural'}};
let records,metadata,perfil,geo,map,layer,filtered=[],view=[],plan,thresholds,stability={},frontier={nucleo:[],frontera:[],fuera:[]},activeKey=null,selectedMap=new Map(),byKey;
const colors={bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#cdd6d2'};
function quantile(values,q){const s=values.slice().sort((a,b)=>a-b),p=(s.length-1)*q,i=Math.floor(p);return s[i]+(s[Math.min(i+1,s.length-1)]-s[i])*(p-i);}
function matches(r){return (!$('state').value||r.state===$('state').value)&&(!$('stable').checked||r.stable_catalog_state)&&norm(r.name+' '+r.key).includes(norm($('search').value.trim()));}
function preventive(r){
 const p=r.profile,base={responsible:'Área de educación cívica y junta local, responsables propuestos; validar atribuciones y capacidad',resource:'Personas alcanzadas y horas de operación registradas; sin costos monetarios inventados',mechanism:'Hipótesis de reducción de barreras informativas; no efecto causal demostrado'};
 if(!Number.isFinite(r.risk))return {...base,type:'Calidad antes de priorizar',action:'Revisar fuente y antecedentes; no asignar prioridad predictiva',coverage:'Territorio con información insuficiente',conditions:'Resolver NS/antecedentes y verificar comparabilidad',measurement:'Completitud, NS y trazabilidad antes/después de la revisión'};
 if(p.urban_pct<50)return {...base,type:'Cobertura territorial presencial',action:'Sesiones de información electoral accesible en sedes comunitarias verificadas',coverage:'Municipio con menos de 50% de LN urbana; población alcanzada registrada',conditions:'Validar sedes, movilidad, accesibilidad y coordinación local; no inferir barreras solo por ruralidad',measurement:'Personas alcanzadas, cobertura de sedes y conocimiento de requisitos mediante evaluación agregada'};
 if(p.young_pct>=25)return {...base,type:'Información para ciudadanía joven',action:'Talleres sobre requisitos y procedimiento electoral en espacios educativos y comunitarios',coverage:'Municipio con proporción 18–29 ≥25%; atención voluntaria y abierta',conditions:'Verificar espacios y acceso; no asumir desinterés por edad ni seleccionar personas por afinidad',measurement:'Alcance verificable y cambio de conocimiento; participación posterior solo agregada'};
 if(p.older_pct>=25)return {...base,type:'Accesibilidad de información',action:'Material legible y sesiones con canales accesibles',coverage:'Municipio con proporción 60+ ≥25%; oferta abierta',conditions:'Validar necesidades de accesibilidad con usuarios; edad no demuestra una barrera',measurement:'Comprensión de instrucciones, accesibilidad percibida y alcance agregado'};
 return {...base,type:'Información electoral general',action:'Sesiones abiertas y materiales claros sobre cuándo, dónde y cómo votar',coverage:'Población municipal alcanzada según capacidad declarada',conditions:'Verificar pertinencia y canales con el área usuaria antes de implementar',measurement:'Alcance, conocimiento y seguimiento agregado con comparación predefinida'};
}
function rankUnder(key,method){const rows=filtered.map(x=>({...x,risk:x[method]}));const rk=Decision.rank(rows,$('lens').value);return rk.findIndex(x=>x.key===key)+1;}
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
  $('detail-state').textContent=r.state_name+' · Clave INE '+r.key+' · Fuera del filtro actual';
  $('detail-content').innerHTML='<div class="missing-message"><strong>Este municipio está fuera de tu selección de territorio</strong><p>Cambia la entidad, la búsqueda o el filtro de catálogo para revisarlo. No tiene puesto ni estabilidad de selección dentro del filtro actual.</p></div>';
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
 const inv=Decision.inverseScenario(r,Number($('reach').value),Number($('response').value),thresholds);
 const p=preventive(r),chosen=selectedMap.get(key);
 const refRank=rankUnder(key,'baseline'),ridgeRank=rankUnder(key,'ridge'),capacityNow=plan.selected.length;
 $('detail-name').textContent=r.name;$('detail-state').textContent=r.state_name+' · Clave INE '+r.key+' · Prioridad '+pos+' de '+total;
 const last=r.history.length?r.history[r.history.length-1]:null;
 const reasons=[];
 if(Number.isFinite(r.baseline))reasons.push(`Abstención en la elección comparable (2021): <strong>${pct(r.baseline)}</strong>`);
 if(last&&Number.isFinite(last.risk))reasons.push(`Último proceso (${last.year}): <strong>${pct(last.risk)}</strong>`);
 if(Number.isFinite(r.profile.urban_pct))reasons.push(`Predominio urbano: ${pct(r.profile.urban_pct)} de LN en secciones urbanas`);
 if(Number.isFinite(r.latest_ns))reasons.push(`NS 2024: <strong>${pct(r.latest_ns)}</strong> (${r.latest_ns<=10?'dentro del umbral 10%':'sobre el umbral de la regla'})`);
 const bothHigh=capacityNow>0&&refRank<=capacityNow&&ridgeRank<=capacityNow;
 reasons.push(`Referencia (puesto ${refRank||'—'}) y Ridge (puesto ${ridgeRank||'—'}): ${bothHigh?'coinciden dentro de la capacidad actual':(refRank<=capacityNow||ridgeRank<=capacityNow)?'solo uno entra en la selección con la capacidad actual':'ninguno entra en la selección con la capacidad actual'}`);
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
 $('detail-content').innerHTML=`<div class="fact-cards">
  <div><span>Dato observado · ${last?last.year:'sin antecedente'}</span><strong>${last?pct(last.risk):'Sin dato'}</strong><small>Abstención registrada</small></div>
  <div><span>Estimación exploratoria · 2027</span><strong>${pct(r.risk)}</strong><small>${esc($('method').selectedOptions[0].text)}</small></div>
  <div><span>Intervención hipotética</span><strong>${chosen?pct(chosen.after):'Sin asignación'}</strong><small>${chosen?fmt.format(chosen.served)+' personas alcanzadas (supuesto)':'Fuera del plan actual'}</small></div></div>
  <h3>¿Por qué está aquí?</h3><ul class="why">${reasons.map(x=>`<li>${x}</li>`).join('')}</ul>
  <h3>Qué revisar antes de actuar</h3><p>Estabilidad de selección: <strong>${TIER[conf.tier]} (${s.count}/6)</strong>. ${s.robust?'Seleccionado en todas las variantes.':s.count>0?'La selección depende del método o de la calidad.':'No entra en las variantes con la capacidad actual.'} Elegible en ${s.eligible}/6. No es probabilidad de acierto; las variantes pueden equivocarse juntas.</p>
  ${r.exclusion_reasons.length?`<div class="evidence-note">${r.exclusion_reasons.map(esc).join('<br>')}</div>`:''}
  <p>${esc(p.conditions)}.</p>
  <h3>Acción sugerida</h3><p><strong>${esc(p.type)}.</strong> ${esc(p.action)}.</p><p class="hint">${esc(p.mechanism)}.</p>
  <details><summary>Consultar el perfil observado por grupos</summary>${profile||'<p>Sin perfil desagregado disponible.</p>'}</details>
  <details><summary>Responsable, cobertura, recurso y evaluación</summary><dl class="prevention">${Object.entries({Responsable:p.responsible,Cobertura:p.coverage,Recurso:p.resource,'Cómo evaluarla':p.measurement}).map(([k,v])=>`<dt>${k}</dt><dd>${esc(v)}</dd>`).join('')}</dl></details>
  <details><summary>Requisito para bajar de nivel (factibilidad algebraica)</summary><p>${req}</p></details>
  <details><summary>Cómo cambia la selección entre variantes</summary><ul class="why">${robustez}</ul><p>Frecuencia de selección ${s.count}/6. En modo personas se usa un número equivalente de municipios; no se recalcula el presupuesto humano por variante.</p></details>
  <details><summary>Antecedentes observados y nota técnica de incertidumbre</summary><div class="history">${r.history.map(h=>`<div><span>${h.year}</span><div class="bar-track"><i style="width:${Number.isFinite(h.risk)?h.risk:0}%"></i></div><b>${pct(h.risk)}</b></div>`).join('')}</div><p>La prioridad se comunica con la frecuencia entre variantes (arriba). El rango técnico ${pct(r.range_low)}–${pct(r.range_high)} (±21.05 pp, p90 retrospectivo de Ridge 2021) se conserva solo aquí como referencia de error histórico; no es intervalo prospectivo.</p><p>${r.flags.map(esc).join('; ')||'Sin alertas adicionales'}</p></details>`;
}
function update(){
 const capacityMode=$('capacity-mode').value,capacity=Number($('capacity').value),persons=Number($('persons').value);
 const reach=Number($('reach').value),response=Number($('response').value),lens=$('lens').value,method=$('method').value,minConf=$('min-confidence').value;
 $('capacity-out').textContent=capacity;$('response-out').textContent=response+'%';$('persons-out').textContent=fmt.format(persons);
 $('capacity').classList.toggle('hidden',capacityMode==='personas');$('capacity-label').classList.toggle('hidden',capacityMode==='personas');
 $('persons').classList.toggle('hidden',capacityMode!=='personas');$('persons-label').classList.toggle('hidden',capacityMode!=='personas');
 view=records.map(r=>({...r,risk:r[method]}));byKey=new Map(view.map(r=>[r.key,r]));filtered=view.filter(matches);
 const rates=view.map(r=>r.risk).filter(Number.isFinite);thresholds={low:quantile(rates,1/3),high:quantile(rates,2/3)};
 const select=pool=>capacityMode==='personas'?Decision.planByBudget(pool,persons,reach,response,lens):Decision.planScenario(pool,capacity,reach,response,lens);
 try{
  if($('reach').value.trim()===''||!$('reach').checkValidity())throw Error('Alcance inválido');
  if(capacityMode==='personas'&&($('persons').value.trim()===''||!$('persons').checkValidity()))throw Error('Personas inválidas');
  let pool=filtered;
  const probe=select(pool),stab0=Decision.selectionStability(filtered,probe.selected.length,lens);
  if(minConf!=='todas'){const min=minConf==='alta'?5/6:3/6;pool=filtered.filter(r=>{const s=stab0[r.key];return s&&s.frequency>=min;});}
  plan=select(pool);
 }catch(e){$('status').textContent='Corrige el alcance o las personas (valores válidos); resultados pendientes.';$('export').disabled=true;for(const id of ['eligible','coverage','selected','additional','served','before','after','reduction','missing-count','list-count','agreement'])$(id).textContent='—';$('ranking').innerHTML='<tr><td colspan="4">Corrige los parámetros para recalcular.</td></tr>';$('entity-table').innerHTML='';$('plan-summary').innerHTML='';$('frontier-table').innerHTML='';$('frontier-summary').textContent='—';$('pilot-note').textContent='';$('detail-content').innerHTML='';$('map').style.visibility='hidden';return;}
 $('map').style.visibility='visible';selectedMap=new Map(plan.selected.map(r=>[r.key,r]));
 const n=plan.selected.length;stability=Decision.selectionStability(filtered,n,lens);frontier=Decision.decisionFrontier(filtered,n,lens);
 const topRate=Decision.rank(filtered,'tasa').slice(0,n),topVol=Decision.rank(filtered,'volumen').slice(0,n),topChange=Decision.rank(filtered,'deterioro').slice(0,n);
 $('agreement').textContent=`Solapamiento con la lista por tasa: volumen ${Decision.overlap(topRate,topVol)}/${topRate.length}; deterioro ${Decision.overlap(topRate,topChange)}/${topRate.length}.`;
 $('status').textContent='Datos locales cargados · Exploratorio. Umbrales base fijos durante la comparación; la estabilidad es frecuencia entre variantes, no probabilidad.';
 $('eligible').textContent=fmt.format(filtered.filter(r=>Number.isFinite(r.risk)).length);$('coverage').textContent=fmt.format(filtered.length)+' territorios en el filtro; '+metadata.n_sin_estimacion+' sin estimación nacional';
 const missing=filtered.filter(r=>!Number.isFinite(r.risk));$('missing-count').textContent=fmt.format(missing.length);
 $('missing-list').innerHTML=missing.slice(0,12).map(r=>`<button class="missing-row" type="button" data-key="${r.key}"><strong>${esc(r.name)}</strong><span>${esc(r.state_name)} · ${r.key}</span><small>${esc(r.exclusion_reasons[0]||'Revisar antecedentes y calidad')}</small></button>`).join('')||'<p>No hay municipios sin estimación en este filtro.</p>';
 $('selected').textContent=n;$('additional').textContent='≈ '+fmt.format(plan.additional);$('served').textContent=fmt.format(plan.served)+' personas de base observable (supuesto)';
 $('before').textContent=n?pct(plan.before):'Sin selección';$('after').textContent=n?pct(plan.after):'Sin selección';$('export').disabled=!n;$('list-count').textContent=n+' seleccionados';
 $('reduction').textContent=n?(plan.before-plan.after).toFixed(3)+' pp':'Sin selección';
 const robust=plan.selected.filter(r=>stability[r.key]&&stability[r.key].robust).length,review=n-robust,entityCount=new Set(plan.selected.map(r=>r.state)).size;
 $('plan-summary').innerHTML=[['Municipios',fmt.format(n)],['Entidades',fmt.format(entityCount)],['Base observable SV+NV 2024',fmt.format(plan.reference_population)],['Prioridad núcleo robusto',fmt.format(robust)],['Requieren revisión',fmt.format(review)],['Personas alcanzadas (supuesto)',fmt.format(plan.served)],['Escenario base',n?pct(plan.before):'—'],['Escenario hipotético',n?pct(plan.after):'—']].map(([k,v])=>`<div><span>${k}</span><strong>${v}</strong></div>`).join('');
 const nuc=frontier.nucleo.length,fro=frontier.frontera.length;
 $('frontier-summary').innerHTML=`<strong>Núcleo robusto:</strong> ${fmt.format(nuc)} municipios entran en la selección bajo las 6/6 variantes. <strong>Frontera de decisión:</strong> ${fmt.format(fro)} cambian según método, calidad o criterio. <strong>Fuera:</strong> ${fmt.format(frontier.fuera.length)} nunca entran con esta capacidad.`;
 $('frontier-table').innerHTML=[['Núcleo robusto (6/6)',nuc,'#1'],['Frontera de decisión (1/6–5/6)',fro,'depende'],['Fuera de la selección',frontier.fuera.length,'—']].map(([k,v,tag])=>`<div><span>${k}</span><strong>${fmt.format(v)}</strong><small>${tag}</small></div>`).join('');
 $('pilot-note').textContent=fro>0?`Si solo existen recursos para atender una fracción de la frontera (por ejemplo, 12 de ${fmt.format(fro)} municipios), una asignación aleatoria dentro de esa zona —con balance por entidad, tamaño, calidad y contexto— permitiría construir un piloto evaluable. La cercanía del score no acredita equivalencia.`:'Con la capacidad actual no hay una zona de frontera: la selección es estable bajo las variantes o el filtro la vació.';
 $('ranking').innerHTML=plan.selected.slice(0,25).map(r=>{const s=stability[r.key]||{count:0,eligible:0,confidence:Decision.confidenceTier(0,6)};const c=s.confidence||Decision.confidenceTier(s.count,6);return `<tr><td><button type="button" data-key="${r.key}" class="row-button">${esc(r.name)}</button><small>${esc(r.state_name)} · ${r.key}</small></td><td>${pct(r.risk)}<small>Escenario ${pct(r.after)}</small></td><td>${TIER[c.tier]}<small>${s.count}/6 · elegible ${s.eligible}/6</small></td><td>NS ${pct(r.latest_ns)}<small>Catálogo ${r.stable_catalog_state?'constante':'cambia'}</small></td></tr>`;}).join('')||'<tr><td colspan="4">Sin municipios seleccionados con estos filtros.</td></tr>';
 const mode=$('map-mode').value;
 const legend=$('confidence').checked?'<span><i style="background:#176b58"></i>Núcleo 6/6</span><span><i style="background:#ddb263"></i>Revisión</span>':mode==='cambio'?'<span><i style="background:#f6faf9;border:1px solid #ddd"></i>0 pp</span><span><i style="background:#9dccdf"></i>0–1 pp</span><span><i style="background:#4b94b8"></i>1–5 pp</span><span><i style="background:#135e87"></i>&gt;5 pp</span>':'<span><i class="low"></i>Bajo</span><span><i class="medium"></i>Medio</span><span><i class="high"></i>Alto</span>';
 document.querySelector('.legend').innerHTML=legend+'<span><i class="missing"></i>Sin estimación</span><span><i class="chosen"></i>Seleccionado</span><span>Atenuado: fuera del filtro</span>';
 $('map-caption').textContent=mode==='cambio'?'Δ = reducción hipotética en puntos porcentuales; blanco = sin reducción, azul = mayor reducción.':'Colores relativos a las estimaciones nacionales: bajo < '+thresholds.low.toFixed(2)+'%; alto ≥ '+thresholds.high.toFixed(2)+'%. Gris = sin estimación.';
 layer.setStyle(f=>{const r=byKey.get(f.properties.key),s=selectedMap.get(r.key),visible=matches(r),after=s?s.after:r.risk,delta=s?r.risk-s.after:0;let color=colors[Decision.level(mode==='intervencion'?after:r.risk,thresholds)];if(mode==='cambio')color=!Number.isFinite(r.risk)?colors.sin_datos:delta>5?'#135e87':delta>1?'#4b94b8':delta>0?'#9dccdf':'#f6faf9';if($('confidence').checked&&Number.isFinite(r.risk)&&visible)color=stability[r.key]?.robust?'#176b58':'#ddb263';return {color:s?'#173c34':'#ffffff',weight:s?1.7:.3,fillColor:color,fillOpacity:visible?.85:.08,opacity:visible?1:.15};});
 $('confidence-note').textContent=$('confidence').checked?'Vista estabilidad: verde = seleccionado en 6/6 variantes; ámbar = revisión; gris = sin estimación. Frecuencia descriptiva; las variantes pueden equivocarse juntas.':'Vista riesgo/cambio. La estabilidad de selección se informa como dimensión separada en lista y ficha.';
 const states=[...new Set(filtered.map(r=>r.state))].sort();
 $('entity-table').innerHTML=states.map(state=>{const all=filtered.filter(r=>r.state===state),valid=all.filter(r=>Number.isFinite(r.risk)),sel=plan.selected.filter(r=>r.state===state),obs=valid.reduce((a,r)=>a+r.observed,0),before=obs?valid.reduce((a,r)=>a+r.risk*r.observed,0)/obs:null,add=sel.reduce((a,r)=>a+r.additional,0);return `<tr><td>${esc(all[0].state_name)}</td><td>${valid.length}/${all.length}</td><td>${sel.length}</td><td>${pct(before)}</td><td>${pct(obs?before-100*add/obs:null)}</td><td>${fmt.format(sel.reduce((a,r)=>a+r.served,0))}</td></tr>`;}).join('');
 if(activeKey)detail(activeKey);
}
function exportPlan(){
 const headers=['clave_ine','entidad','municipio','criterio','metodo','posicion_prioridad','estimacion_2027_pct','escenario_pct','confianza_prioridad','frecuencia_variantes','observados_sv_nv_2024','ln_2024','ns_pct','alcance_limitado','respuesta_supuesta_pct','adicional_hipotetica','selecciones_variantes','variantes_elegibles','nucleo_robusto','catalogo_constante','tipologia','accion','responsable_propuesto','condiciones','recurso','medicion','nota'];
 const ranked=Decision.rank(filtered,$('lens').value);
 const lines=plan.selected.map(r=>{const s=stability[r.key]||{count:0,eligible:0,robust:false},c=s.confidence||Decision.confidenceTier(s.count,6),p=preventive(r),pos=ranked.findIndex(x=>x.key===r.key)+1;return [r.key,r.state_name,r.name,$('lens').value,$('method').value,pos,r.risk,r.after,TIER[c.tier],s.count,r.observed,r.ln,r.latest_ns,r.served,Number($('response').value),r.additional,s.count,s.eligible,s.robust,r.stable_catalog_state,p.type,p.action,p.responsible,p.conditions,p.resource,p.measurement,'Hipótesis no causal; frecuencia no probabilidad; base observable histórica, sin NS; límites sin armonizar'];}); 
 const cell=v=>{let s=String(v??'');if(typeof v==='string'&&/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
 const blob=new Blob(['\uFEFF'+[headers,...lines].map(row=>row.map(cell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='Tecnocalidos_track2_plan.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function load(){
 if(!window.UMBRAL_DATA||!window.UMBRAL_GEO)throw Error('Faltan datos incrustados');records=window.UMBRAL_DATA.municipios;metadata=window.UMBRAL_DATA.metadata;perfil=window.UMBRAL_PERFIL;geo=window.UMBRAL_GEO;
 const states=new Map(records.map(r=>[r.state,r.state_name]));for(const [key,name] of [...states].sort())$('state').add(new Option(name,key));
 map=L.map('map',{preferCanvas:true,attributionControl:true,zoomSnap:.25}).setView([23.7,-102.5],5);map.attributionControl.addAttribution('INE · mayo 2024 simplificado, límites no armonizados');
 layer=L.geoJSON(geo,{onEachFeature:(f,l)=>{const r=records.find(r=>r.key===f.properties.key),node=document.createElement('span');node.textContent=r.name+' · '+r.key;l.bindTooltip(node);l.on('click',()=>{detail(r.key);$('detail').scrollIntoView({behavior:'smooth',block:'start'});});}}).addTo(map);
 $('reset-map').onclick=()=>map.fitBounds(layer.getBounds(),{padding:[12,12]});
 for(const id of ['state','search','stable','capacity','persons','capacity-mode','min-confidence','reach','response','method','lens','map-mode','confidence'])$(id).addEventListener('input',update);
 $('state').addEventListener('change',()=>{const layers=layer.getLayers().filter(l=>!$('state').value||byKey.get(l.feature.properties.key).state===$('state').value);if(layers.length)map.fitBounds(L.featureGroup(layers).getBounds(),{padding:[12,12]});});
 $('ranking').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){detail(b.dataset.key);if(window.innerWidth<=1050)$('detail').scrollIntoView({behavior:'smooth',block:'start'});}});$('export').onclick=exportPlan;
 $('missing-list').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b){detail(b.dataset.key);$('detail').scrollIntoView({behavior:'smooth',block:'start'});}});
 if(perfil&&perfil.nacional){$('perfil-nacional').innerHTML=['edad','sexo','seccion'].flatMap(dim=>Object.keys(perfil.nacional['2024'][dim]).map(g=>{const c=perfil.nacional['2024'][dim][g];return `<tr><td>${esc((GROUP_NAME[dim]&&GROUP_NAME[dim][g])||g)}</td><td>${c.abstencion_pct===null?'—':c.abstencion_pct.toFixed(2)+'%'}</td><td>${fmt.format(c.n)}</td></tr>`;})).join('');}
 $('metrics').innerHTML=Object.entries(metadata.checks).flatMap(([year,c])=>['persistencia','ridge'].map(method=>{const m=c[method];return `<tr><td>${year} · ${method}<small>n=${fmt.format(m.n)}</small></td><td>${m.mae.toFixed(2)} pp</td><td>${m.mae_ponderado.toFixed(2)} pp</td><td>${Math.round(m.precision_top*m.top_k)}/${m.top_k}</td></tr>`;})).join('');
 const ad=metadata.additional_evaluation;
 $('additional-metrics').innerHTML=Object.entries(ad.cuts).flatMap(([year,c])=>Object.entries(c).map(([method,m])=>`<tr><td>${year} · ${method}</td><td>${m.spearman.toFixed(3)}</td><td>${pct(100*m.precision_rojo)}</td><td>${pct(100*m.recobrado_rojo)}</td><td>${m.rojos_predichos}</td><td>${pct(100*m.precision_rojo_vs_tercio_observado_test)}</td></tr>`)).join('');
 $('size-errors').innerHTML=Object.entries(ad.error_by_size).flatMap(([cut,bins])=>Object.entries(bins).map(([size,m])=>`<tr><td>${esc(cut)}</td><td>${esc(size)}</td><td>${m.n}</td><td>${m.mae.toFixed(2)} pp</td><td>${m.p90_abs_error_pp.toFixed(2)} pp</td></tr>`)).join('');
 $('method-note').textContent='Ridge mejora en 2021 y pierde frente a la referencia en 2024. La estimación para 2027 es exploratoria y necesita revisión humana. Los escenarios son hipótesis: no demuestran efectos de una intervención.';
 $('methodology').innerHTML='<p>MAE ponderado usa SV+NV del objetivo histórico. El umbral rojo de evaluación se aprende del entrenamiento y se congela por corte; precisión y recobrado usan ese mismo umbral. La última columna compara rojos predichos contra el tercio alto observado del test, solo retrospectivamente. Los umbrales de la demo 2027 son tercios de estimaciones base y quedan fijos entre sus tres modos.</p><p>Bandas por tamaño: SV+NV del último antecedente, bins &lt;10 mil, 10–100 mil y ≥100 mil. P90 de error retrospectivo no es intervalo futuro. Estabilidad de prioridad: frecuencia entre persistencia/Ridge × NS 5/10/20 (seis variantes). No es probabilidad calibrada. La incertidumbre de ranking se informa con esta frecuencia y no con el rango ±21.05 pp, que se conserva solo como error histórico.</p><p>2021 se usa para seleccionar, no es prueba independiente posterior. 2024 es presidencial, no valida 2027. Solo seis ocasiones, tres intermedias. NS y límites históricos restringen inferencia.</p>';
 update();map.fitBounds(layer.getBounds(),{padding:[12,12]});detail(plan.selected[0]?.key||records[0].key);
}
try{load();}catch(e){$('status').textContent='Faltan recursos locales o hubo un error de carga. Revisa que la carpeta demo esté completa.';console.error(e);}

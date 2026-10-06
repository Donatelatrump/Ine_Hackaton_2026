'use strict';
const $=id=>document.getElementById(id), fmt=new Intl.NumberFormat('es-MX',{maximumFractionDigits:0}), pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'Sin estimación';
const esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
let records, metadata, map, layer, filtered=[], plan, chosen=new Set();
const colors={bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#cdd6d2'};
function matches(r){return (!$('state').value||r.state===$('state').value)&&(!$('stable').checked||r.stable_catalog_state)&&norm(r.name+' '+r.key).includes(norm($('search').value.trim()));}
function detail(r){
 $('detail-name').textContent=r.name; $('detail-state').textContent=r.state_name+' · Clave INE '+r.key;
 $('detail-content').innerHTML=`<div class="detail-risk">${pct(r.risk)}</div><p>Proyección exploratoria 2027 · ${esc(r.method)}.</p><p>Referencia del mismo tipo: ${pct(r.baseline)}. Rango ilustrativo: ${pct(r.range_low)} – ${pct(r.range_high)}; no es un intervalo de confianza.</p><h3>Antecedentes observados</h3><div class="history">${r.history.map(h=>`<div><span>${h.year}</span><div class="bar-track"><i style="width:${Number.isFinite(h.risk)?h.risk:0}%"></i></div><b>${pct(h.risk)}</b></div>`).join('')}</div><p>NS 2024: ${pct(r.latest_ns)}. Si todos los NS hubieran votado o se hubieran abstenido, la abstención histórica 2024 estaría entre ${pct(r.latest_ns_low)} y ${pct(r.latest_ns_high)}. Este rango no corresponde a 2027.</p><p>LN 2024: ${fmt.format(r.ln)}. Catálogo de claves de su entidad: ${r.stable_catalog_state?'constante':'con cambios'}; límites históricos sin armonizar.</p>${r.flags.length?`<p class="evidence-note">${r.flags.map(esc).join('; ')}</p>`:''}<p class="hint">Las tasas históricas usan NV/(SV+NV); NS se informa por separado. La priorización invita a revisar y planear atención cívica, no demuestra causas de abstención.</p>`;
}
function update(){
 const capacity=Number($('capacity').value), reach=Number($('reach').value), response=Number($('response').value);
 $('capacity-out').textContent=capacity; $('response-out').textContent=response+'%';
 filtered=records.filter(matches);
 try { if($('reach').value.trim()===''||!$('reach').checkValidity())throw Error('Alcance inválido'); plan=Decision.planScenario(filtered,capacity,reach,response); }
 catch(e){
  $('status').textContent='Introduce un alcance válido entre 0 y 1,000,000 personas. Resultados pendientes de recalcular.';$('export').disabled=true;
  for(const id of ['eligible','coverage','selected','additional','served','before','after','list-count'])$(id).textContent='—';
  $('ranking').innerHTML='<tr><td colspan="4">Corrige el alcance para recalcular.</td></tr>';$('map').style.visibility='hidden';return;
 }
 $('map').style.visibility='visible';
 chosen=new Set(plan.selected.map(r=>r.key));
 $('status').textContent='Datos locales cargados · Proyección exploratoria; revisar calidad y evidencia antes de tomar decisiones.';
 $('eligible').textContent=fmt.format(filtered.filter(r=>Number.isFinite(r.risk)).length);
 $('coverage').textContent=fmt.format(filtered.length)+' municipios en el filtro · '+metadata.n_sin_estimacion+' sin estimación nacional';
 $('selected').textContent=plan.selected.length; $('additional').textContent='≈ '+fmt.format(plan.additional); $('served').textContent=fmt.format(plan.served)+' personas alcanzadas (supuesto)';
 $('before').textContent=plan.selected.length?pct(plan.before):'Sin selección';$('after').textContent=plan.selected.length?pct(plan.after):'Sin selección';
 $('export').disabled=!plan.selected.length;
 $('list-count').textContent=plan.selected.length+' seleccionados';
 $('ranking').innerHTML=plan.selected.slice(0,25).map(r=>`<tr><td><button type="button" data-key="${r.key}" class="row-button">${esc(r.name)}</button><small>${esc(r.state_name)} · ${r.key}</small></td><td><span class="risk-pill ${r.level}">${pct(r.risk)}</span></td><td>${r.range_low.toFixed(1)}–${r.range_high.toFixed(1)} pp</td><td>NS ${pct(r.latest_ns)}</td></tr>`).join('')||'<tr><td colspan="4">Sin municipios seleccionados con estos filtros.</td></tr>';
 layer.setStyle(f=>{const r=recordsByKey.get(f.properties.key),visible=matches(r);return {color:chosen.has(r.key)?'#173c34':'#ffffff',weight:chosen.has(r.key)?1.7:.3,fillColor:colors[r.level],fillOpacity:visible?.85:.08,opacity:visible?1:.15};});
}
let recordsByKey;
async function load(){
 const responses=await Promise.all(['data/resultados.json','data/municipios.geojson'].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error(url);return r.json();}));
 records=responses[0].municipios; metadata=responses[0].metadata; recordsByKey=new Map(records.map(r=>[r.key,r]));
 const states=new Map(records.map(r=>[r.state,r.state_name]));for(const [key,name] of [...states].sort()){$('state').add(new Option(name,key));}
 map=L.map('map',{preferCanvas:true,attributionControl:true,zoomSnap:.25}).setView([23.7,-102.5],5);
 map.attributionControl.addAttribution('INE · polígonos 2024 simplificados para visualización');
 layer=L.geoJSON(responses[1],{onEachFeature:(f,l)=>{const r=recordsByKey.get(f.properties.key);const node=document.createElement('span');node.textContent=r.name+' · '+pct(r.risk);l.bindTooltip(node);l.on('click',()=>detail(r));}}).addTo(map);
 $('reset-map').onclick=()=>map.fitBounds(layer.getBounds(),{padding:[12,12]});
 for(const id of ['state','search','stable','capacity','reach','response'])$(id).addEventListener('input',update);
 $('state').addEventListener('change',()=>{const layers=layer.getLayers().filter(l=>!$('state').value||recordsByKey.get(l.feature.properties.key).state===$('state').value);if(layers.length)map.fitBounds(L.featureGroup(layers).getBounds(),{padding:[12,12]});});
 $('ranking').addEventListener('click',e=>{const b=e.target.closest('button[data-key]');if(b)detail(recordsByKey.get(b.dataset.key));});
 $('export').onclick=exportPlan;
 $('metrics').innerHTML=Object.entries(metadata.checks).flatMap(([year,c])=>['persistencia','ridge'].map(method=>{const m=c[method];return `<tr><td>${year} · ${method==='ridge'?'Ridge':'Referencia mismo tipo'}<small>n = ${fmt.format(m.n)}</small></td><td>${m.mae.toFixed(2)} pp</td><td>${m.mae_ponderado.toFixed(2)} pp</td><td>${Math.round(m.precision_top*m.top_k)}/${m.top_k}</td></tr>`;})).join('');
 $('method-note').textContent='Ridge se seleccionó con 2021: 19 de los 50 municipios con mayor abstención fueron recuperados. En 2024 su error fue mayor que el de la referencia (8.58 frente a 5.64 pp). La mejora no se transfiere de manera consistente; 2027 sigue siendo exploratorio.';
 $('methodology').innerHTML='<p>Seis ocasiones electorales, no millones de muestras temporales independientes. Entrenamiento anterior a cada corte; Ridge alpha=10 y regla de selección fijados antes de ver resultados. 2021 se utiliza para seleccionar, por lo que su resultado no es una prueba independiente posterior a selección.</p><p>NS máximo 10% en antecedentes y objetivos de evaluación. Se conservan 2,477 territorios y se estiman 1,783; ausencia nunca equivale a riesgo cero. La evaluación también depende de la calidad observada del objetivo y no representa todos los municipios.</p><p>El rango de 2027 usa ±21.05 pp de error histórico de 2021. No garantiza cobertura futura del 90%. Semáforo en tercios relativos nacionales; no expresa probabilidades.</p><p>Escenario: alcance × tasa de abstención × respuesta supuesta. El alcance se limita por LN 2024 y supone que las personas alcanzadas presentan esa misma tasa observada. No se han demostrado efectos de una intervención ni costos.</p>';
 update();map.fitBounds(layer.getBounds(),{padding:[12,12]});detail(plan.selected[0]||records[0]);
}
function exportPlan(){
 const headers=['clave_ine','entidad','municipio','estimacion_2027_pct','rango_inferior_ilustrativo_pct','rango_superior_ilustrativo_pct','ln_referencia_2024','ns_2024_pct','alcance_limitado','respuesta_supuesta_pct','participacion_adicional_hipotetica','abstencion_escenario_pct','metodo','catalogo_entidad_constante','nota'];
 const cell=v=>{let s=String(v??'');if(typeof v==='string'&&/^[=+\-@]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
 const lines=plan.selected.map(r=>[r.key,r.state_name,r.name,r.risk,r.range_low,r.range_high,r.ln,r.latest_ns,r.served,Number($('response').value),r.additional,r.after,r.method,r.stable_catalog_state,'Hipótesis sin efecto causal demostrado; límites históricos sin armonizar']);
 const blob=new Blob(['\uFEFF'+[headers,...lines].map(row=>row.map(cell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='umbral_plan_atencion.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
load().catch(e=>{$('status').textContent='No se pudieron cargar los datos. Abre la demo mediante el servidor local indicado en README.';console.error(e);});

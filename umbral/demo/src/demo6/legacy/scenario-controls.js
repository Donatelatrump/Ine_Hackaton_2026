let defaultReachTerritory=null;
function simulationPopulationDefault(){
 const state=$('state').value;
 const exact=state?records.find(r=>r.state===state&&(r.key===$('search').value||r.name===$('search').value)):null;
 const key=exact?'municipio:'+exact.key:state?'estado:'+state:'pais';
 const population=exact?territoryPopulation2027.municipalities[exact.key]:state?territoryPopulation2027.states[state]:territoryPopulation2027.national;
 return {key,population:Number.isFinite(population)?population:null};
}
function syncDefaultReach(force=false){
 const selected=simulationPopulationDefault();
 if(force||selected.key!==defaultReachTerritory){
  $('reach').value=selected.population!==null?String(selected.population):'';
  defaultReachTerritory=selected.key;
 }
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
 syncDefaultReach();
}
// Actualizar resultados de exploración sin repintar ni reencuadrar el mapa histórico.

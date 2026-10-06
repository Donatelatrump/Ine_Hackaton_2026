const test=require('node:test');
const assert=require('node:assert/strict');
let decision;
try { decision=require('./decision.js'); } catch { decision={}; }
function api(){assert.equal(typeof decision.planScenario,'function','Falta implementar escenario real');return decision;}
test('clasifica por tasa y resuelve empates por clave, omitiendo ausencia',()=>{
 const r=api().planScenario([{key:'b',risk:50,observed:20},{key:'a',risk:50,observed:100},{key:'c',risk:null,observed:50}],1,10,25);
 assert.deepEqual(r.selected.map(x=>x.key),['a']);assert.equal(r.additional,1.25);
});
test('alcance no supera electorado y respuesta no produce tasas negativas',()=>{
 const r=api().planScenario([{key:'a',risk:50,observed:20}],50,1000,100);
 assert.equal(r.served,20);assert.equal(r.additional,10);assert.equal(r.after,0);
});
test('respuesta cero conserva escenario base',()=>{
 const r=api().planScenario([{key:'a',risk:60,observed:1000}],1,100,0);
 assert.equal(r.additional,0);assert.equal(r.before,r.after);
});
test('capacidad cero y filtro sin municipios producen selección vacía',()=>{
 assert.equal(api().planScenario([],50,1000,5).selected.length,0);
 assert.equal(api().planScenario([{key:'a',risk:60,observed:1000}],0,1000,5).served,0);
});
test('valores no finitos son rechazados',()=>{
 assert.throws(()=>api().planScenario([],1,NaN,5),/rango/);
});
test('escenario usa solo denominador observado, no LN con NS',()=>{
 const r=api().planScenario([{key:'a',risk:50,ln:100,observed:80}],1,80,100);
 assert.equal(r.before,50);assert.equal(r.after,0);assert.equal(r.served,80);
 assert.equal(api().planScenario([{key:'b',risk:50,ln:100}],1,80,100).selected.length,0);
});
test('tasa, volumen y deterioro generan lentes diferentes',()=>{
 const rows=[{key:'a',risk:70,baseline:69,observed:100},{key:'b',risk:50,baseline:30,observed:1000}];
 assert.equal(api().rank(rows,'tasa')[0].key,'a');assert.equal(api().rank(rows,'volumen')[0].key,'b');assert.equal(api().rank(rows,'deterioro')[0].key,'b');
});
test('frecuencia incluye seis variantes y distingue falta de elegibilidad',()=>{
 const rows=[{key:'a',risk:50,baseline:40,observed:100,variants:{ridge_5:50,persistencia_5:40,ridge_10:50,persistencia_10:40,ridge_20:50,persistencia_20:40}},
 {key:'b',risk:40,baseline:30,observed:100,variants:{ridge_5:null,persistencia_5:null,ridge_10:40,persistencia_10:30,ridge_20:40,persistencia_20:30}}];
 const f=api().selectionStability(rows,1,'tasa');assert.equal(f.a.frequency,1);assert.equal(f.a.robust,true);assert.equal(f.b.eligible,4);assert.equal(f.b.frequency,0);
});
test('inversión informa requisito, cero respuesta e imposibilidad',()=>{
 const r={key:'a',risk:60,observed:1000};
 assert.equal(api().inverseScenario(r,100,50,{low:30,high:50}).required_reach,334);
 assert.equal(api().inverseScenario(r,100,0,{low:30,high:50}).required_reach,null);
 assert.equal(api().inverseScenario(r,100,50,{low:30,high:50}).feasible_response,false);
});

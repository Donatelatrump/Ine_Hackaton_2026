const test=require('node:test');
const assert=require('node:assert/strict');
let decision;
try { decision=require('./decision.js'); } catch { decision={}; }
function api(){assert.equal(typeof decision.planScenario,'function','Falta implementar escenario real');return decision;}
test('clasifica por tasa y resuelve empates por clave, omitiendo ausencia',()=>{
 const r=api().planScenario([{key:'b',risk:50,ln:20},{key:'a',risk:50,ln:100},{key:'c',risk:null,ln:50}],1,10,25);
 assert.deepEqual(r.selected.map(x=>x.key),['a']);assert.equal(r.additional,1.25);
});
test('alcance no supera electorado y respuesta no produce tasas negativas',()=>{
 const r=api().planScenario([{key:'a',risk:50,ln:20}],50,1000,100);
 assert.equal(r.served,20);assert.equal(r.additional,10);assert.equal(r.after,0);
});
test('respuesta cero conserva escenario base',()=>{
 const r=api().planScenario([{key:'a',risk:60,ln:1000}],1,100,0);
 assert.equal(r.additional,0);assert.equal(r.before,r.after);
});
test('capacidad cero y filtro sin municipios producen selección vacía',()=>{
 assert.equal(api().planScenario([],50,1000,5).selected.length,0);
 assert.equal(api().planScenario([{key:'a',risk:60,ln:1000}],0,1000,5).served,0);
});
test('valores no finitos son rechazados',()=>{
 assert.throws(()=>api().planScenario([],1,NaN,5),/rango/);
});

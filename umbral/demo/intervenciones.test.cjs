const test=require('node:test');
const assert=require('node:assert/strict');
const D=require('./decision.js');
const rows=[{key:'a',risk:60,observed:50000}];
test('proporcional reparte cobertura según población y conserva total entero',()=>{
 const all=[{key:'a',risk:60,observed:1000},{key:'b',risk:40,observed:9000}];
 const p=D.planIntervention(all,{budget:1000,reach:1000,action:'sms_suecia',distribution:'proporcional'});
 assert.deepEqual(p.selected.map(r=>[r.key,r.served]),[['a',100],['b',900]]);
 assert.equal(p.served,1000);assert.equal(p.additional,3);
});
test('mayor resto resuelve empates por clave, sin exceder población o presupuesto',()=>{
 const all=['c','b','a'].map(key=>({key,risk:50,observed:10}));
 const p=D.planIntervention(all,{budget:2,reach:2,action:'sms_suecia',distribution:'proporcional'});
 assert.deepEqual(p.selected.map(r=>[r.key,r.served]),[['a',1],['b',1]]);
 const full=D.planIntervention(all,{budget:100,reach:100,action:'sms_suecia',distribution:'proporcional'});
 assert.equal(full.served,30);assert.ok(full.selected.every(r=>r.served<=r.observed));
 assert.throws(()=>D.planIntervention(all,{budget:1.5,reach:2,distribution:'proporcional'}));
 assert.throws(()=>D.planIntervention(all,{budget:2,reach:2,distribution:'inventada'}));
});
test('resumen territorial incluye municipios sin atender y pondera la base completa',()=>{
 const all=[{key:'a',risk:60,observed:1000},{key:'b',risk:40,observed:9000}];
 const p=D.planIntervention(all,{budget:1000,reach:1000,action:'sms_suecia'});
 const t=D.territorialScenario(all,p);
 assert.equal(t.before,42);assert.equal(t.after,41.97);assert.equal(t.population,10000);
 assert.equal(t.additional,3);assert.equal(t.municipalities,2);assert.equal(t.selected,1);
});
test('SMS usa efecto ITT en pp sobre asignados, sin multiplicar por abstención',()=>{
 const p=D.planIntervention(rows,{capacity:1,reach:10000,action:'sms_suecia'});
 assert.equal(p.additional,30);assert.equal(p.additional_low,13);assert.equal(p.additional_high,48);
 assert.ok(Math.abs(p.after-59.94)<1e-9);assert.equal(p.action.estimand,'ITT');
});
test('llamada usa contactos efectivos y conserva incertidumbre no disponible',()=>{
 const p=D.planIntervention(rows,{capacity:1,reach:1000,action:'plan_voto'});
 assert.equal(p.additional,41);assert.equal(p.additional_low,null);assert.equal(p.action.estimand,'ATT');
});
test('sin intervención conserva selección y base, sin contactos ficticios',()=>{
 const p=D.planIntervention(rows,{capacity:1,reach:1000,action:'ninguna'});
 assert.equal(p.selected.length,1);assert.equal(p.served,0);assert.equal(p.after,p.before);
});
test('capacidad humana limita cobertura y los efectos no exceden abstención disponible',()=>{
 const p=D.planIntervention([{key:'a',risk:0.1,observed:100}],{budget:80,reach:1000,action:'plan_voto'});
 assert.equal(p.served,80);assert.equal(p.additional,0.08);assert.ok(Math.abs(p.after-0.02)<1e-9);
});
test('personalizado conserva fórmula anterior sin adjudicarle una fuente',()=>{
 const p=D.planIntervention(rows,{capacity:1,reach:1000,action:'personalizada',response:5});
 assert.equal(p.additional,30);assert.equal(p.action.source,null);assert.equal(p.additional_low,null);
});
test('rechaza acciones desconocidas, valores inválidos y alcance fraccionario',()=>{
 assert.throws(()=>D.planIntervention(rows,{capacity:1,reach:100,action:'inventada'}));
 assert.throws(()=>D.planIntervention(rows,{capacity:1,reach:NaN,action:'sms_suecia'}));
 assert.throws(()=>D.planIntervention(rows,{capacity:1,reach:1.5,action:'sms_suecia'}));
});

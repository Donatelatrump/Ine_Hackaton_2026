const test=require('node:test');
const assert=require('node:assert/strict');
const A=require('./src/demo6/domain/analytics.js');
const record=(key,rate,weight)=>({key,state:'01',name:'Municipio '+key,state_name:'Estado',
  baseline:rate,ridge:rate,observed:weight,ln:weight,latest_ns:0,stable_catalog_state:true,
  history:[{year:2009,risk:rate,ln:weight,ns:0}]});

test('el agregado pondera población y declara la cobertura excluida',()=>{
  const result=A.summary([record('01001',10,10),record('01002',90,90),record('01003',null,100)],2027,'baseline');
  assert.equal(result.rate,82);
  assert.equal(result.valid,2);
  assert.equal(result.missing,1);
  assert.equal(result.populationCoverage,50);
});
test('un histórico observable no depende de tener proyección y excluye NS del denominador',()=>{
  const r=record('01001',null,100);
  r.history=[{year:2009,risk:40,ln:100,ns:20}];
  assert.deepEqual(A.observation(r,2009),{rate:40,weight:80,ln:100,ns:20});
  assert.equal(A.summary([r],2009,'ridge').rate,40);
  assert.equal(A.summary([r],2027,'ridge').rate,null);
});
test('datos ausentes permanecen vacíos en el CSV y se conservan comillas y filas',()=>{
  const r=record('01001',null,100);r.name='Municipio "A"';
  const csv=A.csv([r],{year:2027,method:'baseline'},{});
  assert.ok(csv.includes('Municipio ""A""'));
  assert.ok(csv.includes('"Proyección exploratoria","Referencia de 2021","",""'));
  assert.equal(csv.split('\r\n').length,2);
});
test('los métodos no alteran lo observado y la serie histórica no incorpora años futuros',()=>{
  const r=record('01001',40,100);r.ridge=60;
  r.history.push({year:2024,risk:30,ln:100,ns:0});
  assert.equal(A.observation(r,2009,'ridge').rate,A.observation(r,2009,'baseline').rate);
  assert.deepEqual(A.series([r],'ridge',2009).map(p=>p.year),[2009]);
  assert.deepEqual(A.series([r],'ridge').map(p=>p.year),[2009,2024,2027]);
  assert.equal(A.initialMethod({selected_model:'persistencia'}),'baseline');
});

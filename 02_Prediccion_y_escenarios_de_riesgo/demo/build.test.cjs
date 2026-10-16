const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const vm=require('node:vm');
const root=__dirname;
const config=JSON.parse(fs.readFileSync(path.join(root,'build.config.json'),'utf8'));
const build=JSON.parse(fs.readFileSync(path.join(root,'assets/build.json'),'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

test('el manifiesto declara fuentes únicas dentro de demo',()=>{
  const sources=[config.analytics,...config.scripts,...config.styles];
  assert.equal(new Set(sources).size,sources.length);
  for(const relative of sources){
    const absolute=path.resolve(root,relative);
    assert.ok(absolute.startsWith(root+path.sep));
    assert.ok(fs.statSync(absolute).isFile());
  }
});

test('la compilación corresponde a las fuentes, configuración y generador actuales',()=>{
  for(const [file,hash] of Object.entries(build.sources))assert.equal(sha(path.join(root,file)),hash,file);
  for(const [file,hash] of Object.entries(build.outputs))assert.equal(sha(path.join(root,'assets',file)),hash,file);
  assert.equal(sha(path.join(root,'build.config.json')),build.config_sha256);
  assert.equal(sha(path.join(root,'../tools/construir_web.py')),build.builder_sha256);
});

test('el paquete tiene sintaxis válida y no contiene sondeos de arranque',()=>{
  const source=fs.readFileSync(path.join(root,'assets/demo6.js'),'utf8');
  assert.doesNotThrow(()=>new vm.Script(source));
  assert.doesNotMatch(source,/\bsetInterval\s*\(/);
  assert.doesNotMatch(source,/window\.__backToNacional\s*=/);
});

test('demo6 carga los paquetes propios sin scripts o estilos de otras demos',()=>{
  const html=fs.readFileSync(path.join(root,'demo6.html'),'utf8');
  assert.match(html,/assets\/demo6\.js/);
  assert.match(html,/assets\/demo6\.css/);
  assert.doesNotMatch(html,/(?:src|href)="(?:demo[245][^"/]*\.(?:js|css)|style\.css)/);
});

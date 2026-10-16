"""Migración explícita de recursos de demo6, sin modificar datos ni modelos."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
TRACK=ROOT/'02_Prediccion_y_escenarios_de_riesgo'
DEMO=TRACK/'demo'
changes=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def move(old,new):
 src=DEMO/old;dst=DEMO/new
 if dst.exists():raise FileExistsError(dst)
 before=digest(src);dst.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(src),str(dst))
 changes.append({'from':str(src.relative_to(ROOT)).replace('\\','/'),'to':str(dst.relative_to(ROOT)).replace('\\','/'),'sha256_before':before,'sha256_after_move':digest(dst)})

# Extraer solamente vistas descriptivas. El controlador conserva coordinación y eventos.
p=DEMO/'demo6.js';controller=p.read_text(encoding='utf-8')
def section(start,end):return controller[controller.index(start):controller.index(end)]
summary=section('  function metricCard(', '  function segments(')
history=section('  function segments(', '  function renderEvidence(')
evidence=section('  function renderEvidence(', '  function renderScenario(')
contexts={
 'summary':('A,state,selectedRecords,territoryLabel,records,view,$,pct,fmt,esc',summary,'renderSummary'),
 'history':('A,state,selectedRecords,territoryLabel,view,$,pct,fmt,esc',history,'renderHistory'),
 'evidence':('state,metadata,name,$,fmt,esc',evidence,'renderEvidence')}
for filename,(args,body,fn) in contexts.items():
 dst=DEMO/f'src/demo6/views/{filename}.js';dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text("/* Vista descriptiva; dependencias recibidas explícitamente. */\n(() => {\n  'use strict';\n  window.UmbralDemo6Views=window.UmbralDemo6Views||{};\n  window.UmbralDemo6Views."+fn+'=function({'+args+'}){\n'+body+'\n    '+fn+'();\n  };\n})();\n',encoding='utf-8')
start=controller.index('  function metricCard(');end=controller.index('  function renderScenario(')
controller=controller[:start]+controller[end:]
controller=controller.replace('    renderSummary();renderHistory();renderEvidence();renderScenario();',
 '''    const context={A,state,selectedRecords,territoryLabel,records,view,metadata,name,$,pct,fmt,esc};
    const views=window.UmbralDemo6Views;
    views.renderSummary(context);views.renderHistory(context);views.renderEvidence(context);
    renderScenario();''')
p.write_text(controller,encoding='utf-8')

moves={
 'demo6-core.js':'src/demo6/domain/analytics.js',
 'demo6-app.js':'src/demo6/legacy/application.js',
 'demo6-geografia.js':'src/demo6/map/geography.js',
 'demo6-map.js':'src/demo6/map/layers.js',
 'demo6-buscadores.js':'src/demo6/ui/search.js',
 'demo6-ficha.js':'src/demo6/views/state-profile.js',
 'demo6.js':'src/demo6/controller.js',
 'demo6.css':'styles/demo6/main.css'}
for old,new in moves.items():move(old,new)
css=DEMO/'styles/demo6/main.css';text=css.read_text(encoding='utf-8')
marker='/* Contexto estatal antes de la simulación opcional. */'
pos=text.index(marker)
(css.parent/'state-profile.css').write_text(text[pos:],encoding='utf-8')
css.write_text(text[:pos].rstrip()+'\n',encoding='utf-8')
html=DEMO/'demo6.html';text=html.read_text(encoding='utf-8')
for old,new in moves.items():text=text.replace('"'+old+'?','"'+new+'?')
text=text.replace('20261016-modelos','20261016-estructura').replace('20261016-fichas','20261016-estructura')
text=text.replace('  <script defer src="src/demo6/controller.js',
 '''  <script defer src="src/demo6/views/summary.js?v=20261016-estructura"></script>
  <script defer src="src/demo6/views/history.js?v=20261016-estructura"></script>
  <script defer src="src/demo6/views/evidence.js?v=20261016-estructura"></script>
  <script defer src="src/demo6/controller.js''')
text=text.replace('  <script defer src="vendor/leaflet.js">', '  <link rel="stylesheet" href="styles/demo6/state-profile.css?v=20261016-estructura">\n  <script defer src="vendor/leaflet.js">')
html.write_text(text,encoding='utf-8')
test=DEMO/'demo6.test.cjs';test.write_text(test.read_text(encoding='utf-8').replace("require('./demo6-core.js')","require('./src/demo6/domain/analytics.js')"),encoding='utf-8')
for filename in ['DEMO6.md','FICHAS_ESTATALES.md']:
 p=DEMO/filename;text=p.read_text(encoding='utf-8')
 for old,new in moves.items():text=text.replace('`'+old+'`','`'+new+'`')
 p.write_text(text,encoding='utf-8')
# Capturas y copias de depuración quedan como archivo histórico, fuera de recursos activos.
for p in list(DEMO.iterdir()):
 if not p.is_file():continue
 snapshot=p.name.startswith('_') and (p.suffix in ['.png','.html'] or p.name.startswith(('_prev_','_log_')) or p.name in ['_oraculo_geo_prev.js','_oraculo_demo5_sin_red.js'])
 if snapshot or p.name.endswith('-err.txt'):move(p.name,'archivo/depuracion/'+p.name)
out=TRACK/'arquitectura';out.mkdir(exist_ok=True)
(out/'migracion_demo6.json').write_text(json.dumps({'note':'Recursos activos actualizados en demo6.html. Hashes registrados al mover; las vistas y estilos se separan después. El archivo de depuración contiene instantáneas históricas.','moves':changes},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(changes)} archivos reubicados; tres vistas y dos hojas de estilo separadas.')

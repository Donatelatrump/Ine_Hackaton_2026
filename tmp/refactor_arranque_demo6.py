from pathlib import Path
import shutil,json
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo';S=D/'src/demo6'
backup=ROOT/'tmp/demo6/antes_arranque';backup.mkdir(parents=True,exist_ok=True)
shutil.copytree(S,backup/'src',dirs_exist_ok=True);shutil.copy2(D/'demo6.html',backup/'demo6.html')
def write(path,text):
 p=S/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
app=(S/'legacy/application.js').read_text(encoding='utf-8')
anchors=[('app/context.js',"'use strict';"),('legacy/scenarios.js','function preventive('),('views/municipality.js','function perfilCell('),('legacy/scenario-controls.js','function simulationMunicipalities('),('app/exploration.js','function updateExplorationAnalysis('),('app/render.js','function update(){'),('legacy/scenario-export.js','function exportPlan('),('ui/lenses.js','function initLensCards('),('legacy/scenario-evidence.js','function renderActionEvidence('),('app/bootstrap.js','function load(){')]
for i,(file,start) in enumerate(anchors):
 begin=app.index(start);end=app.index(anchors[i+1][1]) if i+1<len(anchors) else app.index('try{load();}')
 text=app[begin:end]
 if file=='app/render.js':
  text=text.replace('function update(){','function renderApplication(){',1)
  text+='\nfunction update(){\n  runtime.hooks.beforeUpdate();\n  try{return renderApplication();}\n  finally{runtime.hooks.afterUpdate();}\n}\n'
 if file=='app/exploration.js':
  text=text.replace('function updateExplorationAnalysis(){','function renderExplorationAnalysis(){',1)
  text+='\nfunction updateExplorationAnalysis(){\n  try{return renderExplorationAnalysis();}\n  finally{runtime.hooks.afterExplore();}\n}\n'
 if file=='legacy/scenario-controls.js':
  text=text.replace(" geographyFocusKey=null;geographyHistory.length=0;\n update();\n}"," geographyFocusKey=null;geographyHistory.length=0;\n update();\n runtime.hooks.afterScope();\n}",1)
 text=text.replace('L.canvas(', 'createMapRenderer(')
 write(file,text)
(S/'legacy/application.js').unlink()

# El estado del módulo, las vistas y los hooks quedan dentro de una única clausura privada.
write('app/runtime.js',"""/* Conexiones explícitas; el generador mantiene todo este estado en una clausura privada. */
const runtime={
  views:{},renderProfile:null,startController:null,mapStyles:{},selectMunicipality:null,
  hooks:{beforeUpdate(){},afterUpdate(){},afterExplore(){},afterFocus(){},afterScope(){}}
};
""")
write('map/renderer.js',"""/* Renderer local: no modifica L.canvas ni otras APIs de Leaflet. */
function createMapRenderer(options){
  return L.Browser.svg&&typeof L.svg==='function'?L.svg(options):L.canvas(options);
}
""")
for p in (S/'views').glob('*.js'):
 text=p.read_text(encoding='utf-8').replace('window.UmbralDemo6Views','runtime.views').replace('window.renderDemo6Ficha','runtime.renderProfile')
 p.write_text(text,encoding='utf-8')
geo=(S/'map/geography.js').read_text(encoding='utf-8').replace('L.canvas(','createMapRenderer(')
geo=geo.replace(" map.fitBounds(polygon.getBounds(), {padding:[30,30],maxZoom:10,animate:true});\n}"," map.fitBounds(polygon.getBounds(), {padding:[30,30],maxZoom:10,animate:true});\n runtime.hooks.afterFocus();\n}")
geo=geo.replace('function selectMunicipalityResult(key){','function selectMunicipalityResult(key){\n if(runtime.selectMunicipality)return runtime.selectMunicipality(key);')
write('map/geography.js',geo)
layers=(S/'map/layers.js').read_text(encoding='utf-8')
layers=layers[:layers.index('/* Espera a que aplicacion.js')]
start=layers.index('function estiloMunicipal(');end=layers.index('function removerCapasDemo5(')
layers=layers[:start]+'''function estiloMunicipal(year,stateKey){return runtime.mapStyles.municipality(year,stateKey);}
function estiloEstado(year){return runtime.mapStyles.state(year);}

'''+layers[end:]
write('map/layers.js',layers)
c=(S/'controller.js').read_text(encoding='utf-8')
c=c.replace('window.UmbralDemo6Views','runtime.views').replace('window.renderDemo6Ficha','runtime.renderProfile')
start=c.index('    const originalUpdate=update;');end=c.index('    // Los controles comparten selección')
c=c[:start]+'''    runtime.hooks.beforeUpdate=()=>{
      const active=$('method').value==='baseline'?'ridge':$('method').value;
      for(const r of records){
        for(const limit of [5,10,20]){
          r.variants['persistencia_'+limit]=r.model_variants?.baseline?.[limit]??null;
          r.variants['ridge_'+limit]=r.model_variants?.[active]?.[limit]??null;
        }
      }
    };
    runtime.hooks.afterUpdate=()=>{
      if(currentMapYear!==2027)updateExplorationAnalysis();
      repaint();
    };
    runtime.hooks.afterExplore=refresh;
    runtime.hooks.afterFocus=refresh;
    runtime.selectMunicipality=selectMunicipality;
    runtime.hooks.afterScope=()=>{
      if($('simulation-scope').value==='municipio'){
        const key=$('simulation-municipality').value;
        const polygon=layer.getLayers().find(p=>p.feature.properties.key===key);
        if(polygon)focusMunicipality(key,polygon);
      }else{reconstruirMapa(currentMapYear);}
      refresh();
    };
'''+c[end:]
c=c.replace('estiloEstado=year=>feature=>{','runtime.mapStyles.state=year=>feature=>{').replace('estiloMunicipal=(year,stateKey)=>feature=>{','runtime.mapStyles.municipality=(year,stateKey)=>feature=>{')
c=c.replace('  const timer=setInterval(()=>{if(init())clearInterval(timer);},60);','  runtime.startController=init;')
c=c.replace('selectMunicipality,refresh,preset});','selectMunicipality,refresh,preset,returnToMexico:volverAMexico,inspect});')
insert='''  // Instantánea de diagnóstico: valores copiados, sin referencias mutables a mapas o registros.
  function inspect(){
    const rows=(view.length?view:records).filter(r=>r.state===state.state);
    const center=map.getCenter();
    return Object.freeze({
      focusKey:geographyFocusKey,
      map:Object.freeze({lat:center.lat,lng:center.lng,zoom:map.getZoom()}),
      stateRate:A.summary(rows,state.year,state.method).rate,
      municipalityRate:state.municipality?A.observation(byKey.get(state.municipality),state.year,state.method).rate:null,
      additional:plan?.additional??0,
      stateFill:state.state?estiloEstado(state.year)({properties:{state:state.state}}).fillColor:null,
      thresholds:Object.freeze({...mapThresholds()})
    });
  }
'''
c=c.replace('  function init(){',insert+'  function init(){',1)
write('controller.js',c)

decoration=(D/'demo4.js').read_text(encoding='utf-8')
decoration=decoration.replace('(() => {','function initMapDecorations(){',1)
decoration=decoration[:decoration.index("  // Keep Leaflet's native zoom transition")]+ '}\n'
write('map/decorations.js',decoration)
write('ui/motion.js',(D/'demo2.js').read_text(encoding='utf-8'))
write('app/start.js',"""/* Arranque síncrono después de cargar datos y definiciones; sin sondeos por intervalos. */
try{
  load();
  initMapDecorations();
  initDemo5();
  if(!runtime.startController())throw Error('No se pudo iniciar el controlador de demo6');
  document.dispatchEvent(new CustomEvent('umbral:ready'));
}catch(error){
  $('status').textContent='No se pudo iniciar la aplicación. Revisa los recursos locales.';
  console.error(error);
}
""")
# Estilos propios de demo6: fuentes independientes de los archivos de demos anteriores.
styles=[]
for source,dest in [('style.css','foundation.css'),('demo2.css','layout.css'),('demo4.css','identity.css'),('demo5.css','map.css')]:
 shutil.copy2(D/source,D/'styles/demo6'/dest);styles.append('styles/demo6/'+dest)
styles+=['styles/demo6/main.css','styles/demo6/state-profile.css']
scripts=['app/runtime.js','map/renderer.js','map/geography.js','ui/search.js']+[f for f,_ in anchors]
scripts.remove('app/context.js');scripts.insert(1,'app/context.js')
scripts+=['ui/motion.js','map/layers.js','map/decorations.js','views/state-profile.js','views/summary.js','views/history.js','views/evidence.js','controller.js','app/start.js']
manifest={'analytics':'src/demo6/domain/analytics.js','scripts':['src/demo6/'+f for f in scripts],'styles':styles}
(D/'build.config.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
html=(D/'demo6.html').read_text(encoding='utf-8')
import re
html=re.sub(r'  <link rel="stylesheet" href="(?!vendor/)[^"]+">\n','',html)
html=html.replace('  <script defer src="vendor/leaflet.js">','  <link rel="stylesheet" href="assets/demo6.css?v=20261016-modular">\n  <script defer src="vendor/leaflet.js">')
html=re.sub(r'  <script defer src="(?:src/demo6/|demo4-bootstrap|demo2\.js|demo4\.js)[^\"]*"></script>\n','',html)
html=html.replace('</head>','  <script defer src="assets/demo6.js?v=20261016-modular"></script>\n</head>')
(D/'demo6.html').write_text(html,encoding='utf-8')
print('Fuentes separadas, arranque explícito y manifest de compilación escritos.')

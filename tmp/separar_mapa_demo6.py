from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo';S=D/'src/demo6'
names={'demo5Iniciado':'mapInitialized','demo5ModoHistorico':'historicalMapEnabled','demo5LayerMunicipal':'municipalityLayer','demo5LayerEstado':'stateOverlayLayer','demo5LayerLimites':'boundaryLayer','demo5LayerContexto':'contextLayer','demo5EstadoActivo':'activeMapState','demo5EstadoCapaMunicipal':'municipalityLayerState','demo5RendererMunicipal':'municipalityRenderer','demo6RendererEstado':'stateRenderer','demo5PintarSeleccionMunicipal':'paintMapSelection','demo5SincronizarNivel':'syncMapLevel','demo5SeleccionarEstado':'selectMapState','removerCapasDemo5':'removeMapLayers','initDemo5':'initMapLayers'}
for p in S.rglob('*.js'):
 if p.name=='analytics.js':continue
 s=p.read_text(encoding='utf-8')
 for old,new in names.items():s=re.sub(r'\b'+old+r'\b',new,s)
 s=s.replace('demo5:','Umbral map:')
 p.write_text(s,encoding='utf-8')
p=S/'map/layers.js';s=p.read_text(encoding='utf-8')
# Tres helpers obsoletos no son referenciados por ninguna fuente del bundle.
dead=s[s.index('function stateRiskLevel('):s.index('function estiloMunicipal(')]
for name in ['stateRiskLevel','getJovenesPoblacionEstado','calcularImpactoTeorico']:
 assert sum(len(re.findall(r'\b'+name+r'\b',f.read_text(encoding='utf-8'))) for f in S.rglob('*.js'))==1,name
s=s.replace(dead,'')
sections=[('map/context.js','/* ====='),('map/years.js','function getAvailableYears('),('map/styles.js','function estiloMunicipal('),('map/layers.js','function removeMapLayers('),('map/navigation.js','function volverAMexico('),('map/start.js','function initMapLayers(')]
for i,(dest,start) in enumerate(sections):
 a=s.index(start);b=s.index(sections[i+1][1]) if i+1<len(sections) else len(s)
 (S/dest).write_text(s[a:b].replace('/* ===== DEMO 5: mapa histórico por año y plan recomendado por estado ===== */','/* Estado privado de las capas y la navegación de demo6. */'),encoding='utf-8')
config=json.loads((D/'build.config.json').read_text(encoding='utf-8'))
config['scripts'].insert(config['scripts'].index('src/demo6/map/renderer.js'),'src/demo6/map/context.js')
i=config['scripts'].index('src/demo6/map/layers.js')
config['scripts'][i:i+1]=['src/demo6/'+dest for dest,_ in sections if dest!='map/context.js']
(D/'build.config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')

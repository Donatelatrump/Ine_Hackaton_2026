from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo6.py'
s=p.read_text(encoding='utf-8')
s=s.replace("OUT=ROOT/'tmp/demo6'","OUT=ROOT/'tmp/demo6/modular'")
s=s.replace('OUT.mkdir(parents=True,exist_ok=True)','OUT.mkdir(parents=True,exist_ok=True)')
s=s.replace("geographyFocusKey==='01001'","Umbral6.inspect().focusKey==='01001'")
s=s.replace('!geographyFocusKey','!Umbral6.inspect().focusKey')
s=s.replace("UmbralAnalytics.summary(view.filter(r=>r.state==='01'),2027,'hgb').rate","Umbral6.inspect('01').stateRate")
s=s.replace('[map.getCenter().lat,map.getCenter().lng,map.getZoom()]',"Object.values(Umbral6.inspect().map)")
s=s.replace("UmbralAnalytics.summary([byKey.get('01001')],2027,document.getElementById('method').value).rate","Umbral6.inspect().municipalityRate")
s=s.replace('plan.additional','Umbral6.inspect().additional').replace('volverAMexico()','Umbral6.returnToMexico()')
old="estiloEstado(2027)({properties:{state:'01'}}).fillColor===colors[Decision.level(Umbral6.inspect('01').stateRate,{low:quantile(records.map(r=>r.hgb).filter(Number.isFinite),1/3),high:quantile(records.map(r=>r.hgb).filter(Number.isFinite),2/3)})]"
new="(()=>{const d=Umbral6.inspect('01');return d.stateFill===({bajo:'#8bbbad',medio:'#e8b451',alto:'#bd5472',sin_datos:'#8997ab'})[Decision.level(d.stateRate,d.thresholds)];})()"
assert old in s
s=s.replace(old,new)
s=s.replace("assert page.locator('#method').input_value()=='hgb'", "assert page.locator('#method').input_value()=='hgb'\n    assert page.evaluate(\"typeof records==='undefined' && typeof map==='undefined' && typeof geographyFocusKey==='undefined' && !window.UmbralDemo6Views && !window.UmbralAnalytics\")\n    assert page.evaluate(\"typeof window.__backToNacional==='undefined'\")")
p.write_text(s,encoding='utf-8')

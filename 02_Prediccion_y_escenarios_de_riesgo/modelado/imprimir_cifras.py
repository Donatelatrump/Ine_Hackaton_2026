"""Comando único para reimprimir cifras citadas, sin reentrenamiento."""
import json
from pathlib import Path
d=json.loads((Path(__file__).resolve().parent/'salidas/resultados.json').read_text(encoding='utf-8'))
m=d['metadata'];pool=[r for r in d['municipios'] if r['stable_catalog_state']]
selected=sorted((r for r in pool if r['risk'] is not None),key=lambda r:(-r['risk'],r['key']))[:50]
counts={r['key']:0 for r in pool}
for v in ['persistencia_5','ridge_5','persistencia_10','ridge_10','persistencia_20','ridge_20']:
    for r in sorted((r for r in pool if r['variants'][v] is not None),key=lambda r:(-r['variants'][v],r['key']))[:50]:counts[r['key']]+=1
pop=sum(r['observed'] for r in selected);before=sum(r['risk']*r['observed'] for r in selected)/pop
add=sum(min(1000,r['observed'])*r['risk']/100*.05 for r in selected)
print(json.dumps({'equipo':'Tecnocalidos','cortes_originales':m['checks'],'cobertura':{k:m[k] for k in ['n_municipios','n_estimables','n_sin_estimacion']},'analisis_posterior':m['additional_evaluation'],
 'configuracion_inicial':{'metodo':'ridge','criterio':'tasa','catalogo_constante':True,'N':50,'alcance':1000,'respuesta_pct':5,'estimables':sum(r['risk'] is not None for r in pool),'nucleo_robusto':sum(counts[r['key']]==6 for r in selected),'seleccionados':len(selected),'observados_referencia':pop,'alcance_limitado':sum(min(1000,r['observed']) for r in selected),'adicional_hipotetica':add,'tasa_base':before,'tasa_escenario':before-100*add/pop},'advertencia':'Frecuencia no es probabilidad; escenario hipotético, NS fuera.'},ensure_ascii=True,allow_nan=False,indent=2))

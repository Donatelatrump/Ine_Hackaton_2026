"""Población CONAPO 2027 para los valores iniciales de alcance territorial."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[2]
source=ROOT/'fuentes/Bases_de_datos_explicativos/pobproy_inddemo.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
    municipalities={r['CLAVE'].zfill(5):int(float(r['POB_MIT_MUN'])) for r in csv.DictReader(f) if r['ANO']=='2027'}
states={}
for key,value in municipalities.items():states[key[:2]]=states.get(key[:2],0)+value
data={'year':2027,'source':'CONAPO · proyecciones municipales de población a mitad de año, pobproy_inddemo.csv','municipalities':municipalities,'states':states,'national':sum(states.values())}
target=ROOT/'umbral/demo/src/demo7/population.js'
target.write_text('const territoryPopulation2027=Object.freeze('+json.dumps(data,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
print('Población 2027 preparada:',len(municipalities),'municipios; Quintana Roo:',states['23'])

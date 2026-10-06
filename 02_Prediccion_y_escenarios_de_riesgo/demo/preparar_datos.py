"""Construye recursos locales; no altera fuentes ni polígonos originales."""
import sys, json, shutil, hashlib, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'.task_packages'))
from shapely.geometry import shape, mapping
DEMO=Path(__file__).resolve().parent
TRACK=DEMO.parent
def main():
    (DEMO/'data').mkdir(exist_ok=True)
    (DEMO/'vendor').mkdir(exist_ok=True)
    for name in ['resultados.json','metricas.json']:
        shutil.copyfile(TRACK/'modelado/salidas'/name,DEMO/'data'/name)
    source=TRACK/'cartografia/municipios_ine_2024.geojson'
    geo=json.loads(source.read_text(encoding='utf-8'))
    features=[]
    for f in geo['features']:
        g=shape(f['geometry']).simplify(.006,preserve_topology=True)
        assert not g.is_empty and g.geom_type in ['Polygon','MultiPolygon']
        features.append({'type':'Feature','properties':{'key':f['properties']['clave_municipio_ine']},'geometry':mapping(g)})
    output=DEMO/'data/municipios.geojson'
    output.write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (DEMO/'data/geometria_metadatos.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'features':len(features),'tolerance_degrees':.006,'purpose':'Solo visualización; no armonización histórica ni cálculo territorial','bytes':output.stat().st_size},ensure_ascii=False,indent=2),encoding='utf-8')
    for name in ['leaflet.js','leaflet.css']:
        url='https://unpkg.com/leaflet@1.9.4/dist/'+name
        urllib.request.urlretrieve(url,DEMO/'vendor'/name)
    urllib.request.urlretrieve('https://unpkg.com/leaflet@1.9.4/LICENSE',DEMO/'vendor/LICENSE')
    print(json.dumps({'features':len(features),'geometry_bytes':output.stat().st_size,'sample_properties':features[0]['properties']},ensure_ascii=True))
if __name__=='__main__':main()

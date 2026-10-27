"""Convierte cartografía INE a GeoJSON y verifica claves contra CCPC.
Dependencias: pyshp, pyproj; ZIP descargado de la fuente anotada en metadatos.
"""
import csv
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'.task_packages'))
import shapefile
from pyproj import CRS, Transformer

folder=ROOT/'cartografia'
version=int(sys.argv[1]) if len(sys.argv)>1 else 2023
assert version in (2023,2024)
source=folder/f'MUNICIPIO_cob_{version}.zip'
def normalized(value):
    value=''.join(c for c in unicodedata.normalize('NFKD',value.upper()) if not unicodedata.combining(c))
    return re.sub(r'[^A-Z0-9]','',value)

catalog={}
features=[]
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    files={Path(n).name.upper():n for n in z.namelist() if not n.endswith('/')}
    prj=z.read(files['MUNICIPIO.PRJ']).decode()
    transform=Transformer.from_crs(CRS.from_wkt(prj),CRS.from_epsg(4326),always_xy=True)
    with z.open(files['MUNICIPIO.SHP']) as s,z.open(files['MUNICIPIO.DBF']) as d,z.open(files['MUNICIPIO.SHX']) as x:
        reader=shapefile.Reader(shp=s,dbf=d,shx=x,encoding='utf-8')
        for sr in reader.iterShapeRecords():
            r=sr.record.as_dict()
            key=f"{r['ENTIDAD']:02d}{r['MUNICIPIO']:03d}"
            assert key not in catalog,key
            properties={'clave_municipio_ine':key,'entidad_ine':f"{r['ENTIDAD']:02d}",
              'municipio_ine':f"{r['MUNICIPIO']:03d}",'municipio_nombre':r['NOMBRE']}
            catalog[key]=properties
            xs,ys=zip(*sr.shape.points)
            lons,lats=transform.transform(xs,ys)
            assert all(-119<lon<-85 and 13<lat<34 for lon,lat in zip(lons,lats)),key
            sr.shape.points=list(zip(lons,lats))
            features.append({'type':'Feature','id':key,'properties':properties,'geometry':sr.shape.__geo_interface__})
    xml=z.read(files['MUNICIPIO.SHP.XML']).decode('utf-8')

(folder/f'municipios_ine_{version}.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
with (folder/f'catalogo_municipios_ine_{version}.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(next(iter(catalog.values()))));w.writeheader();w.writerows(catalog.values())
with source.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
metadata={'version':version,'fuente_pagina':f'https://pautas.ine.mx/transparencia/mapas/index_{version+1}.html',
 'fuente_zip':f'https://pautas.ine.mx/transparencia/mapas/cob_{version}/MUNICIPIO.zip',
 'fecha_descarga_utc':datetime.now(timezone.utc).isoformat(),'sha256':digest,
 'municipios':len(features),'fecha_creacion_metadatos':re.search(r'<CreaDate>(.*?)<',xml).group(1),
 'crs_original':prj,'crs_geojson':'WGS84 EPSG:4326, longitud/latitud',
 'advertencia':'Capa de referencia visual. No acredita identidad exacta con el corte CCPC de mayo 2023. La coincidencia de claves no demuestra estabilidad de límites históricos.',
 'capa_alternativa':'MUNICIPIO_ine_portal_2023.zip tiene metadatos 20220620; conservada solamente como fuente alternativa, no seleccionada.'}
(folder/f'metadatos_{version}.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('GeoJSON y catálogo generados:',len(features),flush=True)

base=ROOT/'datos_preparados/municipios_historico.csv'
if not base.exists():
    print('Comparación pendiente: todavía no existe la base municipal.',flush=True)
    raise SystemExit(0)
with base.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
matches=[]
names={}
for r in rows:
    key=r['clave_municipio_ine']; geo=catalog.get(key)
    state='clave_ausente_en_cartografia' if geo is None else ('clave_y_nombre_normalizado' if normalized(r['municipio_nombre'])==normalized(geo['municipio_nombre']) else 'clave_presente_nombre_por_revisar')
    matches.append({'ano':r['ano'],'clave_municipio_ine':key,'nombre_datos':r['municipio_nombre'],
      'nombre_cartografia':geo['municipio_nombre'] if geo else '', 'estado_correspondencia':state})
    names.setdefault(key,{}).setdefault(r['municipio_nombre'],[]).append(int(r['ano']))
with (ROOT/'auditoria/correspondencia_cartografia.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(matches[0]));w.writeheader();w.writerows(matches)
comparability=[]
for key,v in sorted(names.items()):
    years=sorted(y for ys in v.values() for y in ys)
    comparability.append({'clave_municipio_ine':key,'anos_presentes':';'.join(map(str,years)),
      'cantidad_anos':len(years),'nombres_observados':' | '.join(v),'nombres_distintos':len(v),
      'clave_en_cartografia':key in catalog,
      'observacion':'requiere_revision_de_nombre_o_territorio' if len(v)>1 or len(years)<6 else 'seis_anos_presentes_limites_no_verificados'})
with (ROOT/'auditoria/comparabilidad_municipal.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=list(comparability[0]));w.writeheader();w.writerows(comparability)
summary={year:dict(Counter(m['estado_correspondencia'] for m in matches if m['ano']==year)) for year in sorted({r['ano'] for r in rows})}
(ROOT/'auditoria/resumen_cartografia.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/f'auditoria/resumen_cartografia_{version}.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True),flush=True)

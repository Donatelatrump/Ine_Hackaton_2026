"""Añade banderas de calidad y realiza una conciliación independiente con CSV estándar."""
import csv
import hashlib
import json
import zipfile
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

rows=read_csv(ROOT/'datos_preparados/municipios_historico.csv')
audits=json.loads((ROOT/'auditoria/auditoria_archivos.json').read_text(encoding='utf-8'))
annual=json.loads((ROOT/'auditoria/resumen_anual.json').read_text())
assert len(audits)==192 and len(rows)==14779
keys=[(r['ano'],r['clave_municipio_ine']) for r in rows]
assert len(set(keys))==len(keys)
mapping={(r['ano'],r['clave_municipio_ine']):r for r in read_csv(ROOT/'auditoria/correspondencia_cartografia.csv')}
history={r['clave_municipio_ine']:r for r in read_csv(ROOT/'auditoria/comparabilidad_municipal.csv')}
for r in rows:
    m=mapping[(r['ano'],r['clave_municipio_ine'])];h=history[r['clave_municipio_ine']]
    r['estado_correspondencia_cartografia']=m['estado_correspondencia']
    r['municipio_nombre_cartografia']=m['nombre_cartografia']
    r['anos_disponibles']=h['cantidad_anos']
    r['nombres_historicos_distintos']=h['nombres_distintos']
    r['cartografia_referencia']='INE cob_2024; metadatos 20240509'
    flags=[]
    if r['observacion']:flags.append(r['observacion'])
    if float(r['no_especificados_pct'] or 0)>10:flags.append('no_especificados_mayor_10pct')
    if int(r['ln_edad_mayor_120'])>0:flags.append('conteos_con_edad_mayor_120')
    if h['cantidad_anos']!='6':flags.append('historial_incompleto')
    if int(h['nombres_distintos'])>1:flags.append('nombre_historico_variable')
    if m['estado_correspondencia']!='clave_y_nombre_normalizado':flags.append('nombre_cartografia_por_revisar')
    r['alertas_calidad']=';'.join(flags)
    assert int(r['ln'])==int(r['sv'])+int(r['nv'])+int(r['ns'])
    if int(r['sv'])+int(r['nv']):
        assert abs(float(r['abstencion_pct'])-100*int(r['nv'])/(int(r['sv'])+int(r['nv'])))<1e-9
        assert abs(float(r['participacion_pct'])+float(r['abstencion_pct'])-100)<1e-9
    else:assert r['abstencion_pct']=='' and r['participacion_pct']==''
write_csv(ROOT/'datos_preparados/municipios_historico_con_calidad.csv',rows)

# Un lector distinto del motor de agregación verifica un archivo real completo.
independent=defaultdict(lambda:[0,0,0,0])
with zipfile.ZipFile(ROOT/'DatosAbiertos_DECEyEC_ConteosCensales2024.zip') as z:
    name=next(n for n in z.namelist() if n.endswith('_ags.csv'))
    with z.open(name) as f:
        for r in csv.DictReader(TextIOWrapper(f,encoding='utf-8-sig',newline='')):
            key=f"{int(r['EDOCVE']):02d}{int(r['MPIOCVE']):03d}"
            for i,c in enumerate(['LN','SV','NV','NS']):independent[key][i]+=int(r[c])
for r in rows:
    if r['ano']=='2024' and r['entidad_ine']=='01':
        assert independent[r['clave_municipio_ine']]==[int(r[c]) for c in ['ln','sv','nv','ns']]

originals=json.loads((ROOT/'auditoria/inventario_local.json').read_text(encoding='utf-8'))
for entry in originals['zips']:
    with (ROOT/entry['archivo']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==entry['sha256']

geometry=json.loads((ROOT/'cartografia/municipios_ine_2024.geojson').read_text(encoding='utf-8'))
geo_keys={f['properties']['clave_municipio_ine'] for f in geometry['features']}
assert len(geometry['features'])==len(geo_keys)==2477
assert set(r['clave_municipio_ine'] for r in rows)<=geo_keys
assert all(f['geometry']['type'] in ('Polygon','MultiPolygon') for f in geometry['features'])

summary={'filas_originales':sum(a['filas'] for a in audits),'registros_municipio_ano':len(rows),
 'claves_municipales':len(history),'municipios_con_seis_anos':sum(h['cantidad_anos']=='6' for h in history.values()),
 'municipios_con_historia_incompleta':sum(h['cantidad_anos']!='6' for h in history.values()),
 'claves_con_nombres_historicos_distintos':sum(int(h['nombres_distintos'])>1 for h in history.values()),
 'registros_sin_observaciones':sum(r['observacion']=='sin_datos_observados' for r in rows),
 'registros_ns_mayor_10pct':sum(float(r['no_especificados_pct'] or 0)>10 for r in rows),
 'filas_edad_mayor_120':sum(a['filas_edad_mayor_120'] for a in audits),
 'ln_edad_mayor_120':sum(a['ln_edad_mayor_120'] for a in audits),
 'registros_municipales_con_edad_mayor_120':sum(int(r['ln_edad_mayor_120'])>0 for r in rows),
 'edades_min_max':[min(a['edad_min'] for a in audits),max(a['edad_max'] for a in audits)],
 'verificacion_independiente':'CSV Aguascalientes 2024 completo; LN/SV/NV/NS coinciden por municipio.',
 'hashes_originales_sin_cambios':True,'cobertura_claves_cartografia_pct':100,
 'cartografia_metadatos':'20240509','limites_historicos_armonizados':False,
 'def_vacio_o_no_numerico':sum(a['def_faltante']+a['def_no_numerico'] for a in audits),
 'del_vacio_o_no_numerico':sum(a['del_faltante']+a['del_no_numerico'] for a in audits)}
(ROOT/'auditoria/verificacion_final.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True),flush=True)

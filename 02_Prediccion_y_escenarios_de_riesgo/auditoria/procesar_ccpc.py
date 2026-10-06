"""Auditoría completa y agregación reproducible de los seis ZIP CCPC.

Ejecutar desde el workspace: python 02_Prediccion_y_escenarios_de_riesgo/auditoria/procesar_ccpc.py
Dependencia: duckdb (también admite .task_packages del workspace).
"""
import csv
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / '.task_packages'))
import duckdb

OUT = ROOT / 'datos_preparados'
OUT.mkdir(exist_ok=True)
TMP = ROOT / '.analysis_tmp'
TMP.mkdir(exist_ok=True)
con = duckdb.connect()
con.execute("SET memory_limit='1GB'; SET threads=4")
parts = []
audits = []
numeric = ['AELEC', 'EDOCVE', 'MPIOCVE', 'SECCION', 'SEXO', 'EDAD', 'LN', 'SV', 'NV', 'NS']

for year in [2009, 2012, 2015, 2018, 2021, 2024]:
    zpath = ROOT / f'DatosAbiertos_DECEyEC_ConteosCensales{year}.zip'
    with zipfile.ZipFile(zpath) as z:
        for n in sorted(n for n in z.namelist() if n.endswith('.csv')):
            scratch = TMP / 'actual.csv'
            with z.open(n) as src, scratch.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            con.execute('''CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv(?, header=true, delim=',', quote='"', escape='"', all_varchar=true, strict_mode=true)''', [str(scratch)])
            casts = ','.join(f'try_cast({c} AS BIGINT) AS {c}' for c in numeric)
            con.execute(f'CREATE OR REPLACE TABLE t AS SELECT {casts}, EDONOM, MPIONOM, TIPOSEC, DEF, DEL, FELECCION FROM raw')
            invalid = ' OR '.join(f'{c} IS NULL' for c in numeric)
            values = con.execute(f'''SELECT count(*) AS filas,
              count(*) FILTER(WHERE {invalid}) AS numericos_invalidos,
              count(*) FILTER(WHERE AELEC != {year}) AS ano_incorrecto,
              count(*) FILTER(WHERE EDOCVE NOT BETWEEN 1 AND 32 OR MPIOCVE<1 OR SECCION<1 OR EDAD<18 OR SEXO NOT IN (0,1,2)) AS categorias_invalidas,
              count(*) FILTER(WHERE LN<0 OR SV<0 OR NV<0 OR NS<0) AS conteos_negativos,
              count(*) FILTER(WHERE LN != SV+NV+NS) AS identidades_incorrectas,
              count(*) FILTER(WHERE TIPOSEC IS NULL OR TIPOSEC NOT IN ('U','M','R')) AS tiposec_invalido,
              count(*) FILTER(WHERE MPIONOM IS NULL OR EDONOM IS NULL) AS nombres_faltantes,
              count(*) FILTER(WHERE DEF IS NULL) AS def_faltante,
              count(*) FILTER(WHERE DEL IS NULL) AS del_faltante,
              count(*) FILTER(WHERE FELECCION IS NULL) AS fecha_faltante,
              count(*) FILTER(WHERE EDAD>120) AS filas_edad_mayor_120,
              sum(CASE WHEN EDAD>120 THEN LN ELSE 0 END) AS ln_edad_mayor_120,
              count(*) FILTER(WHERE DEF IS NOT NULL AND try_cast(DEF AS BIGINT) IS NULL) AS def_no_numerico,
              count(*) FILTER(WHERE DEL IS NOT NULL AND try_cast(DEL AS BIGINT) IS NULL) AS del_no_numerico,
              count(*) FILTER(WHERE AELEC<2024 AND SEXO=2) AS sexo_no_binario_antes_2024,
              string_agg(distinct FELECCION,';') AS fechas_observadas,
              min(EDAD) AS edad_min,max(EDAD) AS edad_max,
              sum(LN) AS LN,sum(SV) AS SV,sum(NV) AS NV,sum(NS) AS NS FROM t''').fetchone()
            names = [d[0] for d in con.description]
            audit = dict(zip(names, values))
            dup = con.execute('''SELECT count(*),coalesce(sum(n-1),0) FROM
              (SELECT *,count(*) n FROM raw GROUP BY ALL HAVING count(*)>1)''').fetchone()
            keydup = con.execute('''SELECT count(*),coalesce(sum(n-1),0) FROM
              (SELECT count(*) n FROM raw GROUP BY AELEC,EDOCVE,MPIOCVE,SECCION,TIPOSEC,DEF,DEL,SEXO,EDAD HAVING count(*)>1)''').fetchone()
            audit.update(ano=year, archivo=n, duplicados_exactos_extra=dup[1], claves_repetidas_extra=keydup[1])
            audits.append(audit)
            fatal = ['numericos_invalidos','ano_incorrecto','categorias_invalidas','conteos_negativos','identidades_incorrectas','tiposec_invalido','nombres_faltantes','sexo_no_binario_antes_2024']
            if any(audit[k] for k in fatal):
                (ROOT/'auditoria/auditoria_archivos.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2),encoding='utf-8')
                raise ValueError(f'Archivo requiere revisión antes de agregar: {n}: {audit}')
            result = con.execute('''SELECT AELEC ano, lpad(cast(EDOCVE AS VARCHAR),2,'0') entidad_ine,
              lpad(cast(MPIOCVE AS VARCHAR),3,'0') municipio_ine,
              min(EDONOM) entidad_nombre,min(MPIONOM) municipio_nombre,
              count(distinct MPIONOM) variantes_nombre,count(*) filas_origen,
              sum(LN) ln,sum(SV) sv,sum(NV) nv,sum(NS) ns,
              sum(CASE WHEN EDAD BETWEEN 18 AND 29 THEN LN ELSE 0 END) ln_18_29,
              sum(CASE WHEN EDAD>=60 THEN LN ELSE 0 END) ln_60_mas,
              sum(CASE WHEN EDAD>120 THEN LN ELSE 0 END) ln_edad_mayor_120,
              sum(CASE WHEN SEXO=1 THEN LN ELSE 0 END) ln_mujeres,
              sum(CASE WHEN SEXO=2 THEN LN ELSE 0 END) ln_no_binario,
              sum(CASE WHEN TIPOSEC='U' THEN LN ELSE 0 END) ln_urbana,
              sum(CASE WHEN TIPOSEC='R' THEN LN ELSE 0 END) ln_rural,
              sum(CASE WHEN TIPOSEC='M' THEN LN ELSE 0 END) ln_mixta
              FROM t GROUP BY AELEC,EDOCVE,MPIOCVE ORDER BY EDOCVE,MPIOCVE''').fetchall()
            fields = [d[0] for d in con.description]
            parts.extend(dict(zip(fields, row)) for row in result)
            scratch.unlink()
    print(f'{year}: {sum(a["filas"] for a in audits if a["ano"]==year):,} filas auditadas',flush=True)

for row in parts:
    row['clave_municipio_ine'] = row['entidad_ine']+row['municipio_ine']
    denominator = row['sv']+row['nv']
    row['participacion_pct'] = 100*row['sv']/denominator if denominator else None
    row['abstencion_pct'] = 100*row['nv']/denominator if denominator else None
    row['no_especificados_pct'] = 100*row['ns']/row['ln'] if row['ln'] else None
    row['tipo_eleccion'] = 'intermedia' if row['ano'] in [2009,2015,2021] else 'presidencial'
    row['observacion'] = 'sin_datos_observados' if not denominator else ''

def write_csv(path, rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

parts.sort(key=lambda r:(r['ano'],r['entidad_ine'],r['municipio_ine']))
write_csv(OUT/'municipios_historico.csv',parts)
write_csv(ROOT/'auditoria/auditoria_archivos.csv',audits)
(ROOT/'auditoria/auditoria_archivos.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summaries=[]
for year in [2009,2012,2015,2018,2021,2024]:
    source=[a for a in audits if a['ano']==year]
    grouped=[r for r in parts if r['ano']==year]
    for c in ['LN','SV','NV','NS']:
        assert sum(a[c] for a in source)==sum(r[c.lower()] for r in grouped), (year,c)
    summaries.append({'ano':year,'archivos':len(source),'filas':sum(a['filas'] for a in source),
      'municipios':len(grouped),'entidades':len({r['entidad_ine'] for r in grouped}),
      **{c:sum(a[c] for a in source) for c in ['LN','SV','NV','NS']},
      'duplicados_exactos_extra':sum(a['duplicados_exactos_extra'] for a in source),
      'claves_repetidas_extra':sum(a['claves_repetidas_extra'] for a in source)})
write_csv(ROOT/'auditoria/resumen_anual.csv',summaries)
(ROOT/'auditoria/resumen_anual.json').write_text(json.dumps(summaries,indent=2)+'\n',encoding='utf-8')
print(f'Base generada: {len(parts):,} filas municipales. Totales conciliados en los seis años.',flush=True)

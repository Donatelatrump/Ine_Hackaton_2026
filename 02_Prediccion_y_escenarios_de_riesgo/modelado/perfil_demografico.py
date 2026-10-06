"""Capa explicativa de perfil demografico observado (CCPC), separada del modelo.

Calcula abstención observada por grupo de edad, sexo y tipo de sección a nivel
municipal para los procesos 2021 y 2024. No alimenta a Ridge ni a la prioridad:
es una lectura descriptiva posterior. NS permanece fuera del denominador por
grupo (abstención = 100*NV/(SV+NV)).
"""
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACK = ROOT.parent
sys.path.insert(0, str(TRACK.parent / '.task_packages'))
import duckdb

TMP = TRACK / '.analysis_tmp'
TMP.mkdir(exist_ok=True)
OUT = ROOT / 'salidas' / 'perfil_demografico.json'
YEARS = [2021, 2024]

DIMENSIONS = {
    'edad': {'18_29': 'EDAD BETWEEN 18 AND 29', '30_59': 'EDAD BETWEEN 30 AND 59', '60_mas': 'EDAD BETWEEN 60 AND 120'},
    'sexo': {'hombres': 'SEXO=0', 'mujeres': 'SEXO=1', 'no_binario': 'SEXO=2'},
    'seccion': {'urbana': "TIPOSEC='U'", 'mixta': "TIPOSEC='M'", 'rural': "TIPOSEC='R'"},
}

con = duckdb.connect()
con.execute("SET memory_limit='1GB'; SET threads=4")

select_cols = []
for mapping in DIMENSIONS.values():
    for name, cond in mapping.items():
        select_cols.append(f'''sum(CASE WHEN {cond} THEN SV ELSE 0 END) AS "{name}_sv"''')
        select_cols.append(f'''sum(CASE WHEN {cond} THEN NV ELSE 0 END) AS "{name}_nv"''')
select_cols = ','.join(select_cols)


def ratio(sv, nv):
    den = sv + nv
    return None if den <= 0 else round(100 * nv / den, 2)


def add_cell(acc, key, sv, nv):
    cell = acc.setdefault(key, {'sv': 0, 'nv': 0})
    cell['sv'] += sv
    cell['nv'] += nv


municipal = {}
national = {}
for year in YEARS:
    zpath = TRACK / f'DatosAbiertos_DECEyEC_ConteosCensales{year}.zip'
    with zipfile.ZipFile(zpath) as z:
        for name in sorted(n for n in z.namelist() if n.endswith('.csv')):
            scratch = TMP / 'perfil_actual.csv'
            with z.open(name) as src, scratch.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            con.execute('''CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv(?, header=true, delim=',', quote='"', escape='"', all_varchar=true, strict_mode=true)''', [str(scratch)])
            casts = ','.join(f'try_cast({c} AS BIGINT) AS {c}' for c in ['EDOCVE', 'MPIOCVE', 'SEXO', 'EDAD', 'SV', 'NV'])
            con.execute(f'CREATE OR REPLACE TABLE t AS SELECT {casts}, TIPOSEC FROM raw')
            rows = con.execute(f'SELECT EDOCVE, MPIOCVE, {select_cols} FROM t GROUP BY EDOCVE, MPIOCVE').fetchall()
            fields = [d[0] for d in con.description]
            for values in rows:
                rec = dict(zip(fields, values))
                key = f"{int(rec['EDOCVE']):02d}{int(rec['MPIOCVE']):03d}"
                entry = municipal.setdefault(key, {})
                dims = entry.setdefault(str(year), {dim: {} for dim in DIMENSIONS})
                nat = national.setdefault(str(year), {dim: {} for dim in DIMENSIONS})
                for dim, mapping in DIMENSIONS.items():
                    for group in mapping:
                        sv, nv = rec[f'{group}_sv'], rec[f'{group}_nv']
                        add_cell(dims[dim], group, sv, nv)
                        add_cell(nat[dim], group, sv, nv)
            scratch.unlink()

national_out = {}
for year, dims in national.items():
    national_out[year] = {
        dim: {group: {'abstencion_pct': ratio(c['sv'], c['nv']), 'n': c['sv'] + c['nv']} for group, c in groups.items()}
        for dim, groups in dims.items()
    }
municipal_out = {}
for key, years in municipal.items():
    municipal_out[key] = {
        year: {dim: {group: {'abstencion_pct': ratio(c['sv'], c['nv']), 'n': c['sv'] + c['nv']} for group, c in groups.items()}
               for dim, groups in dims.items()}
        for year, dims in years.items()
    }

payload = {
    'definicion': 'Abstención observada CCPC por grupo: 100*NV/(SV+NV) dentro de cada grupo. Capa explicativa posterior; no alimenta a Ridge, a la referencia ni a la prioridad.',
    'nota_ns': 'NS queda fuera del denominador por grupo. Edades mayores de 120 se excluyen de 60_mas. Sexo: 0=hombres, 1=mujeres, 2=no binario (solo 2024). Sección: U=urbana, M=mixta, R=rural.',
    'anios': YEARS,
    'nacional': national_out,
    'municipios': municipal_out,
}
OUT.write_text(json.dumps(payload, ensure_ascii=True, allow_nan=False, separators=(',', ':')), encoding='utf-8')
print(json.dumps({'municipios': len(municipal_out), 'anios': YEARS, 'bytes': OUT.stat().st_size}, ensure_ascii=True))

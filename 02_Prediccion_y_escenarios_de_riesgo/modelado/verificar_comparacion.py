"""Verificación independiente de las métricas y del modelo serializado."""
import csv
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
from threadpoolctl import threadpool_limits
import comparar_modelos as benchmark
from core import metricas

HERE=Path(__file__).resolve().parent
OUT=HERE/'salidas/comparacion_modelos'
report=json.loads((OUT/'resultados.json').read_text(encoding='utf-8'))
assert report['script_sha256']==hashlib.sha256(Path(benchmark.__file__).read_bytes()).hexdigest()
assert report['protocol_sha256']==hashlib.sha256((HERE/'PROTOCOLO_COMPARACION_4_MODELOS.md').read_bytes()).hexdigest()
assert report['source_sha256']==hashlib.sha256(benchmark.SOURCE.read_bytes()).hexdigest()
for filename,digest in report['output_sha256'].items():assert hashlib.sha256((OUT/filename).read_bytes()).hexdigest()==digest
rows=list(csv.DictReader((OUT/'backtest_predicciones.csv').open(encoding='utf-8-sig',newline='')))
for year,cut in report['cuts'].items():
    test=[row for row in rows if row['year']==year]
    assert len(test)==cut['n_test'] and len({r['key'] for r in test})==len(test)
    assert all(int(r['source_year'])<int(year) and int(r['same_type_year'])<int(year) for r in test)
    assert all(y<int(year) for y in cut['train_years'])
    for family,value in cut['models'].items():
        actual=metricas([float(r['observed']) for r in test],[float(r[family]) for r in test],
                       [float(r['weight']) for r in test],[r['key'] for r in test])
        for key in ['n','mae','mae_ponderado','sesgo','precision_top','error_absoluto_p90']:
            assert abs(actual[key]-value[key])<1e-9,(year,family,key)
        if family!='baseline':
            for config in cut['tuning'][family]:
                for fold in config['folds']:
                    assert fold['validation_year']<int(year)
                    assert all(y<fold['validation_year'] for y in fold['train_years'])
assert report['selected_model']==benchmark.choose(report['aggregates'])
future=benchmark.examples(benchmark.load_histories(),2027,observed=False)
saved=list(csv.DictReader((OUT/'proyeccion_2027.csv').open(encoding='utf-8-sig',newline='')))
artifact=joblib.load(OUT/'modelo_seleccionado.joblib')
assert artifact['family']==report['selected_model'] and artifact['feature_names']==report['feature_names']
with threadpool_limits(limits=1):predictions=benchmark.predict(artifact['model'],future)
assert [r['key'] for r in future]==[r['key'] for r in saved]
assert np.allclose(predictions,[float(r[artifact['family']]) for r in saved],atol=1e-9,rtol=1e-9)
assert len(saved)==1783
publication=json.loads((HERE.parent/'demo/data/comparacion_modelos.json').read_text(encoding='utf-8'))
assert publication['report']['script_sha256']==report['script_sha256']
for expected,actual in zip(saved,publication['forecasts']):
    assert expected['key']==actual['key']
    for family in ['baseline',*benchmark.NAMES]:assert abs(float(expected[family])-actual[family])<1e-9
result={'metrics_recomputed':10,'cohort_rows':len(rows),'future_rows':len(saved),
        'temporal_leakage_checks':'pass','serialization_roundtrip':'pass','source_hashes':'pass',
        'selected_model':artifact['family'],'publication_matches':'pass'}
(OUT/'verificacion.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

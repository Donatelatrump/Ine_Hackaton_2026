"""Publica el benchmark solo en demo6, sin reescribir los datos de otras demos."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from threadpoolctl import threadpool_limits
import comparar_modelos as benchmark
from core import make_features,valid_rate

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'demo/data'
OUT=ROOT/'modelado/salidas/comparacion_modelos'


def examples_ns(histories,year,limit,observed):
    rows=[]
    for key,history in sorted(histories.items()):
        feature=make_features(history,year,limit)
        target=next((r for r in history if r['ano']==year),None)
        if not feature or (observed and (not target or not valid_rate(target,limit))):continue
        assert feature['source_year']<year and feature['same_year']<year
        rows.append({'key':key,'feature':feature,'y':target['abstencion_pct'] if target else None,'year':year})
    return rows


def main():
    report=json.loads((OUT/'resultados.json').read_text(encoding='utf-8'))
    assert report['script_sha256']==hashlib.sha256(Path(benchmark.__file__).read_bytes()).hexdigest()
    assert report['source_sha256']==hashlib.sha256(benchmark.SOURCE.read_bytes()).hexdigest()
    forecasts=list(csv.DictReader((OUT/'proyeccion_2027.csv').open(encoding='utf-8-sig',newline='')))
    for row in forecasts:
        for name in ['baseline',*benchmark.NAMES]:row[name]=float(row[name])
    base_data=json.loads((DATA/'resultados.json').read_text(encoding='utf-8'))
    original={r['key']:r for r in base_data['municipios']}
    assert len(forecasts)==1783 and all(row['key'] in original for row in forecasts)
    assert all(abs(row['baseline']-original[row['key']]['baseline'])<1e-9 for row in forecasts)
    histories=benchmark.load_histories()
    sensitivity={r['key']:{family:{} for family in ['baseline',*benchmark.NAMES]} for r in base_data['municipios']}
    for row in forecasts:
        for family in ['baseline',*benchmark.NAMES]:sensitivity[row['key']][family]['10']=row[family]
    # Sensibilidad de calidad: parámetros finales congelados del experimento NS10.
    # Estos ajustes no intervienen en la selección ni en las métricas del benchmark.
    with threadpool_limits(limits=1):
        for limit in (5,20):
            train=[row for year in (2015,2018,2021,2024) for row in examples_ns(histories,year,limit,True)]
            future=examples_ns(histories,2027,limit,False)
            for row in future:sensitivity[row['key']]['baseline'][str(limit)]=row['feature']['baseline']
            for family in benchmark.NAMES:
                model=benchmark.fit(family,report['projection']['parameters'][family],train)
                values=benchmark.predict(model,future)
                for row,value in zip(future,values):sensitivity[row['key']][family][str(limit)]=value
                print('Sensibilidad',limit,family,len(future),flush=True)
    payload={'report':report,'forecasts':forecasts,'sensitivity':sensitivity,
        'sensitivity_definition':'NS 5/10/20. Parámetros finales NS10 congelados; reentrenamiento con la cohorte de calidad correspondiente. Referencia versus método activo; referencia versus Ridge si se consulta baseline.'}
    text=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    (DATA/'comparacion_modelos.json').write_text(text+'\n',encoding='utf-8')
    runtime=""";
(() => {
  const comparison=window.UMBRAL_MODEL_COMPARISON, report=comparison.report;
  const forecasts=new Map(comparison.forecasts.map(r=>[r.key,r]));
  for(const r of window.UMBRAL_DATA.municipios){
    const values=forecasts.get(r.key);
    for(const name of ['ridge','hgb','lightgbm','catboost'])r[name]=values?.[name]??null;
    r.model_variants=comparison.sensitivity[r.key];
    r.risk=r[report.selected_model];
  }
  const metadata=window.UMBRAL_DATA.metadata;
  metadata.previous_experiment={checks:metadata.checks,feature_names:metadata.feature_names,
    selected_model:metadata.selected_model,additional_evaluation:metadata.additional_evaluation};
  metadata.selected_model=report.selected_model;
  metadata.feature_names=report.feature_names;
  metadata.coefficients_standardized=report.ridge_coefficients_standardized;
  metadata.alpha_final=report.projection.parameters.ridge.alpha;
  metadata.checks=Object.fromEntries(Object.entries(report.cuts).map(([year,cut])=>[year,{
    entrenamiento_anos:cut.train_years,n_train:cut.n_train,persistencia:cut.models.baseline,
    ridge:cut.models.ridge,hgb:cut.models.hgb,lightgbm:cut.models.lightgbm,catboost:cut.models.catboost
  }]));
  metadata.comparison_report=report;
  metadata.selection_rule=report.selection_rule;
  metadata.selection_caveat=report.limitation;
  metadata.variant_definition=comparison.sensitivity_definition;
  metadata.historical_error_p90_pp=report.cuts['2021'].models[report.selected_model].error_absoluto_p90;
  metadata.error90_method=report.selected_model;
})();
"""
    (DATA/'comparacion_modelos.js').write_text('window.UMBRAL_MODEL_COMPARISON='+text+runtime,encoding='utf-8')
    (OUT/'publicacion_demo6.json').write_text(json.dumps({
        'selected_model':report['selected_model'],'forecast_count':len(forecasts),
        'benchmark_source_sha256':report['source_sha256'],
        'publisher_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'data_js_sha256':hashlib.sha256((DATA/'comparacion_modelos.js').read_bytes()).hexdigest(),
        'sensitivity_definition':payload['sensitivity_definition']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Demo6: publicado',report['selected_model'],len(forecasts),'proyecciones. Datos anteriores conservados.')


if __name__=='__main__':main()

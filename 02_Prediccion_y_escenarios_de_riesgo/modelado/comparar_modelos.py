"""Benchmark temporal reproducible de cuatro regresores municipales.

Leer PROTOCOLO_COMPARACION_4_MODELOS.md antes de ejecutar.
Usar el entorno aislado .venv_modelos (Python 3.12), sin importar ejecutar.py.
"""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
import csv
import hashlib
import importlib.metadata
import json
import platform
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

import joblib
import numpy as np
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from core import FEATURE_NAMES,make_features,metricas,valid_rate

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE=ROOT/'datos_preparados/municipios_historico_con_calidad.csv'
OUT=HERE/'salidas/comparacion_modelos'
NAMES={'ridge':'Ridge','hgb':'HistGradientBoosting','lightgbm':'LightGBM','catboost':'CatBoost'}
CONFIGS={
    'ridge':[{'alpha':a} for a in (10,100,500,1000)],
    'hgb':[{'max_leaf_nodes':leaf,'max_iter':n} for leaf in (7,15) for n in (100,200)],
    'lightgbm':[{'num_leaves':leaf,'n_estimators':n} for leaf in (7,15) for n in (100,200)],
    'catboost':[{'depth':depth,'iterations':n} for depth in (3,5) for n in (100,200)],
}


def learner(family,parameters):
    if family=='ridge':return make_pipeline(StandardScaler(),Ridge(**parameters))
    if family=='hgb':return HistGradientBoostingRegressor(**parameters,learning_rate=.05,
        l2_regularization=5,min_samples_leaf=40,early_stopping=False,random_state=42)
    if family=='lightgbm':return LGBMRegressor(**parameters,learning_rate=.05,reg_lambda=5,
        min_child_samples=40,random_state=42,n_jobs=1,deterministic=True,force_col_wise=True,verbosity=-1)
    if family=='catboost':return CatBoostRegressor(**parameters,learning_rate=.05,l2_leaf_reg=5,
        loss_function='RMSE',random_seed=42,thread_count=1,allow_writing_files=False,verbose=False)
    raise ValueError(family)


def load_histories():
    numeric=['ano','ln','sv','nv','ns','no_especificados_pct','abstencion_pct','ln_18_29',
             'ln_60_mas','ln_urbana','ln_rural','ln_edad_mayor_120']
    histories=defaultdict(list)
    with SOURCE.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            for column in numeric:row[column]=float(row[column]) if row[column]!='' else None
            row['ano']=int(row['ano'])
            histories[row['clave_municipio_ine']].append(row)
    for rows in histories.values():rows.sort(key=lambda row:row['ano'])
    return histories


def examples(histories,year,observed=True):
    rows=[]
    for key,history in sorted(histories.items()):
        feature=make_features(history,year,10)
        target=next((row for row in history if row['ano']==year),None)
        if not feature or (observed and (not target or not valid_rate(target,10))):continue
        assert feature['source_year']<year and feature['same_year']<year
        assert len(feature['x'])==len(FEATURE_NAMES)==15
        rows.append({'key':key,'year':year,'state':history[-1]['entidad_ine'],
            'feature':feature,'y':target['abstencion_pct'] if target else None,
            'weight':target['sv']+target['nv'] if target else None})
    return rows


def matrix(rows):return np.asarray([row['feature']['x'] for row in rows],dtype=np.float64)
def base(rows):return np.asarray([row['feature']['baseline'] for row in rows])


def fit(family,parameters,rows):
    model=learner(family,parameters)
    model.fit(matrix(rows),np.asarray([row['y'] for row in rows])-base(rows))
    return model


def predict(model,rows):
    # Nombres estables para LightGBM evitan ambigüedad de orden de columnas.
    return np.clip(base(rows)+model.predict(matrix(rows)),0,100).tolist()


def metrics(rows,predictions):
    assert len(rows)==len(predictions) and all(np.isfinite(predictions))
    return metricas([r['y'] for r in rows],predictions,[r['weight'] for r in rows],[r['key'] for r in rows])


def tune(family,by_year,training_years):
    folds=[]
    for index in range(1,len(training_years)):
        validation=training_years[index]
        train=[row for year in training_years[:index] for row in by_year[year]]
        assert all(row['year']<validation for row in train)
        folds.append((train,by_year[validation],validation))
    assert folds
    scores=[]
    for parameters in CONFIGS[family]:
        evaluated=[]
        for train,test,year in folds:
            model=fit(family,parameters,train)
            value=metrics(test,predict(model,test))
            evaluated.append({'validation_year':year,'train_years':sorted({row['year'] for row in train}),**value})
        scores.append({'parameters':parameters,'mean_mae':statistics.mean(v['mae'] for v in evaluated),
                       'mean_weighted_mae':statistics.mean(v['mae_ponderado'] for v in evaluated),'folds':evaluated})
    scores.sort(key=lambda score:(score['mean_mae'],score['mean_weighted_mae']))
    return scores[0]['parameters'],scores


def benchmark_fit(family,parameters,train,test):
    times=[];predictions=None
    for _ in range(3):
        start=time.perf_counter();model=fit(family,parameters,train);times.append(time.perf_counter()-start)
        current=predict(model,test)
        if predictions is not None:assert np.allclose(current,predictions,rtol=1e-8,atol=1e-8)
        predictions=current
    predict(model,test)
    inference=[]
    for _ in range(10):
        start=time.perf_counter();predict(model,test);inference.append(time.perf_counter()-start)
    return model,predictions,{'fit_seconds_median':statistics.median(times),
        'predict_seconds_median':statistics.median(inference),'fit_repeats':3,'predict_repeats':10}


def choose(aggregates):
    best=min(v['mean_mae'] for v in aggregates.values())
    candidates=[k for k,v in aggregates.items() if v['mean_mae']<=best+.05]
    weighted=min(aggregates[k]['mean_weighted_mae'] for k in candidates)
    candidates=[k for k in candidates if aggregates[k]['mean_weighted_mae']<=weighted+.05]
    top=max(aggregates[k]['mean_precision_top50'] for k in candidates)
    candidates=[k for k in candidates if aggregates[k]['mean_precision_top50']>=top-.01]
    return min(candidates,key=lambda k:(aggregates[k]['mean_fit_seconds'],k))


def markdown(report):
    lines=['# Resultados de la comparación de cuatro modelos','',
        'Ejecución real: '+report['timestamp_utc']+'. Python '+report['environment']['python']+'.',
        '','Se reentrenaron los cuatro regresores sobre la misma cohorte y las mismas 15 variables históricas. '
        'Las cifras no son las del experimento anterior con 18 variables declaradas en sus metadatos.','',
        '| Corte | Modelo | Municipios | MAE pp | Ponderado pp | Sesgo pp | Top50 | Entrenar s | Predecir ms |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for year,cut in report['cuts'].items():
        for family,value in cut['models'].items():
            timing=value.get('timing',{})
            fit_time=f"{timing['fit_seconds_median']:.4f}" if timing else 'No aplica'
            prediction_time=f"{timing['predict_seconds_median']*1000:.4f}" if timing else 'No medido'
            lines.append(f"| {year} | {NAMES.get(family,'Referencia homóloga')} | {value['n']} | {value['mae']:.4f} | {value['mae_ponderado']:.4f} | {value['sesgo']:.4f} | {round(value['precision_top']*value['top_k'])}/{value['top_k']} | {fit_time} | {prediction_time} |")
    lines+=['','## Selección','',f"Modelo seleccionado entre los cuatro: **{NAMES[report['selected_model']]}**.",'',
        '| Modelo | MAE medio entre elecciones | MAE ponderado medio | Aciertos top50 medios | Entrenar s medios |',
        '|---|---:|---:|---:|---:|']
    for family,v in sorted(report['aggregates'].items(),key=lambda item:item[1]['mean_mae']):
        lines.append(f"| {NAMES[family]} | {v['mean_mae']:.4f} | {v['mean_weighted_mae']:.4f} | {v['mean_precision_top50']*50:.1f}/50 | {v['mean_fit_seconds']:.4f} |")
    lines+=['',f"Referencia homóloga adicional: MAE medio {report['baseline_mean_mae']:.4f} pp. "+
            ('El modelo seleccionado mejora ese promedio.' if report['improves_baseline_mean'] else 'El modelo seleccionado no mejora ese promedio; conservar la referencia como comparación es necesario.'),'',
        'Se prioriza MAE medio con igual peso para 2021 y 2024. Desempates: tolerancia 0.05 pp, MAE ponderado, precisión top50 (tolerancia 0.01) y tiempo de ajuste. '
        'Las diferencias de tiempo se midieron en esta CPU con un hilo, tres ajustes y diez predicciones por corte.','',
        'La selección utiliza estos dos cortes. No existe una prueba futura independiente después de seleccionar al ganador. '
        '2024 ya fue observado en investigaciones anteriores y no se presenta como una prueba nueva ciega. '
        'La proyección 2027 continúa siendo exploratoria.','',
        'Los rangos de error se identifican como referencias retrospectivas, sin garantías probabilísticas. '
        'No se modifica Voto Vigía. Demo6 conserva predicciones precalculadas.','',
        '## Reproducción','',
        'Desde la raíz: `.venv_modelos/Scripts/python.exe 02_Prediccion_y_escenarios_de_riesgo/modelado/comparar_modelos.py`. '
        'Dependencias exactas: `requirements_comparacion.lock.txt`. Protocolo: `PROTOCOLO_COMPARACION_4_MODELOS.md`.','',
        'Artefactos en `salidas/comparacion_modelos/`: informe JSON, predicciones por municipio y corte, '
        'proyecciones 2027 para los cuatro modelos, modelo seleccionado serializado, búsqueda de parámetros y hashes.']
    return '\n'.join(lines)+'\n'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    histories=load_histories()
    by_year={year:examples(histories,year) for year in (2015,2018,2021,2024)}
    report={'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'protocol':'PROTOCOLO_COMPARACION_4_MODELOS.md','feature_names':FEATURE_NAMES,
        'feature_count':len(FEATURE_NAMES),'seed':42,'threads':1,'configs':CONFIGS,
        'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256((HERE/'PROTOCOLO_COMPARACION_4_MODELOS.md').read_bytes()).hexdigest(),
        'environment':{'python':platform.python_version(),'platform':platform.platform(),
                       'processor':platform.processor(),'versions':{name:importlib.metadata.version(name)
                       for name in ('numpy','scipy','scikit-learn','lightgbm','catboost','joblib','threadpoolctl')}},
        'cuts':{},'aggregates':{},'selection_rule':'MAE medio por año, tolerancia 0.05 pp; MAE ponderado; top50 tolerancia .01; tiempo de ajuste.',
        'limitation':'Selección retrospectiva; no es validación prospectiva de 2027.'}
    predicted_rows=[]
    with threadpool_limits(limits=1):
        for year in (2021,2024):
            train_years=[y for y in by_year if y<year]
            train=[row for y in train_years for row in by_year[y]];test=by_year[year]
            cut={'train_years':train_years,'n_train':len(train),'n_test':len(test),
                 'cohort_sha256':hashlib.sha256('\n'.join(row['key'] for row in test).encode()).hexdigest(),
                 'models':{'baseline':metrics(test,base(test).tolist())},'tuning':{}}
            report['cuts'][str(year)]=cut
            predictions={'baseline':base(test).tolist()}
            for family in NAMES:
                parameters,scores=tune(family,by_year,train_years)
                cut['tuning'][family]=scores
                model,pred,timing=benchmark_fit(family,parameters,train,test)
                predictions[family]=pred
                value={**metrics(test,pred),'parameters':parameters,'timing':timing}
                cut['models'][family]=value
                print(f"{year} {family}: MAE={value['mae']:.4f}, ponderado={value['mae_ponderado']:.4f}, top50={value['precision_top']:.2f}, fit={timing['fit_seconds_median']:.3f}s",flush=True)
            for index,row in enumerate(test):
                predicted_rows.append({'year':year,'key':row['key'],'state':row['state'],'observed':row['y'],
                    'weight':row['weight'],'source_year':row['feature']['source_year'],
                    'same_type_year':row['feature']['same_year'],**{name:values[index] for name,values in predictions.items()}})
            (OUT/'progreso.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        for family in NAMES:
            values=[cut['models'][family] for cut in report['cuts'].values()]
            report['aggregates'][family]={'mean_mae':statistics.mean(v['mae'] for v in values),
                'mean_weighted_mae':statistics.mean(v['mae_ponderado'] for v in values),
                'mean_precision_top50':statistics.mean(v['precision_top'] for v in values),
                'mean_fit_seconds':statistics.mean(v['timing']['fit_seconds_median'] for v in values),
                'mean_predict_seconds':statistics.mean(v['timing']['predict_seconds_median'] for v in values)}
        selected=choose(report['aggregates']);report['selected_model']=selected
        report['baseline_mean_mae']=statistics.mean(cut['models']['baseline']['mae'] for cut in report['cuts'].values())
        report['improves_baseline_mean']=report['aggregates'][selected]['mean_mae']<report['baseline_mean_mae']
        future=examples(histories,2027,observed=False)
        train=[row for rows in by_year.values() for row in rows]
        report['projection']={'n':len(future),'train_years':list(by_year),'parameters':{},'tuning':{},
                             'cohort_sha256':hashlib.sha256('\n'.join(row['key'] for row in future).encode()).hexdigest()}
        final_predictions={}
        for family in NAMES:
            parameters,scores=tune(family,by_year,list(by_year))
            model=fit(family,parameters,train)
            final_predictions[family]=predict(model,future)
            report['projection']['parameters'][family]=parameters
            report['projection']['tuning'][family]=scores
            if family=='ridge':
                report['ridge_coefficients_standardized']=[{'feature':name,'coefficient':float(value)}
                    for name,value in zip(FEATURE_NAMES,model.named_steps['ridge'].coef_)]
            if family==selected:
                joblib.dump({'family':family,'model':model,'feature_names':FEATURE_NAMES,'parameters':parameters,
                    'source_sha256':report['source_sha256'],'prediction':'clip(reference + model.predict(X), 0, 100)'},OUT/'modelo_seleccionado.joblib')
    with (OUT/'backtest_predicciones.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(predicted_rows[0]));writer.writeheader();writer.writerows(predicted_rows)
    future_rows=[{'key':row['key'],'state':row['state'],'baseline':row['feature']['baseline'],
                 **{family:values[index] for family,values in final_predictions.items()}}
                 for index,row in enumerate(future)]
    with (OUT/'proyeccion_2027.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(future_rows[0]));writer.writeheader();writer.writerows(future_rows)
    report['output_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
        (OUT/'backtest_predicciones.csv',OUT/'proyeccion_2027.csv',OUT/'modelo_seleccionado.joblib')}
    (OUT/'resultados.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    (HERE/'COMPARACION_4_MODELOS.md').write_text(markdown(report),encoding='utf-8')
    frozen=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
    (HERE/'requirements_comparacion.lock.txt').write_text(frozen,encoding='utf-8')
    print('SELECCIONADO:',selected,json.dumps(report['aggregates'][selected]),flush=True)


if __name__=='__main__':main()

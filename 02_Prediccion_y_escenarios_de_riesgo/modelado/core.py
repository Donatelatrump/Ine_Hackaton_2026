"""Contratos puros para análisis temporal y escenarios exploratorios."""
import math

FEATURE_NAMES=['abstencion_mismo_tipo','abstencion_ultimo_proceso','diferencia_ultimo_mismo',
 'log_lista_nominal','proporcion_18_29','proporcion_60_mas_sin_extremos','proporcion_urbana',
 'ns_ultimo','ns_mismo_tipo','eleccion_intermedia']

def is_intermedia(year):
    return int(year)%6==5

def valid_rate(row,ns_limit=10):
    rate=row.get('abstencion_pct')
    return rate is not None and math.isfinite(float(rate)) and 0<=float(rate)<=100 and float(row['sv'])+float(row['nv'])>0 and float(row['ln'])>0 and float(row['no_especificados_pct'])<=ns_limit

def make_features(history,target_year,ns_limit=10):
    previous=sorted((r for r in history if int(r['ano'])<target_year),key=lambda r:int(r['ano']))
    same=[r for r in previous if is_intermedia(r['ano'])==is_intermedia(target_year)]
    if not previous or not same:return None
    last,lag=previous[-1],same[-1]
    if not valid_rate(last,ns_limit) or not valid_rate(lag,ns_limit):return None
    latest=float(last['abstencion_pct']);baseline=float(lag['abstencion_pct'])
    denominator=float(last['ln'])
    extremes=float(last.get('ln_edad_mayor_120',0))
    clean_den=denominator-extremes
    if clean_den<=0:return None
    x=[baseline,latest,latest-baseline,math.log1p(denominator),
       float(last['ln_18_29'])/clean_den,
       max(0,float(last['ln_60_mas'])-extremes)/clean_den,
       float(last['ln_urbana'])/denominator,float(last['no_especificados_pct']),
       float(lag['no_especificados_pct']),float(is_intermedia(target_year))]
    if not all(math.isfinite(v) for v in x):return None
    return {'x':x,'baseline':baseline,'source_year':int(last['ano']),'same_year':int(lag['ano'])}

def quantile(values,q):
    if not values:raise ValueError('No hay errores para cuantificar')
    s=sorted(values);pos=(len(s)-1)*q;i=int(pos)
    return s[i]+(s[min(i+1,len(s)-1)]-s[i])*(pos-i)

def metricas(y,pred,weights,keys,k=50):
    if not y or not(len(y)==len(pred)==len(weights)==len(keys)) or sum(weights)<=0:
        raise ValueError('Métricas requieren arrays completos y pesos positivos')
    error=[abs(a-b) for a,b in zip(y,pred)]
    k=min(k,len(y))
    true_top=sorted(range(len(y)),key=lambda i:(-y[i],keys[i]))[:k]
    predicted_top=sorted(range(len(y)),key=lambda i:(-pred[i],keys[i]))[:k]
    return {'n':len(y),'mae':sum(error)/len(y),
      'mae_ponderado':sum(e*w for e,w in zip(error,weights))/sum(weights),
      'precision_top':len(set(true_top)&set(predicted_top))/k if k else 0,
      'top_k':k,'error_absoluto_p90':quantile(error,.9),
      'diferencia_abstencion_top_pp':(sum(y[i] for i in true_top)-sum(y[i] for i in predicted_top))/k if k else 0}

def choose_model(baseline,candidate):
    return 'ridge' if candidate['mae']<=baseline['mae']*.99 and candidate['mae_ponderado']<=baseline['mae_ponderado'] and candidate['precision_top']>=baseline['precision_top'] else 'persistencia'

def missingness_bounds(sv,nv,ns):
    total=sv+nv+ns
    if total<=0:return None,None
    return 100*nv/total,100*(nv+ns)/total

def scenario(items,capacity,reach,response):
    if not all(math.isfinite(float(v)) for v in [capacity,reach,response]) or capacity<0 or int(capacity)!=capacity or reach<0 or not 0<=response<=100:
        raise ValueError('Capacidad, alcance y respuesta fuera de rango')
    valid=[r for r in items if r.get('risk') is not None and math.isfinite(r['risk']) and 0<=r['risk']<=100 and r.get('observed') is not None and math.isfinite(r['observed']) and r['observed']>0]
    selected=[]
    for r in sorted(valid,key=lambda r:(-r['risk'],r['key']))[:int(capacity)]:
        served=min(reach,r['observed']);additional=served*r['risk']/100*response/100
        selected.append({**r,'served':served,'additional':additional,'after':max(0,r['risk']-100*additional/r['observed'])})
    population=sum(r['observed'] for r in selected)
    additional=sum(r['additional'] for r in selected)
    before=sum(r['risk']*r['observed'] for r in selected)/population if population else 0
    return {'selected':selected,'served':sum(r['served'] for r in selected),'additional':additional,
      'reference_population':population,'before':before,'after':max(0,before-100*additional/population) if population else 0}

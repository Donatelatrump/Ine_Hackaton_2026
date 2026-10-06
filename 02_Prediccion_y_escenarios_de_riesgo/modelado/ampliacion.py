"""Funciones del análisis posterior; no cambian el experimento original."""
import math
from core import is_intermedia

def ranks(values):
    order=sorted(range(len(values)),key=values.__getitem__);result=[0.0]*len(values);i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:j+=1
        for k in order[i:j]:result[k]=(i+j-1)/2+1
        i=j
    return result

def spearman(y,pred):
    if len(y)!=len(pred) or len(y)<2:raise ValueError('Rangos requieren pares completos')
    a,b=ranks(y),ranks(pred);ma=sum(a)/len(a);mb=sum(b)/len(b)
    cov=sum((x-ma)*(z-mb) for x,z in zip(a,b));den=math.sqrt(sum((x-ma)**2 for x in a)*sum((z-mb)**2 for z in b))
    return cov/den if den else None

def classification_metrics(y,pred,threshold):
    true={i for i,v in enumerate(y) if v>=threshold};red={i for i,v in enumerate(pred) if v>=threshold};tp=len(true&red)
    return {'umbral_alto_entrenamiento':threshold,'rojos_observados':len(true),'rojos_predichos':len(red),
      'verdaderos_positivos':tp,'precision_rojo':tp/len(red) if red else None,
      'recobrado_rojo':tp/len(true) if true else None,'spearman':spearman(y,pred)}

def size_bin(observed):
    return 'menos_10000' if observed<10000 else '10000_99999' if observed<100000 else '100000_mas'

def exclusion_reasons(history,target,limit):
    previous=sorted((r for r in history if r['ano']<target),key=lambda r:r['ano'])
    same=[r for r in previous if is_intermedia(r['ano'])==is_intermedia(target)]
    if not previous:return ['Sin antecedentes anteriores al objetivo']
    reasons=[]
    if not same:reasons.append('Sin antecedente del mismo tipo electoral')
    for label,r in [('Último proceso',previous[-1])]+([('Último del mismo tipo',same[-1])] if same else []):
        if r['sv']+r['nv']<=0 or r['abstencion_pct'] is None:reasons.append(f'{label} {r["ano"]}: sin participación observable')
        elif r['no_especificados_pct']>limit:reasons.append(f'{label} {r["ano"]}: NS {r["no_especificados_pct"]:.2f}% supera {limit}%')
    return reasons

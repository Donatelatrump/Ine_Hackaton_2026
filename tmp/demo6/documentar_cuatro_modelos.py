"""Actualiza documentación y generadores desde el benchmark realmente ejecutado."""
import ast
import json
import pprint
from pathlib import Path

ROOT=Path('02_Prediccion_y_escenarios_de_riesgo')
R=json.loads((ROOT/'modelado/salidas/comparacion_modelos/resultados.json').read_text(encoding='utf-8'))
C=json.loads((ROOT/'entrega/caso_municipal.json').read_text(encoding='utf-8'))
NAMES={'ridge':'Ridge','hgb':'HistGradientBoosting','lightgbm':'LightGBM','catboost':'CatBoost'}
winner=NAMES[R['selected_model']]
agg=R['aggregates'];best=agg[R['selected_model']]
improvement=100*(agg['ridge']['mean_mae']-best['mean_mae'])/agg['ridge']['mean_mae']
summary=(f'Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. '
         f'Se seleccionó {winner}: MAE medio {best["mean_mae"]:.4f} pp frente a {agg["ridge"]["mean_mae"]:.4f} de Ridge '
         f'({improvement:.2f}% menos error). LightGBM obtuvo MAE {agg["lightgbm"]["mean_mae"]:.4f} pp; la diferencia menor que 0.05 pp '
         f'activó el desempate por MAE ponderado, favorable a {winner}. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.')
table='| Modelo | MAE medio (pp) | MAE ponderado medio (pp) | Aciertos top50 medios | Ajuste medio (s) |\n|---|---:|---:|---:|---:|\n'
for family,v in sorted(agg.items(),key=lambda item:item[1]['mean_mae']):
    table+=f'| {NAMES[family]} | {v["mean_mae"]:.4f} | {v["mean_weighted_mae"]:.4f} | {v["mean_precision_top50"]*50:.1f}/50 | {v["mean_fit_seconds"]:.4f} |\n'
doc=f'''# Metodología vigente: comparación de cuatro modelos

16 de octubre de 2026. Esta etapa sí incluye una nueva ejecución real de entrenamiento y evaluación. Los resultados anteriores se conservan en sus artefactos y no se atribuyen a esta ejecución.

{summary}

## Datos, variables y cortes

CCPC INE de 2009 a 2024. Objetivo: abstención observable municipal = 100 × NV / (SV+NV). Cohorte con NS≤10% en ambos antecedentes y, para evaluar, también en el objetivo. Las 15 variables de core.make_features son idénticas para todos los modelos y se construyen solo con años anteriores al objetivo. No se añaden identificadores categóricos a un solo competidor ni proyecciones CONAPO exclusivas de 2027.

Todos estiman el residual respecto a la última elección del mismo tipo; la salida suma referencia más residual y se acota a [0,100]. La referencia homóloga se conserva como control adicional. Para 2027 la referencia es 2021.

| Corte externo | Etiquetas de entrenamiento | Validaciones internas | Municipios evaluados |
|---|---|---|---:|
| 2021 | 2015, 2018 | 2018, entrenando solo con 2015 | 1,490 |
| 2024 | 2015, 2018, 2021 | 2018 y 2021, cada una con años anteriores | 1,476 |
| Proyección 2027 | 2015, 2018, 2021, 2024 | 2018, 2021 y 2024 | 1,783 proyecciones |

Cuatro configuraciones por familia, semilla 42, un hilo de CPU y ninguna parada temprana con el corte externo. La estandarización de Ridge se ajusta solo con entrenamiento. Parámetros completos y búsquedas internas en salidas/comparacion_modelos/resultados.json.

## Regla de selección fijada antes de ejecutar

Menor MAE medio dando igual peso a 2021 y 2024. Dentro de 0.05 pp del mínimo, menor MAE ponderado; si este difiere ≤0.05 pp, mayor precisión top50; dentro de 0.01 de precisión, menor tiempo de ajuste. No se mezcla tiempo y error en una puntuación arbitraria.

Esta regla sustituye en el nuevo experimento la comparación defectuosa del cambio de sesgo con signo. No se reescriben core.choose_model ni los resultados de las demos anteriores. El sesgo con signo se informa para cada modelo sin rechazar mejoras de sesgo absoluto por un cambio de signo.

## Resultados

{table}

La referencia obtiene MAE medio {R['baseline_mean_mae']:.4f} pp. En 2024 logra 27/50 aciertos top50 frente a 19/50 de HistGradientBoosting: menor MAE no implica mejor ranking en todos los casos. LightGBM recupera más municipios top50 en promedio que el ganador, pero el protocolo prioriza MAE y su desempate ponderado.

## Velocidad

Mediana de tres ajustes por corte, excluyendo carga y búsqueda. Mediana de diez predicciones tras calentamiento, sobre la cohorte completa. El informe registra CPU, plataforma y versiones. Ridge conserva el menor tiempo de entrenamiento; no se afirma que el ganador sea más rápido. Demo6 sigue leyendo proyecciones precalculadas, sin ejecutar modelos en cada clic.

## Proyección y sensibilidad

Demo6 carga data/comparacion_modelos.js después de los datos originales. El complemento incorpora los cuatro métodos y selecciona HistGradientBoosting. No reemplaza datos_embebidos.js ni las demos previas. Se guardan también el modelo seleccionado serializado, predicciones por municipio y corte y sus hashes.

La sensibilidad NS5/10/20 usa los parámetros finales NS10 congelados y reentrena con la cohorte correspondiente. La frecuencia compara referencia y método activo; cuando se consulta referencia, el comparador es Ridge. Los nombres internos ridge_* de decision.js son compatibilidad de implementación, no atribución del método activo a Ridge. No se usan estas sensibilidades para decidir el ganador.

## Incertidumbre y límites

El rango ilustrativo de la ficha usa el P90 del error absoluto de 2021 de cada método. Para el ganador: ±{R['cuts']['2021']['models'][R['selected_model']]['error_absoluto_p90']:.2f} pp, acotado a [0,100]. Es error retrospectivo, no un intervalo prospectivo calibrado.

Los dos cortes participan en la selección final. 2024 ya fue examinado en etapas previas: no se presenta como una nueva prueba ciega de todo el proceso de investigación. Falta una elección futura independiente después de seleccionar. Hay pocos ciclos electorales, cohortes condicionadas por calidad y límites históricos sin armonizar. No se garantizan resultados de 2027 ni se infieren comportamientos individuales.

## Reproducción

1. Crear un entorno Python 3.12 e instalar modelado/requirements_comparacion.lock.txt.
2. Ejecutar modelado/comparar_modelos.py con ese entorno.
3. Ejecutar modelado/publicar_comparacion_demo6.py para generar el complemento local y la sensibilidad.
4. Ejecutar modelado/verificar_comparacion.py y demo/verificar_demo6.py.

[Protocolo previo](PROTOCOLO_COMPARACION_4_MODELOS.md), [resultados completos](COMPARACION_4_MODELOS.md), salidas/comparacion_modelos/resultados.json y verificacion.json. No se modifica Voto Vigía.
'''
(ROOT/'modelado/METODOLOGIA.md').write_text(doc,encoding='utf-8')
(ROOT/'modelado/RESULTADOS.md').write_text('# Resultados vigentes de Umbral\n\n'+summary+'\n\n'+table+'\n[Comparación completa y tiempos por corte](COMPARACION_4_MODELOS.md). [Protocolo](PROTOCOLO_COMPARACION_4_MODELOS.md). [Metodología](METODOLOGIA.md).\n\nLa referencia de 2021 sigue disponible. Los resultados anteriores se conservan en los artefactos originales y no se mezclan con este benchmark de 15 variables. En 2024 la referencia recupera más municipios del top50 que el modelo seleccionado.\n',encoding='utf-8')

def prepend(path,text):
    s=path.read_text(encoding='utf-8')
    if not s.startswith(text):path.write_text(text+'\n\n---\n\n'+s,encoding='utf-8')
notice='## Comparación de cuatro modelos ejecutada · 16 de octubre de 2026\n\n'+summary+'\n\nLa versión vigente de demo6 incluye los cuatro métodos y usa HistGradientBoosting por defecto. La documentación anterior que sigue corresponde a la etapa previa al benchmark. Fuente actual: modelado/COMPARACION_4_MODELOS.md del track.'
for p in [ROOT/'README.md',ROOT/'demo/README.md',ROOT/'CORRECCIONES_Y_ESTADO.md',ROOT/'entrega/README.md',Path('README.md'),Path('EXPLICACION_DEL_PROYECTO.md'),Path('ANALISIS_GENERAL_DEL_PROYECTO.md')]:
    if p.exists():prepend(p,notice)

p=ROOT/'demo/DEMO6.md';s=p.read_text(encoding='utf-8')
a=s.index('## Métodos y evidencia');b=s.index('## Denominadores y semáforo',a)
s=s[:a]+f'''## Métodos y evidencia

{summary}

El selector ofrece HistGradientBoosting, LightGBM, CatBoost, Ridge y referencia de 2021. Los cuatro regresores fueron reentrenados sobre las mismas 15 variables y cohortes. La consulta histórica permanece observada e independiente del método. La tabla muestra ambos cortes, error, aciertos y tiempos de CPU.

[Protocolo](../modelado/PROTOCOLO_COMPARACION_4_MODELOS.md), [resultados completos](../modelado/COMPARACION_4_MODELOS.md) y [metodología](../modelado/METODOLOGIA.md). El rango de la ficha usa el error P90 retrospectivo de 2021 del método activo; no es un intervalo prospectivo.

Los factores Ridge son coeficientes del Ridge reentrenado en el benchmark y no explican las predicciones de los otros modelos. La estabilidad compara referencia y método activo en NS5/10/20, con parámetros congelados. Al elegir referencia se compara con Ridge. No es probabilidad de acierto.

'''+s[b:]
s=s.replace('Esta publicación no modifica el proyecto Voto Vigía.','El complemento data/comparacion_modelos.js conserva los datos de las demos anteriores. Esta publicación no modifica el proyecto Voto Vigía.')
p.write_text(s,encoding='utf-8')

case=C['scenario'];mun=C['municipality'];position=C['position_model']
case_text=f'''# Caso municipal vigente: SOLIDARIDAD, clave histórica 23008

16 de octubre de 2026. Modelo seleccionado: {winner}. Nombre y límites del catálogo histórico, sin certificar denominación o fronteras actuales.

Abrir demo/demo6.html, Quintana Roo, clave 23008, año 2027, HistGradientBoosting y catálogo constante. Elegir SMS Suecia, cobertura total de 1,000 personas. Los puestos nacionales usan la cohorte de catálogo constante; no son el ranking local de un único municipio.

| Indicador | Valor |
|---|---:|
| Puesto del modelo seleccionado | {position} |
| Puesto Ridge (benchmark) | {C['position_ridge']} |
| Puesto de referencia | {C['position_reference']} |
| Proyección del modelo seleccionado | {case['before']:.6f}% |
| Referencia 2021 | {mun['baseline']:.6f}% |
| Base SV+NV 2024 | {mun['observed_2024']:,.0f} |
| Frecuencia nacional top50 | {C['stability']['count']}/6 |
| Cobertura total SMS | 1,000 personas asignadas |
| Votos adicionales hipotéticos | 3 |
| Rango externo trasladado | 1.3–4.8 |
| Proyección posterior | {case['after']:.6f}% |
| Reducción municipal | {case['reduction_pp']:.6f} pp |

H = 1,000 × 0.30 / 100 = 3. Posterior = antes - 100 × H / 255,362. El efecto ITT cuenta asignación a SMS, no lectores efectivos. Fuente: Lindgren, Nyman y Oskarsson (2025), DOI 10.1017/S0007123424000504. El traslado a México es hipotético, no validado. El rango externo no incluye incertidumbre del predictor ni de transferencia.

Los puestos y la frecuencia son del ranking nacional top50 con catálogo constante. Las sensibilidades comparan referencia y método activo con parámetros congelados en NS5/10/20. La cobertura no es capacidad institucional confirmada. Validar población, canal, atribuciones, capacidad y protocolo antes de un piloto.

Reproducción: entrega/generar_caso.cjs, que lee demo/data/comparacion_modelos.json. El JSON del caso y esta documentación sustituyen la etapa anterior que usaba Ridge explícito.
'''
(ROOT/'entrega/CASO_MUNICIPAL.md').write_text(case_text,encoding='utf-8')
p=ROOT/'entrega/GUION_PRESENTACION.md';s=p.read_text(encoding='utf-8')
s=s.replace('la referencia de 2021. El resumen','HistGradientBoosting, modelo seleccionado. El resumen')
a=s.index('## 2. Proyección y evaluación');b=s.index('## 3. Acción bajo supuestos',a)
s=s[:a]+'## 2. Proyección y evaluación\n\n'+summary+'\n\nMostrar la tabla de los cuatro modelos y los tiempos. La referencia homóloga sigue disponible. No afirmar superioridad en todos los indicadores: en 2024 la referencia tiene más aciertos top50. Los factores Ridge no explican las predicciones de los otros modelos. El clic derecho vuelve al estado y después a México.\n\n'+s[b:]
s=s.replace('Ridge explícito y catálogo constante. Base 62.071193%','HistGradientBoosting y catálogo constante. Base '+f'{case["before"]:.6f}%')
s=s.replace('posterior 62.070018%',f'posterior {case["after"]:.6f}%')
s=s.replace('Los puestos del caso son Ridge 5 y referencia 3',f'El puesto del modelo seleccionado es {position}, Ridge {C["position_ridge"]} y referencia {C["position_reference"]}')
p.write_text(s,encoding='utf-8')

def literal(source,name,value):
    node=next(n for n in ast.parse(source).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
    lines=source.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'+''.join(lines[node.end_lineno:])

p=ROOT/'entrega/reporte/generar_reporte.py';s=p.read_text(encoding='utf-8')
if 'BENCHMARK=' not in s:
    mark="M=json.loads((ROOT/'modelado/salidas/metricas.json').read_text(encoding='utf-8'))"
    s=s.replace(mark,mark+"\nBENCHMARK=json.loads((ROOT/'modelado/salidas/comparacion_modelos/resultados.json').read_text(encoding='utf-8'))\nM['checks']={year:{**cut['models'],'persistencia':cut['models']['baseline']} for year,cut in BENCHMARK['cuts'].items()}\n")
pages=ast.literal_eval(next(n.value for n in ast.parse(s).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAGES' for t in n.targets)))
updates={
 'Resumen ejecutivo':summary+' Demo6 muestra la consulta histórica y proyecciones precalculadas, comparación estatal, exportación de consultas y escenarios hipotéticos con cobertura total y fuentes.',
 'Ajuste Ridge':'Se comparan cuatro regresores del residual respecto a la misma referencia: Ridge, HistGradientBoosting, LightGBM y CatBoost. Todos usan las mismas 15 variables históricas y cohortes. Cuatro configuraciones por familia, semilla 42 y un hilo de CPU. No se añaden variables futuras ni categóricas a un único competidor.',
 'Cortes temporales':'Evaluación 2021: entrenamiento 2015/2018 y validación interna 2018 con entrenamiento 2015. Evaluación 2024: entrenamiento 2015/2018/2021 y validaciones internas 2018/2021 con años anteriores. Para 2027 se entrena hasta 2024. No se ajusta ni detiene el aprendizaje con el corte externo.',
 'Regla de selección':'Menor MAE medio, igual peso para 2021 y 2024. Diferencias ≤0.05 pp se desempatan por MAE ponderado; después top50 y tiempo. HistGradientBoosting y LightGBM empatan dentro de la tolerancia; gana el primero por su menor MAE ponderado. La regla previa de sesgo con signo no se usa en este experimento.',
 '2021 es selección, no prueba':'Los dos backtests participan en la selección final. 2024 ya fue examinado en etapas anteriores del proyecto. No hay una elección futura independiente después de elegir al ganador; la proyección 2027 sigue siendo exploratoria.',
 'Lectura honesta':summary,
 'Métricas posteriores congeladas':'Se publican MAE, error ponderado, sesgo con signo, P90 y aciertos top50 para cada método y corte. En 2024 la referencia recupera 27/50 frente a 19/50 de HistGradientBoosting: mejorar error no garantiza mejor priorización. Fuente: modelado/salidas/comparacion_modelos/resultados.json.',
 'Incertidumbre de prioridad, no de intervalo':f'Cada método muestra su P90 retrospectivo de 2021. Para {winner}, ±{R["cuts"]["2021"]["models"][R["selected_model"]]["error_absoluto_p90"]:.2f} pp, acotado a [0,100]. No es intervalo prospectivo calibrado. La estabilidad compara referencia y método activo en NS5/10/20 con parámetros finales congelados; no interviene en la selección del ganador.',
 'Caso 23008: SOLIDARIDAD (catálogo histórico)':f'{winner}, catálogo constante: puesto {position}; referencia {C["position_reference"]}. Proyección {case["before"]:.6f}%. Frecuencia nacional top50 {C["stability"]["count"]}/6. SMS Suecia a 1,000 personas asignadas: 3 votos hipotéticos [1.3,4.8], posterior {case["after"]:.6f}%, reducción {case["reduction_pp"]:.6f} pp. Base 255,362. La transferencia del efecto a México requiere evaluación. Fuente: entrega/caso_municipal.json.',
 'Reproducibilidad y cierre':'Abrir demo/demo6.html. Se ejecutaron comparar_modelos.py, publicar_comparacion_demo6.py y verificar_comparacion.py en Python 3.12 con dependencias fijadas. Se conservan predicciones por fila, modelo serializado y hashes. La interacción usa proyecciones precalculadas. Fuentes: protocolo y comparación de cuatro modelos en modelado/. Voto Vigía no se modifica.',
 'Estabilidad del top N':'Seis variantes: referencia y método activo, con calidad NS5/10/20. Al consultar referencia, el comparador es Ridge. Se fijan los parámetros elegidos en NS10 y se reentrena sobre cada cohorte. La frecuencia describe el ranking topN; no es probabilidad ni se utiliza para elegir al ganador.',
 'Límite territorial':'Se conservan 2,477 claves, con proyección NS10 para 1,783. La cartografía incorpora 308 componentes insulares oficiales. Los límites históricos no están armonizados y la coincidencia de claves no prueba continuidad territorial.'
}
pages=[(label,title,[(h,updates.get(h,body)) for h,body in sections]) for label,title,sections in pages]
s=literal(s,'PAGES',pages)
variables=ast.literal_eval(next(n.value for n in ast.parse(s).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='VARIABLES' for t in n.targets)))
s=literal(s,'VARIABLES',[row for row in variables if row[0]!='Demografía proyectada'])
s=s.replace("for name in ['persistencia','ridge']:","for name in ['persistencia','ridge','hgb','lightgbm','catboost']:")
s=s.replace("('Referencia' if name=='persistencia' else 'Ridge')","{'persistencia':'Referencia','ridge':'Ridge','hgb':'HistGradientBoosting','lightgbm':'LightGBM','catboost':'CatBoost'}[name]")
s=s.replace("Fuente: modelado/salidas/metricas.json.","Fuente: modelado/salidas/comparacion_modelos/resultados.json.")
p.write_text(s,encoding='utf-8')

p=ROOT/'entrega/presentacion/generar_presentacion.py';s=p.read_text(encoding='utf-8')
if 'BENCHMARK=' not in s:
    mark="M=json.loads((HERE.parents[1]/'demo/data/resultados.json').read_text(encoding='utf-8'))"
    s=s.replace(mark,mark+"\nBENCHMARK=json.loads((HERE.parents[1]/'modelado/salidas/comparacion_modelos/resultados.json').read_text(encoding='utf-8'))")
slides=ast.literal_eval(next(n.value for n in ast.parse(s).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='slides' for t in n.targets)))
slides[3]=('Cuatro modelos, una comparación temporal', [('Misma cohorte y 15 variables históricas',25),('Ridge, HistGradientBoosting, LightGBM y CatBoost aprenden el residual respecto a la referencia homóloga.',21),('Los parámetros se eligen con años anteriores al corte evaluado. Sin parada temprana sobre 2021 o 2024.',21),('Protocolo previo, cuatro configuraciones por familia, semilla 42 y un hilo de CPU.',21)],'Fuente: modelado/PROTOCOLO_COMPARACION_4_MODELOS.md y salidas/comparacion_modelos/resultados.json.')
slides[4]=('HistGradientBoosting seleccionado',[],f'Media de 2021/2024 con igual peso por elección. Referencia adicional: MAE {R["baseline_mean_mae"]:.2f} pp. No valida 2027.')
slides[7]=(slides[7][0],[('SOLIDARIDAD · catálogo histórico de Quintana Roo',24),(f'{winner}, puesto {position}; referencia {C["position_reference"]}. Base {case["before"]:.6f}%. Frecuencia nacional top50 {C["stability"]["count"]}/6.',21),('1,000 personas asignadas a SMS Suecia: 3 votos adicionales hipotéticos; rango externo 1.3–4.8.',22),(f'Posterior {case["after"]:.6f}%. Reducción {case["reduction_pp"]:.6f} pp. Traslado a México sujeto a evaluación.',21)],'Fuente: entrega/caso_municipal.json. Modelo seleccionado del benchmark. SV+NV 2024: 255,362. DOI 10.1017/S0007123424000504.')
s=literal(s,'slides',slides)
a=s.index("        data=[['Corte / método'");b=s.index("        old=ET.fromstring",a)
s=s[:a]+'''        data=[['Modelo','MAE medio','Ponderado','Top50 medio','Ajustar ms']]
        labels={'ridge':'Ridge','hgb':'HistGradientBoosting','lightgbm':'LightGBM','catboost':'CatBoost'}
        for family in ['hgb','lightgbm','catboost','ridge']:
            v=BENCHMARK['aggregates'][family]
            data.append([labels[family],f"{v['mean_mae']:.2f}",f"{v['mean_weighted_mae']:.2f}",f"{v['mean_precision_top50']*50:.1f}/50",f"{v['mean_fit_seconds']*1000:.1f}"])
'''+s[b:]
s=s.replace('La evidencia no demuestra superioridad consistente.',f'MAE medio {improvement:.1f}% menor que Ridge.')
s=s.replace('Cifras de los artefactos actuales. 2021 participa en selección; 2024 no valida la intermedia de 2027.','Empate de MAE con tolerancia 0.05 pp; gana por error ponderado. Ridge es el más rápido. Selección retrospectiva.')
p.write_text(s,encoding='utf-8')
print('Documentos y generadores actualizados para los cuatro modelos; ganador:',winner)

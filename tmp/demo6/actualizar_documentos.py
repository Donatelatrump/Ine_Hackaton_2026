import ast
import json
from pathlib import Path

ROOT=Path('02_Prediccion_y_escenarios_de_riesgo')
M=json.loads((ROOT/'demo/data/resultados.json').read_text(encoding='utf-8'))['metadata']
C=json.loads((ROOT/'entrega/caso_municipal.json').read_text(encoding='utf-8'))
DATE='16 de octubre de 2026'
rows=[]
for year,check in M['checks'].items():
    for key in ['persistencia','ridge']:
        v=check[key]
        rows.append([year,'Referencia' if key=='persistencia' else 'Ridge',f"{v['n']:,}",f"{v['mae']:.2f}",f"{v['mae_ponderado']:.2f}",f"{round(v['precision_top']*v['top_k'])}/{v['top_k']}"])
table='| Corte | Método | Municipios | MAE (pp) | MAE ponderado (pp) | Aciertos top 50 |\n|---|---|---:|---:|---:|---:|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in rows)
summary='Ridge mejora el error medio en 2021 (8.90 frente a 12.12 pp) y empeora en 2024 (8.96 frente a 5.64 pp). La referencia recupera 27 de los 50 municipios prioritarios en 2024 y Ridge 21. No hay evidencia de superioridad consistente.'
rule='El artefacto actual identifica persistencia como método seleccionado y alpha final 500 para el ajuste Ridge. Demo6 inicia con la referencia de 2021 y permite comparar Ridge. La condición de sesgo implementada compara el cambio con signo: (sesgo candidato - sesgo referencia) >= -3 pp. Con 3.72 - 7.87 = -4.14 pp en 2021, rechaza Ridge aunque disminuya el sesgo absoluto. Esta selección describe el código vigente; no demuestra que la referencia sea universalmente superior. Corregir esa regla y regenerar modelos requiere un experimento separado, sin alterar retrospectivamente esta evaluación.'
method=f'''# Metodología vigente de Umbral y demo6

Actualización: {DATE}. Esta versión documenta los artefactos locales existentes; la actualización de demo6 no reentrena el modelo.

## Datos y objetivo

CCPC del INE 2009, 2012, 2015, 2018, 2021 y 2024. Unidad: municipio, 2,477 claves históricas. Abstención observable = 100 × NV / (SV + NV). NS% = 100 × NS / LN. La proyección 2027 utiliza SV+NV 2024 como base operativa, sin proyectar el electorado.

La referencia repite la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Ridge estima un ajuste respecto a la referencia con variables agregadas y estandarización. El artefacto exporta {len(M['feature_names'])} nombres de variables, incluidas interacciones y variables demográficas de proyección. Esa lista no prueba por sí misma disponibilidad de todas las variables en cada corte; hay que conservar la distinción entre variables históricas y de proyección.

## Parámetros, selección y cortes

{rule}

Los metadatos registran entrenamiento con etiquetas 2015/2018 para 2021 y 2015/2018/2021 para 2024. Para 2027 incorporan etiquetas hasta 2024. Registran selección de alpha y mezcla mediante validación temporal sobre 2021 antes de observar la comprobación 2024. 2021 participa en la selección y no constituye una prueba independiente posterior. El módulo `entrenamiento.py` contiene alternativas adicionales; su presencia no significa que los artefactos actuales hayan sido regenerados con todas ellas.

## Resultados cargados por la demo

{table}

{summary}

## Calidad e incertidumbre

NS máximo de 10% en ambos antecedentes requeridos; 1,783 municipios estimables y 694 sin estimación. La evaluación exige también objetivo observable y NS dentro del límite. La cobertura condiciona los resultados y no representa territorios excluidos.

En demo6 el rango ilustrativo depende del método mostrado: ±{M['checks']['2021']['persistencia']['error_absoluto_p90']:.2f} pp para referencia y ±{M['checks']['2021']['ridge']['error_absoluto_p90']:.2f} pp para Ridge, a partir del P90 del error absoluto retrospectivo de 2021 y acotado a [0,100]. No es un intervalo prospectivo calibrado. El rango predeterminado del artefacto corresponde a `{M['error90_method']}`. La frecuencia entre seis variantes de método y calidad describe estabilidad de selección, no probabilidad de acierto.

## Agregación y cartografía en demo6

Mapa, resumen, brecha estatal y gráfica usan la misma media ponderada. Para históricos se reconstruye SV+NV = LN × (1 - NS%/100) porque el paquete de consulta exporta LN y NS%. Para proyecciones y escenarios se utiliza `observed` (SV+NV 2024). Sin dato no equivale a cero; se excluye del numerador y del denominador de la tasa y se informa cobertura. El semáforo usa tercios nacionales por año y método y conserva los umbrales al comparar escenarios.

La base CONABIO/INEGI AGEM 2024 conserva los límites continentales. `data/islas.js` agrega 308 componentes insulares a 34 municipios desde servicios INEGI 2025. Son una referencia visual; el cruce de nombres y claves no armoniza fronteras históricas. Fuentes y hashes: `data/cartografia_metadatos.json` e `islas_metadatos.json`. No se usan puntos geográficos inventados.

## Simulación

La cobertura es un total territorial, limitada por la base observable. Con efecto externo: H = mínimo(cobertura × efecto_pp/100, cobertura × tasa/100). Con respuesta personalizada: H = cobertura × tasa/100 × respuesta/100. Después = antes - 100 × H / (SV+NV 2024). Las funciones y citas están en `demo/decision.js`. SMS y llamada trasladan evidencia extranjera de forma hipotética; las acciones digital e institucional del catálogo son supuestos y deben identificarse como tales. No se suman acciones ni se convierten probabilidades de clase en votos.

Los presets de demo6 preparan 1,000 personas asignadas a SMS o 1,000 conversaciones completadas. Son ejemplos editables, no capacidades institucionales ni presupuestos confirmados.

## Reproducción y alcance de esta actualización

Abrir `demo/demo6.html` con la carpeta completa. `node entrega/generar_caso.cjs` regenera el caso con Ridge explícito; `python demo/verificar_demo6.py` comprueba el flujo de demo6. Las tablas documentales se extraen de `demo/data/resultados.json` y se contrastan con `datos_embebidos.js`.

Esta actualización revisa presentación, consultas y documentación. No certifica una nueva ejecución del pipeline, no incorpora CatBoost y no modifica Voto Vigía. Los comandos históricos de entrenamiento siguen disponibles en el código; antes de regenerar se debe revisar la regla de sesgo descrita arriba y mantener una prueba temporal independiente.
'''
(ROOT/'modelado/METODOLOGIA.md').write_text(method,encoding='utf-8')
(ROOT/'modelado/RESULTADOS.md').write_text(f'''# Resultados vigentes de Umbral

{DATE}. Fuente: artefactos locales de `demo/data/resultados.json`, `datos_embebidos.js` y `modelado/salidas/metricas.json`. La publicación de demo6 no constituye una nueva ejecución del entrenamiento.

{table}

{summary}

## Selección y parámetros

{rule}

## Cobertura y límites

2,477 municipios; 1,783 con estimación y 694 sin estimación. Evaluación sobre cohortes condicionadas por calidad: 1,490 municipios en 2021 y 1,476 en 2024. Los municipios excluidos no tienen tasa cero. 2024 es presidencial y no valida directamente la intermedia de 2027.

La incertidumbre histórica se identifica por método en [METODOLOGIA.md](METODOLOGIA.md). No se comunica como probabilidad calibrada de acierto o de participación individual. Los escenarios siguen siendo hipótesis de transferencia y cobertura.

## Demo6

Resumen territorial ponderado, historial con proyección diferenciada, comparación estatal, evaluación visible, coeficientes Ridge, consulta CSV completa y presets editables. [Guía de uso](../demo/DEMO6.md).

Esta versión sustituye las cifras anteriores 9.21/8.58 pp para Ridge y alpha 10 en la documentación activa. Se conserva el historial de versiones en Git; no se adjudican estas cifras actualizadas a los reportes de experimentos anteriores.
''',encoding='utf-8')

def prepend(path,text):
    old=path.read_text(encoding='utf-8')
    if old.startswith(text):return
    path.write_text(text+'\n\n---\n\n'+old,encoding='utf-8')

prepend(ROOT/'demo/README.md','''# Versión vigente: demo6

16 de octubre de 2026. Abrir [demo6.html](demo6.html). Guía completa: [DEMO6.md](DEMO6.md). La documentación que sigue describe versiones anteriores; para cifras y parámetros actuales consultar [Metodología](../modelado/METODOLOGIA.md) y [Resultados](../modelado/RESULTADOS.md).

Demo6 inicia con la referencia de 2021 según los metadatos guardados y permite comparar Ridge. Los rangos se calculan por método, no con un ±21.05 pp fijo. Conserva la consulta histórica y las islas, añade agregaciones ponderadas, gráfica, brecha estatal y CSV de la consulta. Demo5 continúa disponible.''')
prepend(ROOT/'README.md','''# Actualización Umbral demo6

16 de octubre de 2026. Versión de consulta actual: [demo6](demo/demo6.html), con [guía](demo/DEMO6.md), [metodología actualizada](modelado/METODOLOGIA.md) y [resultados vigentes](modelado/RESULTADOS.md). El reporte y la presentación de entrega se actualizan con los artefactos existentes. Esta actualización no reentrena el modelo. Las referencias fechadas más abajo documentan etapas previas.''')
prepend(ROOT/'CORRECCIONES_Y_ESTADO.md',f'''# Estado de demo6 · {DATE}

Demo6 incorpora consulta unificada, mapa y resúmenes ponderados, serie temporal con proyección diferenciada, brecha municipal-estatal, métricas reales, coeficientes Ridge y descarga CSV independiente de la simulación. Presets SMS/llamada con supuestos explícitos. Consulta histórica sin recomendaciones ni proyecciones del pasado.

{summary}

{rule}

Las cifras y rangos actuales sustituyen las menciones fijas de versiones previas. Evidencia técnica: [guía demo6](demo/DEMO6.md) y [metodología](modelado/METODOLOGIA.md). Voto Vigía no se modifica.''')
prepend(Path('README.md'),'# Umbral demo6\n\nVersión actual: [abrir demo6](02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html). [Guía](02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md), [metodología](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md) y [resultados](02_Prediccion_y_escenarios_de_riesgo/modelado/RESULTADOS.md), actualizados el 16 de octubre de 2026. Voto Vigía se conserva como proyecto separado.')
for path in [Path('EXPLICACION_DEL_PROYECTO.md'),Path('ANALISIS_GENERAL_DEL_PROYECTO.md'),ROOT/'entrega/README.md',ROOT/'entrega/GUION_PRESENTACION.md']:
    if path.exists():prepend(path,'> Actualización de 16 de octubre de 2026: la versión vigente es demo6. Consultar `02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md` y `modelado/RESULTADOS.md` del track para parámetros y cifras actuales. El contenido fechado anteriormente conserva el contexto de su versión y no debe usarse como fuente de las métricas vigentes.')

scenario=C['scenario'];m=C['municipality']
case=f'''# Caso municipal vigente: SOLIDARIDAD, clave histórica 23008

{DATE}. Nombre del catálogo histórico, sin certificar denominación ni límites actuales. Fuente reproducible: `caso_municipal.json` y `generar_caso.cjs`.

Abrir `demo/demo6.html`, seleccionar Quintana Roo y 23008, año 2027, método Ridge explícito y catálogo constante. Demo6 inicia con la referencia; para este ejemplo hay que cambiar el método. Elegir SMS Suecia y cobertura total de 1,000 personas.

| Indicador | Valor |
|---|---:|
| Puesto Ridge, cohorte nacional de catálogo constante | {C['position_ridge']} |
| Puesto de referencia, misma cohorte | {C['position_reference']} |
| Abstención de referencia 2021 | {m['baseline']:.6f}% |
| Proyección Ridge 2027 | {scenario['before']:.6f}% |
| SV+NV 2024 | {m['observed_2024']:,.0f} |
| LN 2024 | {m['ln_2024']:,.0f} |
| NS 2021 / 2024 | {m['ns_2021']:.2f}% / {m['ns_2024']:.2f}% |
| Frecuencia de selección nacional top50 | {C['stability']['count']}/6 |
| Cobertura total prevista | 1,000 personas |
| Votos adicionales hipotéticos | {scenario['additional_hypothetical']} |
| Rango externo trasladado | {scenario['additional_low']}–{scenario['additional_high']} |
| Proyección posterior | {scenario['after']:.6f}% |
| Reducción | {scenario['reduction_pp']:.6f} pp |

H = 1,000 × 0.30 / 100 = 3. La tasa posterior resta 100 × H / 255,362. El efecto es ITT: personas asignadas al SMS, no lectores efectivos. Fuente: Lindgren, Nyman y Oskarsson (2025), DOI 10.1017/S0007123424000504. El traslado a México es una hipótesis y el rango no cubre incertidumbre del predictor ni de transferencia.

Los puestos y frecuencia anteriores corresponden al ranking nacional top50 con catálogo constante, no a la simulación sobre un municipio. Las variantes NS≤5% no son elegibles. La consulta local recalcula su propio universo; 4/6 no equivale a una probabilidad de acierto del 67%.

La propuesta preventiva requiere validar canal, población, capacidad y atribuciones con el área usuaria. Registrar cobertura agregada y comprensión con un protocolo previo. Evaluar causalmente la participación exige un piloto independiente; el ejemplo no acredita un resultado observado.
'''
(ROOT/'entrega/CASO_MUNICIPAL.md').write_text(case,encoding='utf-8')

def assign_literal(source,name,value):
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
    lines=source.splitlines(keepends=True)
    import pprint
    return ''.join(lines[:node.lineno-1])+name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'+''.join(lines[node.end_lineno:])

# Actualizar el contenido del reporte manteniendo sus 14 páginas y su diseño.
p=ROOT/'entrega/reporte/generar_reporte.py';s=p.read_text(encoding='utf-8')
tree=ast.parse(s);pages=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PAGES' for t in n.targets)))
updates={
'Ajuste Ridge':f'Ridge estima un ajuste regularizado respecto de la referencia. El paquete actual registra alpha final {M["alpha_final"]} y {len(M["feature_names"])} nombres de variables, con interacciones y variables demográficas de proyección. Estandarización y entrenamiento utilizan antecedentes del corte. Demo6 permite comparar ambos métodos; no reentrena ni demuestra precisión futura.',
'Regla de selección':'El artefacto identifica persistencia como método seleccionado. La regla de sesgo vigente compara cambios con signo y rechaza Ridge al caer más de 3 pp, incluso si mejora el sesgo absoluto. Demo6 respeta la selección guardada; revisar la regla requiere un experimento independiente. No se presenta como evidencia de superioridad universal.',
'Lectura honesta':summary,
'Incertidumbre de prioridad, no de intervalo':f'El rango ilustrativo depende del método: P90 retrospectivo de 2021, ±{M["checks"]["2021"]["persistencia"]["error_absoluto_p90"]:.2f} pp para referencia y ±{M["checks"]["2021"]["ridge"]["error_absoluto_p90"]:.2f} pp para Ridge, acotado a [0,100]. No es un intervalo prospectivo. La frecuencia de seis variantes describe acuerdo y no probabilidad. Los rangos SMS pertenecen a estudios externos.',
'Caso 23008: SOLIDARIDAD (catálogo histórico)':f'Ridge explícito, catálogo constante, puesto nacional {C["position_ridge"]}; referencia {C["position_reference"]}. Proyección {scenario["before"]:.6f}%; referencia 2021 {m["baseline"]:.2f}%. Frecuencia nacional top50 {C["stability"]["count"]}/6. SMS Suecia, 1,000 personas asignadas, ITT 0.30 pp: 3 votos hipotéticos [1.3,4.8], posterior {scenario["after"]:.6f}%, reducción {scenario["reduction_pp"]:.6f} pp. Base 255,362. La fuente externa no valida efecto en México. Puestos y frecuencia son del ranking nacional, no del plan local.',
'Vista operativa':'Demo6 conserva año y territorio al cambiar de método, muestra históricos sin proyecciones del pasado, agrega resumen ponderado y brecha estatal, gráfica temporal y exportación de toda la consulta. La simulación compara antes/después con presets editables. Cartografía municipal e islas INEGI, con límites históricos sin armonizar.',
'Reproducibilidad y cierre':'Abrir demo/demo6.html con doble clic. Las métricas del reporte proceden de los artefactos existentes, sin nuevo entrenamiento. La consulta exporta históricos y proyecciones; el plan conserva supuestos y fuentes. Guía: demo/DEMO6.md. El caso se regenera con entrega/generar_caso.cjs. Revisar límites, capacidad y protocolo de evaluación antes de un piloto.',
'Límites territoriales':'Base municipal CONABIO/INEGI AGEM 2024 y complemento de 308 componentes insulares INEGI 2025 en 34 municipios. Cruce por nombre y entidad, sin sustituir el continente. Claves y límites históricos no armonizados. Fuentes y hashes en demo/data/*metadatos.json.'
}
new=[]
for label,title,sections in pages:
    new.append((label,title,[(h,updates.get(h,body).replace('6 de octubre de 2026',DATE)) for h,body in sections]))
s=assign_literal(s,'PAGES',new)
s=s.replace('6 de octubre de 2026',DATE).replace("FIG=ROOT/'demo/verificacion'","FIG=ROOT/'demo/verificacion/demo6'")
s=s.replace('Regla de selección','Regla de selección')
s=s.replace("'visual_review':'14 páginas inspeccionadas individualmente; sin recortes ni superposición'","'visual_review':'Render generado; revisión visual separada de las comprobaciones de texto y límites'")
p.write_text(s,encoding='utf-8')

# Actualizar el contenido de las 10 diapositivas sin cambiar su plantilla.
p=ROOT/'entrega/presentacion/generar_presentacion.py';s=p.read_text(encoding='utf-8-sig')
tree=ast.parse(s);slides=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='slides' for t in n.targets)))
slides[0]=(slides[0][0],[(t.replace('6 de octubre de 2026',DATE),size) for t,size in slides[0][1]],slides[0][2])
slides[1]=('Consulta territorial en demo6', [('Municipio, estado o país',26),('Un mismo año y método para el mapa, el resumen y la ficha. Los históricos muestran resultados observados y 2027 una proyección diferenciada.',21),('Gráfica temporal y comparación con el promedio estatal, ponderados por personas con dato de voto.',21),('La consulta completa se descarga en CSV, aunque no se configure una intervención.',21)],'Guía: demo/DEMO6.md. Cartografía municipal y complemento insular INEGI 2025.')
slides[3]=(slides[3][0],[(t.replace('Alpha = 10 permanece congelado. Cada corte aprende con resultados anteriores al año objetivo.','Alpha del artefacto: 500. Demo6 inicia con referencia de 2021 y permite comparar Ridge.'),size) for t,size in slides[3][1]],'Fuente: demo/data/resultados.json. La regla de sesgo guardada requiere revisión independiente, sin reentrenamiento en esta actualización.')
slides[6]=('Una ficha para entender la selección', [('Resultados observados y proyección diferenciados',25),('Serie temporal 2009–2024 con 2027 separado visualmente. Faltantes visibles y cobertura declarada.',21),('Brecha municipal frente al estado con el mismo método y denominador. Las diferencias agregadas no identifican causas.',21),('Métricas reales y coeficientes Ridge disponibles. Los coeficientes no son efectos causales ni explicaciones individuales.',21)],'Demo6. Umbrales nacionales por año y método; fijos entre escenarios.')
slides[7]=(slides[7][0],[(slides[7][1][0][0],24),(f'Puesto Ridge {C["position_ridge"]}, referencia {C["position_reference"]}. Base {scenario["before"]:.6f}%. Frecuencia nacional top50 {C["stability"]["count"]}/6.',21),('1,000 personas asignadas a SMS Suecia: 3 votos adicionales hipotéticos; rango externo 1.3–4.8.',22),(f'Posterior {scenario["after"]:.6f}%. Reducción {scenario["reduction_pp"]:.6f} pp. Traslado a México sujeto a evaluación.',21)],'Fuente: entrega/caso_municipal.json. Método Ridge explícito. SV+NV 2024: 255,362. DOI 10.1017/S0007123424000504.')
s=assign_literal(s,'slides',slides)
old=next(line for line in s.splitlines() if line.strip().startswith("data=[['Corte / método'"))
s=s.replace(old,'        data='+repr([['Corte / método','n','MAE (pp)','Ponderado','Top50']]+[[r[0]+' · '+r[1]]+r[2:] for r in rows]))
s=s.replace("        tree.append(table)\n", "        tree.append(table)\n        for row_node,values in zip(table.findall('.//a:tr',NS),data):\n            for cell,value in zip(row_node.findall('a:tc',NS),values):\n                runs=cell.findall('.//a:t',NS)\n                if runs:\n                    runs[0].text=value\n                    for run in runs[1:]:run.text=''\n")
old=next(line for line in s.splitlines() if "text(slide,'Spearman referencia" in line)
s=s.replace(old,"        text(slide,'Cifras de los artefactos actuales. 2021 participa en selección; 2024 no valida la intermedia de 2027.',.65,5.6,12,.7,20)")
p.write_text(s,encoding='utf-8')
print('Documentación activa, caso y generadores actualizados.')

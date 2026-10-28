"""Reporte de 14 páginas; fuente MD, PDF y render/QA reproducibles. Python 3.10+.

Estructura: portada y resumen ejecutivo (1), problema y decisión (1),
datos y variables (2), modelo (2), evidencia y límites (2), semáforo (1),
escenarios (1), prevención y priorización (3), viabilidad (1). Total: 14.
La convocatoria admite 10-15 cuartillas para el Reto 2 y no define "cuartilla";
este documento usa una cuartilla = una página carta de PDF (ver LEEME).
"""
from pathlib import Path
import sys, json, hashlib, html
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE/'.packages'),str(HERE.parents[2]/'.task_packages')]
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
ROOT=HERE.parents[1]
FIG=ROOT/'demo/verificacion/demo7'
M=json.loads((ROOT/'modelado/salidas/metricas.json').read_text(encoding='utf-8'))
BENCHMARK=json.loads((ROOT/'modelado/salidas/comparacion_modelos/resultados.json').read_text(encoding='utf-8'))
FORECAST=json.loads((ROOT/'demo/data/comparacion_modelos.json').read_text(encoding='utf-8'))
RATES=sorted(r[BENCHMARK['selected_model']] for r in FORECAST['forecasts'] if r.get(BENCHMARK['selected_model']) is not None)
def quantile(q):
    pos=(len(RATES)-1)*q;index=int(pos)
    return RATES[index]+(RATES[min(index+1,len(RATES)-1)]-RATES[index])*(pos-index)
RISK_LEGEND=f"HistGradientBoosting 2027: verde, bajo < {quantile(1/3):.2f}%; amarillo, medio desde {quantile(1/3):.2f}% y < {quantile(2/3):.2f}%; rosa, alto desde {quantile(2/3):.2f}%. Gris: sin estimación. Cortes redondeados; el cálculo conserva precisión completa."
M['checks']={year:{**cut['models'],'persistencia':cut['models']['baseline']} for year,cut in BENCHMARK['cuts'].items()}

PAGES=[('UMBRAL',
  'Resumen ejecutivo',
  [('Reporte metodológico y preventivo · Reto 2',
    'aguas.exe. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Versión técnica para '
    'revisión, 28 de octubre de 2026. Horizonte de predicción: elección intermedia de 2027. Cobertura: México por '
    'municipio, claves INE. Datos históricos ordinarios 2009-2024. Reporte de 14 páginas.'),
   ('Resumen ejecutivo',
    'Umbral predice la abstención municipal para las elecciones de 2027, permite consultar información electoral y simula acciones para reducir la abstención. Utiliza conteos del INE de 2009 a 2024 y características sociodemográficas agregadas. De 2,477 claves históricas, 1,783 tienen información suficiente para estimar. Se compararon cuatro modelos y se seleccionó HistGradientBoosting: su error absoluto medio fue de 6.84 puntos porcentuales en las evaluaciones de 2021 y 2024, frente a 8.88 de la referencia simple. Las predicciones pueden equivocarse y su acierto en 2027 se comprobará cuando existan resultados observados. La consulta informativa reúne históricos, perfiles territoriales y fuentes. El simulador calcula cambios hipotéticos con coeficientes publicados en investigaciones y coberturas elegidas por el usuario. Además, propone planes para las 32 entidades, apoyados en su contexto y en estudios mexicanos de participación y abstencionismo. Los coeficientes de acciones específicas y los supuestos del plan estatal se presentan por separado. El conjunto sirve para anticipar riesgos, entender los territorios y preparar decisiones de prevención y recursos.'),
   ('Alcance de la propuesta',
    'Umbral es una herramienta predictiva, informativa y de simulación. Sus estimaciones orientan la priorización y sus planes proponen actividades para revisión institucional. La evaluación histórica permite conocer errores del predictor; no elimina el error futuro. Los escenarios calculan qué ocurriría si se cumplieran los efectos y coberturas indicados. El respaldo documental de una propuesta no equivale a haber demostrado su eficacia en cada estado.')]),
 ('01 / PROBLEMA Y DECISIÓN',
  'Para qué sirve y para quién',
  [('Pregunta operativa',
    'Si un área de educación cívica puede atender a un número limitado de personas, ¿en qué municipios conviene concentrar el trabajo y con qué criterio? Umbral permite comparar la abstención estimada, revisar la información disponible y repartir esa capacidad. Por ejemplo, una cobertura de 1,000 personas para un estado se distribuye entre sus municipios: no equivale a atender 1,000 en cada uno. El escenario permite examinar el cambio que se obtendría si se cumpliera el efecto supuesto de la acción.'),
   ('Criterio de prioridad y selector',
    'La prioridad principal es la tasa de abstención estimada, no el número absoluto ni el deterioro. El prototipo '
    'permite elegir entre tres lentes que responden preguntas distintas: tasa (proporción estimada), volumen sobre la '
    'población observable (cuántas abstenciones) y deterioro frente a la última elección del mismo tipo. Cambiar el '
    'lente cambia la lista; la elección responde al objetivo institucional declarado, no a un valor universal.'),
   ('Persona usuaria y flujo de uso',
    'Un área de educación cívica elige municipio, estado o país, catálogo, método y criterio; define cobertura total, '
    'distribución y acción; revisa estimaciones, exclusiones y evidencia; compara el territorio completo y descarga el '
    'plan.')]),
 ('02 / DATOS Y VARIABLES (1/2)',
  'De conteos a una base comparable',
  [('Fuente y volumen auditado',
    'Conteos Censales de Participación Ciudadana del INE, seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y '
    '2024, agregados y disociados, sin datos personales. Se auditaron 54,872,712 filas de 192 CSV con integridad CRC, '
    'duplicados y reconciliación de conteos, y se generaron 14,779 registros municipio-año y 2,477 claves. Prisión '
    'preventiva y voto anticipado se conservan como fuentes separadas. Fuente: auditoria/ y datos_preparados/.'),
   ('Definiciones',
    'SV: participación registrada. NV: no participación. NS: participación no especificada. LN = SV + NV + NS. '
    'Abstención observable (%) = 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. La '
    'suma de conteos precede al cálculo de porcentajes: una tasa vacía es denominador cero, no abstención de cero.'),
   ('Reglas de calidad y cobertura',
    'Se exige NS ≤10% en el antecedente más reciente y en el del mismo tipo; la evaluación exige además objetivo '
    'observable con NS ≤10%. En 2027 hay 1,783 municipios con estimación y 694 sin estimación sobre 2,477 claves. La '
    'exclusión por calidad puede apartar zonas con necesidad alta: es un sesgo de cohorte que debe declararse. Fuente: '
    'modelado/salidas/metricas.json.'),
   ('Límite territorial',
    'Se conservan 2,477 claves, con proyección NS10 para 1,783. La cartografía incorpora 308 componentes insulares '
    'oficiales. Los límites históricos no están armonizados y la coincidencia de claves no prueba continuidad '
    'territorial.')]),
 ('02 / DATOS Y VARIABLES (2/2)',
  'Variables usadas, omitidas y trazabilidad',
  [('TABLE_VARIABLES', ''),
   ('Variables omitidas y por qué',
    'Sexo, escolaridad y variables externas no verificadas no forman parte del predictor. Sexo existe en la fuente y '
    'se usa solo en la capa explicativa posterior (sección de prevención); el modelo conserva variables agregadas '
    'verificables para reducir sobreajuste y fuga. La representación etaria es agregada; no se infieren '
    'características individuales.'),
   ('Trazabilidad',
    'Cada cifra proviene de archivos citados en el pie de tabla o en el texto: '
    'datos_preparados/municipios_historico_con_calidad.csv, modelado/salidas/metricas.json, evaluacion_adicional.json '
    'y perfil_demografico.json. El diccionario de datos y las tablas largas viven en la base CSV y el repositorio, no '
    'en este PDF.')]),
 ('03 / MODELO (1/2)',
  'Referencia homóloga y cuatro regresores',
  [('Referencia',
    'Predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si '
    'no existe antecedente válido, no se sustituye por otro tipo electoral. Es interpretable y constituye la exigencia '
    'mínima que la complejidad debe superar.'),
   ('Cuatro regresores',
    'Ridge, HistGradientBoosting, LightGBM y CatBoost estiman una cantidad continua: el cambio respecto a la última elección del mismo tipo. A ese cambio se le llama residual. Si la referencia fuera 60% y el cambio estimado fuera -4 puntos porcentuales, la proyección sería 56%; es un ejemplo didáctico, no un resultado municipal. Ridge ajusta una relación lineal; los otros tres métodos combinan árboles de decisión para representar relaciones más complejas. La comparación usa las mismas 15 variables y los mismos municipios, cuatro configuraciones por familia, semilla 42 y un hilo de CPU. Así se evita favorecer a un modelo con información adicional.'),
   ('Flujo simple',
    'Antecedentes observados con calidad verificada → Referencia del mismo tipo → Ajuste del residual con el modelo seleccionado → '
    'Estimación 2027 → Semáforo relativo, estabilidad y decisión con capacidad.')]),
 ('03 / MODELO (2/2)',
  'Construcción, cortes y regla de selección',
  [('Cortes temporales',
    'Se simula qué habría podido conocerse antes de cada elección. Para evaluar 2021 se entrena con 2015 y 2018; las configuraciones se comparan primero prediciendo 2018 a partir de 2015. Para evaluar 2024 se entrena con 2015, 2018 y 2021, usando las evaluaciones internas de 2018 y 2021 para elegir configuraciones. Los resultados del año evaluado no se usan para ajustar ese modelo. Finalmente, la proyección de 2027 incorpora datos hasta 2024. Esta separación temporal evita usar información del futuro durante el ajuste.'),
   ('Regla de selección',
    'Menor MAE medio, igual peso para 2021 y 2024. Diferencias ≤0.05 pp se desempatan por MAE ponderado; después top50 '
    'y tiempo. HistGradientBoosting y LightGBM empatan dentro de la tolerancia; gana el primero por su menor MAE '
    'ponderado. La regla previa de sesgo con signo no se usa en este experimento.'),
   ('Selección retrospectiva',
    'Los dos backtests participan en la selección final. 2024 ya fue examinado en etapas anteriores del proyecto. No '
    'hay una elección futura independiente después de elegir al ganador; la proyección 2027 sigue siendo '
    'exploratoria.')]),
 ('04 / EVIDENCIA Y LÍMITES (1/2)',
  'Comparación temporal de cuatro modelos',
  [('TABLE_METRICS', ''),
   ('Cómo leer los resultados',
    'MAE es el error absoluto medio: cuánto se aparta la estimación del valor observado. Se expresa en puntos porcentuales (pp); pasar de 40% a 45% equivale a 5 pp. La columna Pond. da mayor peso a municipios con mayor población observable. n indica municipios evaluados. Top50 cuenta coincidencias entre los 50 municipios con mayor abstención estimada y los 50 con mayor abstención observada. Un menor MAE es mejor; en Top50, un mayor número es mejor.'),
   ('Resultados y límites de priorización',
    'Se publican MAE, error ponderado, sesgo con signo, P90 y aciertos top50 para cada método y corte. En 2024 la '
    'referencia recupera 27/50 frente a 19/50 de HistGradientBoosting: mejorar error no garantiza mejor priorización. '
    'Fuente: modelado/salidas/comparacion_modelos/resultados.json.')]),
 ('04 / EVIDENCIA Y LÍMITES (2/2)',
  'Estabilidad, incertidumbre y límites',
  [('Estabilidad del top N',
    'Seis variantes: referencia y método activo, con límites de participación no especificada (NS) de 5%, 10% y 20%. Al consultar referencia, el comparador es '
    'Ridge. Se fijan los parámetros elegidos en NS10 y se reentrena sobre cada cohorte. La frecuencia describe el '
    'ranking topN; no es probabilidad ni se utiliza para elegir al ganador.'),
   ('Incertidumbre de prioridad, no de intervalo',
    'P90 es el valor por debajo del cual quedó el 90% de los errores absolutos en la evaluación de 2021. Para HistGradientBoosting fue 18.04 pp. La ficha muestra ese margen alrededor de la proyección, limitado a [0,100]. Sirve para dimensionar el error histórico; no garantiza que el resultado de 2027 quede dentro de ese rango.'),
   ('Error por tamaño y límites',
    'El P90 del error por denominador observable previo (<10 mil, 10-100 mil, ≥100 mil) describe heterogeneidad por '
    'escala, no un intervalo para 2027. Límites: seis ocasiones electorales y tres intermedias; 2024 es presidencial y '
    'no valida 2027; sin causalidad; selección por calidad que puede excluir zonas con necesidad alta.')]),
 ('05 / SEMÁFORO',
  'Clasificación territorial y estabilidad',
  [('Tercios relativos',
    'Bajo, medio y alto son tercios de las estimaciones nacionales válidas. Alto es el tercio superior de tasas '
    'estimadas; no es probabilidad calibrada de deterioro. Gris significa información insuficiente para estimar, se '
    'muestra con motivo de exclusión y nunca recibe riesgo cero.'),
   ('Leyenda de la figura y umbrales',RISK_LEGEND),
   ('Eje de estabilidad',
    'La calidad (NS), la estabilidad entre seis variantes y el acuerdo entre métodos se informan como dimensión '
    'separada del color, en la lista y en la ficha. Los umbrales base permanecen fijos al comparar escenarios para que '
    'el color no se redefina entre ellos.'),
   ('Cobertura del catálogo',
    'El catálogo constante restringe la consulta a claves presentes en la serie histórica: quedan 1,144 estimaciones, frente a 1,783 sin ese filtro. Esta diferencia corresponde a la cobertura del catálogo, no a mover los cortes del semáforo. La coincidencia de claves tampoco garantiza límites municipales idénticos. Fuente: modelado/salidas/metricas.json.'),
   ('FIGURE_MAP_STATES', '')]),
 ('06 / ESCENARIOS',
  'Sin intervención y con intervención hipotética',
  [('Fórmulas del escenario',
    'O = SV2024 + NV2024. E es cobertura asignada, limitada por O. Acción con evidencia: H = mínimo(E × efecto_pp/100, '
    'E × tasa/100). Personalizada: H = E × tasa/100 × respuesta/100, sin evidencia causal. Tasa posterior = tasa - 100 '
    '× H/O. La comparación pondera por O TODOS los municipios estimables filtrados, incluidos los no atendidos (H=0).'),
   ('Supuestos explícitos',
    'O es referencia observable 2024, no electorado 2027. Transferencia del efecto extranjero a México hipotética y no '
    'validada. ITT mide el efecto de asignar la intervención; ATT, el efecto entre quienes la reciben. SMS usa asignaciones; llamada exige contactos efectivos. No sumar acciones ni '
    'efectos. País: «México: municipios con estimación incluidos»; catálogo y exclusiones explícitos.'),
   ('FIGURE_TRIPLE', ''),
   ('Plan estatal de Umbral',
    'Al elegir un estado se muestra un escenario ilustrativo: cobertura del 10% de la base estimable y efecto '
    'supuesto de 1.5 pp entre alcanzados (variantes 0.3 y 3 pp). Son supuestos del proyecto, no eficacia medida '
    'del plan ni intervalos de confianza. Cobertura fija y reparto proporcional; un único efecto para el plan, '
    'sin sumar actividades. Fuente: docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md, sección 8.')]),
 ('07 / PREVENCIÓN (1/3)',
  'Tipologías observables y línea de acción',
  [('Tipologías por perfil observable',
    'Se derivan tipologías de información agregada, no de personas: territorio con menor proporción urbana; proporción '
    'joven 18-29 ≥25%; proporción 60+ ≥25%; y calidad insuficiente (NS alto o antecedentes incompletos). Cada '
    'tipología lleva una línea de acción: información electoral accesible, talleres en espacios educativos y '
    'comunitarios, material legible, o revisión de datos antes de priorizar.'),
   ('Uso de los perfiles territoriales',
    'El criterio elegido ordena los municipios; las tipologías ayudan a adaptar las actividades a su contexto. El perfil CCPC por edad, sexo y tipo de sección describe grupos agregados, sin explicar por sí solo las causas de abstención. El predictor usa proporciones de edad y urbanización; no usa sexo ni las tipologías posteriores. Los grupos con muestra insuficiente se señalan. Fuente: modelado/salidas/perfil_demografico.json.'),
   ('Sustento de los planes estatales', 'Los planes de las 32 entidades son propuestas del proyecto que combinan contexto territorial, estudios mexicanos sobre abstencionismo y participación, ENCUCI 2020 y el marco de ENCÍVICA. Estas fuentes orientan el diagnóstico y las líneas de acción; los planes no se transcriben de ellas. Los coeficientes del simulador proceden de investigaciones sobre intervenciones específicas. El efecto de 1.5 pp del plan estatal es un supuesto independiente. Fuentes y alcances: docs/FUENTES_COMPLEMENTARIAS_UMBRAL.md y docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md.'),
   ('Mecanismo como hipótesis',
    'SMS Suecia: ITT 0.30 pp [0.13,0.48], Lindgren, Nyman y Oskarsson (2025), resultados, figura 1; DOI '
    '10.1017/S0007123424000504. SMS EEUU: ITT 0.25 pp, IC95% [0.17,0.34], Haenschen, Mann y DeMora (2026), '
    'introducción; DOI 10.1007/s11109-026-10121-2. Plan de voto por llamada: ATT 4.1 pp, EE 1.7, ITT publicado 0.9 pp; '
    'Nickerson y Rogers (2010), pp.194-199, tabla 1; DOI 10.1177/0956797609359326. ATT exige contacto efectivo: no '
    'intentos ni talleres. No sumar acciones. México requiere validación propia.')]),
 ('07 / PREVENCIÓN (2/3)',
  'Ficha tipo y ejemplo completo',
  [('Ficha tipo',
    'La ficha reúne condición observable, acción, responsable propuesto, cobertura, recursos y medición. Para este caso se propone que el área de educación cívica revise el mensaje, confirme un canal autorizado y registre asignaciones y entregas. Las 1,000 personas son un supuesto de simulación; personal, horas y costo deben acordarse antes del piloto. Entregar un mensaje no demuestra que haya causado un voto.'),
   ('Caso 23008: SOLIDARIDAD (catálogo histórico)',
    'HistGradientBoosting, catálogo constante: puesto 9; referencia 3. Proyección 61.636222%. Frecuencia nacional '
    'top50 4/6. SMS Suecia a 1,000 personas asignadas: 3 votos hipotéticos [1.3,4.8], posterior 61.635048%, reducción '
    '0.001175 pp. Base 255,362. La transferencia del efecto a México requiere evaluación. Fuente: '
    'entrega/caso_municipal.json.'),
   ('Interpretación del cambio municipal',
    'En este ejemplo, 0.30 pp entre 1,000 personas equivalen a 3 votos hipotéticos. Al repartir ese cambio sobre la base municipal de 255,362 personas, la reducción es de apenas 0.001175 pp. Por eso puede resultar imperceptible en el mapa. El CSV permite revisar las cifras sin depender del color; la ficha imprimible reúne la recomendación y sus límites.')]),
 ('07 / PREVENCIÓN (3/3)',
  'Priorización de recursos y diseño de evaluación',
  [('Priorización de recursos',
    'Cobertura total limitada a población observable elegible. Prioridad concentra cupo siguiendo ranking hasta '
    'agotarlo. Proporcional distribuye según SV+NV2024 entre todos los elegibles, redondeo por mayor resto y desempate '
    'determinista. Son decisiones del proyecto, no reglas de la literatura. Con coeficiente homogéneo y sin activar el '
    'límite de abstenciones, igual cobertura produce igual H total: cambia dónde se asigna, no necesariamente el '
    'impacto agregado. Estabilidad de referencia separada del reparto actual.'),
   ('Diseño de evaluación propuesto',
    'Se propone un piloto en tres etapas. Antes de iniciar: el área responsable confirma territorios, capacidad, canal y costos; fija indicadores y un protocolo de análisis. Durante la ejecución: se asigna al azar atención inmediata o diferida entre municipios cercanos al límite de capacidad, equilibrando entidad, tamaño y contexto; se registran personas alcanzadas, horas y comprensión del mensaje. Al cierre: se comparan los grupos y se documentan costos y dificultades. Medir comprensión permite evaluar la comunicación, pero demostrar un cambio en participación requiere observar resultados electorales y una evaluación causal. La proximidad en el ranking no sustituye la asignación aleatoria.'),
   ('Vista operativa',
    'Umbral permite consultar históricos y el plan estatal con su cálculo fijo, simular acciones con cobertura '
    'editable y comparar mapas sin/con acción con umbrales comunes. El CSV incluye municipios atendidos, pendientes '
    'y sin estimación, tasas antes/después, semáforo, fuente y denominador. La ficha imprimible resume recursos y '
    'límites. Revisar responsables, horas y costo real antes de cualquier piloto.')]),
 ('08 / VIABILIDAD',
  'Qué se puede defender hoy y qué falta',
  [('TABLE_VIABILITY', ''),
   ('Riesgos de uso',
    'Uso automático de la lista como asignación definitiva; lectura causal del escenario; y falacia ecológica al pasar '
    'del municipio a la persona. Se mitigan con revisión humana, etiquetando el escenario como hipótesis y sin inferir '
    'comportamiento individual del agregado.'),
   ('Reproducibilidad y cierre',
    'Para consultar la entrega, descomprimir el ZIP y abrir index.html junto a los PDF, CSV y carpetas incluidos. El mapa utiliza proyecciones precalculadas; no necesita entrenar modelos al abrirse. La carpeta codigo contiene la aplicación y el experimento de cuatro modelos. En el repositorio se conservan el protocolo, las predicciones por municipio, el modelo serializado y las huellas de integridad. Las rutas citadas en este reporte se refieren al proyecto completo; no todas forman parte del ZIP. Repositorio: https://github.com/Donatelatrump/Ine_Hackaton_2026.')])]

VARIABLES=[['Variable', 'Uso y por qué'],
 ['Abstención del mismo tipo',
  'Antecedente comparable; base de la referencia y de la estabilidad entre elecciones del mismo tipo.'],
 ['Abstención del último proceso', 'Señal más reciente del territorio.'],
 ['Diferencia último − mismo tipo', 'Capta deterioro o mejora reciente.'],
 ['log(1 + LN)', 'Logaritmo natural de uno más la lista nominal; controla la escala.'],
 ['Proporción 18-29', 'Composición joven agregada; patrón documentado de mayor abstención.'],
 ['Proporción 60+ (sin >120)', 'Composición de mayor edad; reduce valores extremos.'],
 ['Proporción urbana', 'Contexto territorial agregado.'],
 ['NS de ambos antecedentes', 'Calidad del dato como condición de inclusión.'],
 ['Tipo de elección (intermedia)', 'Distingue intermedias de presidenciales.'],
 ['Interacciones electorales', 'Dos interacciones: tasas previas por tipo de elección.'],
 ['Indicadores complementarios',
  'Tres transformaciones de NS, distancia a 50% y volatilidad; no acreditan competitividad real.']]

VIABILITY=[['Se puede defender hoy','Falta evidencia o validación'],
['Marco de decisión con capacidad y criterio explícitos','Aceptación institucional del flujo y de los responsables.'],
['Auditoría de datos y calidad visible','Armonización histórica de límites municipales.'],
['Comparación con la referencia (2021 y 2024)','Validación futura y mejora de la identificación del grupo prioritario.'],
['Análisis posteriores congelados (rango, tamaño, estabilidad)','Semáforo calibrado como probabilidad; hoy es relativo.'],
['Escenarios y fichas preventivas revisables','Costos monetarios y efecto causal.'],
['Reproducibilidad local (mapa, cifras, código)','Piloto ejecutado y evaluado.']]

def add_results():
 p=ROOT/'modelado/salidas/evaluacion_adicional.json'
 if not p.exists(): return 'Las definiciones de esta página constituyen el protocolo posterior. Las cifras completas se consultan en evaluacion_adicional.json; no se imputan resultados ausentes.'
 data=json.loads(p.read_text(encoding='utf-8'))
 parts=[]
 for yr in ['2021','2024']:
  for method in ['persistencia','ridge']:
   a=data['cuts'][yr][method]
   parts.append(f"{yr} {method}: Spearman {a['spearman']:.3f}; precisión alta {a['precision_rojo']*100:.1f}%; recobrado {a['recobrado_rojo']*100:.1f}%.")
 return '\n'.join(parts)

def main():
 for f,name in [('arial.ttf','Arial'),('arialbd.ttf','Arial-Bold')]:
  p=Path('C:/Windows/Fonts')/f
  if p.exists():pdfmetrics.registerFont(TTFont(name,str(p)))
 regular='Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
 bold='Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
 style=ParagraphStyle('body',fontName=regular,fontSize=11,leading=16.5,textColor=HexColor('#253b3b'),spaceAfter=8)
 hstyle=ParagraphStyle('head',fontName=bold,fontSize=12,leading=16,textColor=HexColor('#12645e'))
 note_style=ParagraphStyle('note',fontName=regular,fontSize=8.5,leading=11.5,textColor=HexColor('#526a62'),spaceAfter=6)
 total=len(PAGES)
 pdf=HERE/'Umbral_reporte_metodologico_preventivo.pdf'
 c=canvas.Canvas(str(pdf),pagesize=(612,792));c.setTitle('Umbral | Reporte metodológico y preventivo')
 md=['# Umbral: reporte metodológico y preventivo','Versión técnica para revisión | 28 de octubre de 2026',f'Estructura de {total} páginas (8 secciones)']
 def paragraph(txt,st):
  nonlocal y
  p=Paragraph(html.escape(txt).replace('\n','<br/>'),st);w,h=p.wrap(516,700);y-=h;p.drawOn(c,48,y);y-=6
 def draw_table(rows,widths):
  nonlocal y
  wrapped=[[Paragraph(html.escape(str(v)),ParagraphStyle('cell',fontName=regular,fontSize=9,leading=12,textColor=HexColor('#ffffff' if ri==0 else '#253b3b'))) for v in row] for ri,row in enumerate(rows)];t=Table(wrapped,colWidths=widths);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),regular),('FONTSIZE',(0,0),(-1,-1),9),('LEADING',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),HexColor('#12645e')),('TEXTCOLOR',(0,0),(-1,0),HexColor('#ffffff')),('BACKGROUND',(0,1),(-1,-1),HexColor('#edf4f0')),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
  w,h=t.wrap(516,y);t.drawOn(c,48,y-h);y-=h+8
 def draw_figure(kind):
  nonlocal y
  from PIL import Image
  def aspect(p):
   im=Image.open(p);return im.size[1]/im.size[0]
  if kind=='FIGURE_MAP_STATES':
   p=FIG/'mapa_base.png';w=395;h=w*aspect(p)
   c.drawImage(str(p),48,y-h,width=w,height=h,preserveAspectRatio=True,anchor='n');y-=h+3
   paragraph('Figura 1. Mapa nacional por estados del semáforo: bajo, medio, alto y sin estimación (gris). Semáforo relativo, no probabilidad. Demo Umbral.',note_style)
  elif kind=='FIGURE_TRIPLE':
   ps=[FIG/'escenario_sin.png',FIG/'mapa_intervencion.png',FIG/'mapa_cambio.png']
   labels=['(a) Sin intervención','(b) Con intervención','(c) Cambio en pp']
   w=168;h=w*aspect(ps[0])
   for i,p in enumerate(ps):
    x=48+i*(w+6);c.drawImage(str(p),x,y-h,width=w,height=h,preserveAspectRatio=True,anchor='n')
    c.setFillColor(HexColor('#526a62'));c.setFont(regular,8);c.drawCentredString(x+w/2,y-h-10,labels[i])
   y-=h+16
   paragraph('Figura 2. Mismo conjunto y umbrales base fijos: sin intervención, con intervención y cambio hipotético. Umbral, Quintana Roo: plan estatal con cobertura del 10%, efecto supuesto de 1.5 pp y reparto proporcional. No es el caso SMS municipal de 1,000 personas.',note_style)
 for i,(label,title,sections) in enumerate(PAGES,1):
  c.setFillColor(HexColor('#edf4f0'));c.rect(0,692,612,100,fill=1,stroke=0)
  c.setFillColor(HexColor('#12645e'));c.setFont(bold,10);c.drawString(48,753,label)
  c.setFont(bold,21);c.drawString(48,715,title)
  y=670;md+=['',f'## Página {i}: {title}']
  for heading,body in sections:
   if heading=='TABLE_METRICS':
    rows=[['Corte / método','n','MAE pp','Pond. pp','Top50']]
    for yr in ['2021','2024']:
     for name in ['persistencia','ridge','hgb','lightgbm','catboost']:
      a=M['checks'][yr][name];rows.append([yr+' / '+{'persistencia':'Referencia','ridge':'Ridge','hgb':'HistGradientBoosting','lightgbm':'LightGBM','catboost':'CatBoost'}[name],str(a['n']),f"{a['mae']:.3f}",f"{a['mae_ponderado']:.3f}",f"{round(a['precision_top']*50)}/50"])
    draw_table(rows,[185,50,75,75,65]);md+=['','| '+' | '.join(rows[0])+' |','|'+'---|'*len(rows[0])]+['| '+' | '.join(r)+' |' for r in rows[1:]]
    paragraph('Fuente: modelado/salidas/comparacion_modelos/resultados.json.',note_style);continue
   if heading=='TABLE_VARIABLES':
    draw_table(VARIABLES,[150,366]);md+=['','Variables del predictor en modelado/core.py: '+', '.join(r[0] for r in VARIABLES[1:])+'.'];continue
   if heading=='TABLE_VIABILITY':
    draw_table(VIABILITY,[258,258]);md+=['','| '+' | '.join(VIABILITY[0])+' |','|---|---|']+['| '+' | '.join(r)+' |' for r in VIABILITY[1:]];continue
   if heading.startswith('FIGURE_'):
    draw_figure(heading);md+=['',f'({heading})'];continue
   md+=['',f'### {heading}',body]
   paragraph(heading,hstyle);paragraph(body,style)
  if y<50:raise RuntimeError(f'Page {i} overflows: {y}')
  c.setStrokeColor(HexColor('#c4d8cf'));c.line(48,42,564,42);c.setFillColor(HexColor('#526a62'));c.setFont(regular,8);c.drawString(48,27,'UMBRAL  /  RETO 2  /  VERSIÓN TÉCNICA PARA REVISIÓN');c.drawRightString(564,27,f'{i:02d} / {total}');c.showPage()
 c.save();(HERE/'Umbral_reporte_fuente.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 doc=fitz.open(pdf);assert len(doc)==total,(len(doc),total)
 render=HERE/'revision_visual';render.mkdir(exist_ok=True)
 checks=[]
 for i,p in enumerate(doc,1):
  text=p.get_text();assert len(text)>600,(i,len(text))
  violations=[b[:4] for b in p.get_text('blocks') if b[0]<0 or b[1]<0 or b[2]>613 or b[3]>793]
  assert not violations,(i,violations)
  p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(render/f'pagina_{i:02d}.png')
  checks.append({'page':i,'text_chars':len(text),'bounds_ok':True})
 from PIL import Image
 cols=4;rows_n=(total+cols-1)//cols
 sheet=Image.new('RGB',(cols*306,rows_n*420),'#dfe8e3')
 for i in range(total):
  img=Image.open(render/f'pagina_{i+1:02d}.png');img.thumbnail((296,395));sheet.paste(img,((i%cols)*306+5,(i//cols)*420+20))
 sheet.save(render/'contacto.png')
 (HERE/'verificacion.json').write_text(json.dumps({'pages':len(doc),'structure':'8 secciones','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'checks':checks,'model_rerun':False,'visual_review':'Render generado; revisión visual separada de las comprobaciones de texto y límites','scenario_source':'entrega/caso_municipal.json','metrics_table_present':True},indent=2),encoding='utf-8')
 print(f'{total} páginas generadas, texto y geometría verificados:',pdf)
if __name__=='__main__':main()

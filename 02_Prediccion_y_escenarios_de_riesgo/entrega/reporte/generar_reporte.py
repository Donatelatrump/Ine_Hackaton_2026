"""Reporte de 12 páginas; fuente MD, PDF y render/QA reproducibles. Python 3.10+."""
from pathlib import Path
import sys, json, hashlib, html
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.packages'))
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
ROOT=HERE.parents[1]
M=json.loads((ROOT/'modelado/salidas/metricas.json').read_text(encoding='utf-8'))
PAGES=[
('UMBRAL','Una decisión municipal revisable',[
('Reporte metodológico y preventivo | Track 2', 'Versión técnica para revisión, 5 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios: 2009-2024. La propuesta combina una referencia sencilla, un modelo regularizado, calidad de datos visible y escenarios sujetos a capacidad.'),
('La decisión que organiza el atlas','Si un área de educación cívica dispone de capacidad para atender N municipios, Umbral permite revisar cuáles aparecen primero, qué antecedentes sustentan su posición y qué alcance y respuesta serían necesarios bajo una hipótesis de intervención. La lista es un insumo para deliberación institucional; la prioridad automática no sustituye diagnóstico local.'),
('Hallazgo central','Ridge reduce el error en el corte 2021, utilizado para selección, y empeora frente a persistencia en 2024. El resultado adverso forma parte de la evidencia. La utilidad defendible está en hacer revisable la decisión territorial, mostrar su sensibilidad y registrar supuestos, sin prometer superioridad predictiva consistente ni impacto causal.'),
('Ruta de lectura','Páginas 2-3: fuentes, calidad y unidad de análisis. Páginas 4-6: modelo, resultados y análisis posteriores. Páginas 7-8: semáforo, estabilidad y escenario. Páginas 9-10: acciones preventivas y piloto. Páginas 11-12: operación, límites y reproducibilidad.'),
('Equipo y estado de la propuesta','Tecnocalidos. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Este documento desarrolla el reporte de 10-15 cuartillas solicitado para el reto 2. Los formatos de cartas no equivalen a firmas; registro y envío oficial no están acreditados en este trabajo. El paquete técnico requiere revisión humana antes de su presentación formal.')]),
('01 / PROBLEMA','Priorizar exige definir el objetivo',[
('Alineación con el reto','La convocatoria pide un modelo simple de riesgo con antecedentes y variables sociodemográficas, escenarios sin intervención y con intervención hipotética, clasificación territorial comprensible y recomendaciones preventivas. El reporte y el mapa ejecutable con base anonimizada son entregables específicos. Estas exigencias se verificaron en las páginas 3-5 del PDF oficial [1].'),
('Tres preguntas distintas','La tasa estimada identifica territorios con mayor proporción de abstención. El volumen estimado aproxima cuántas abstenciones corresponderían a esa tasa sobre la población observable de referencia. El deterioro compara la estimación con la última elección del mismo tipo. Una localidad pequeña con tasa alta puede no encabezar el volumen; ninguna lista es neutral respecto al objetivo.'),
('Unidad y horizonte','La unidad es municipio-año identificado por clave INE, preservada como texto. Para 2027 se toma 2021 como último antecedente del mismo tipo y 2024 como último proceso disponible. La proyección es exploratoria y municipal: no permite afirmar comportamientos individuales ni producir una asignación distrital que la base no contiene.'),
('Capacidad como restricción explícita','N expresa municipios revisables o atendibles, no presupuesto monetario. El ejemplo inicial de 50 municipios es una decisión del prototipo y puede cambiar. Cada ejecución debe registrar método, umbral NS, filtro territorial, objetivo de prioridad, capacidad, alcance y respuesta; cambiar esos valores altera la decisión y exige volver a revisarla.'),
('Resultado institucional esperado','El producto propone una mesa de revisión: evidencia histórica, calidad, posiciones bajo alternativas, acción propuesta y factibilidad. La institución debe confirmar responsables, recursos y pertinencia territorial. No se atribuye respaldo institucional a las recomendaciones ni se asegura que su implementación aumente la participación.')]),
('02 / FUENTES','De conteos a una base comparable',[
('Serie histórica y trazabilidad','La serie principal procede de los Conteos Censales de Participación Ciudadana del INE [2], para seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y 2024. Los insumos de prisión preventiva y voto anticipado se conservan separados y no se incorporan automáticamente al histórico municipal ordinario.'),
('Auditoría realizada','El procesamiento principal comprende 54,872,712 filas de 192 CSV y genera 14,779 registros municipio-año y 2,477 claves históricas. Se revisaron integridad CRC, duplicados y reconciliación de conteos. Estas comprobaciones sustentan consistencia de archivos y sumas; no resuelven cambios de límites ni equivalencia de población a lo largo del tiempo.'),
('Definiciones que evitan confundir desconocimiento con abstención','SV cuenta participación registrada; NV cuenta no participación; NS indica participación no especificada. LN = SV + NV + NS. La abstención observable es 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. Se suman conteos antes de calcular tasas, evitando promediar porcentajes de grupos con tamaños distintos.'),
('Calidad y exclusión','La regla principal exige NS ≤10% y tasas observables en los antecedentes más reciente y del mismo tipo. La evaluación exige también calidad del objetivo histórico. En 2027 hay 1,783 estimaciones y 694 municipios sin estimación, sobre 2,477 claves. El estado sin datos se muestra gris y con motivo de exclusión; no recibe riesgo cero.'),
('Cartografía y sociodemografía','Los polígonos INE sirven de referencia visual de mayo de 2024 [3]. Catálogo de claves constante y límites constantes son propiedades distintas: falta armonización histórica. Se excluyen edades superiores a 120 al construir proporciones etarias, conservando conteos originales. Sexo, escolaridad y variables externas no verificadas no forman parte del predictor actual.')]),
('03 / MÉTODO','Referencia simple y ajuste regularizado',[
('Persistencia del mismo tipo','La referencia predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye silenciosamente por otro tipo electoral. Esta referencia es interpretable y constituye una exigencia mínima para valorar la complejidad adicional.'),
('Diez características agregadas','Se usan abstención del mismo tipo, abstención del último proceso, su diferencia, logaritmo de LN, proporción de 18-29 años, proporción de 60 años y más sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo electoral. LN conserva su papel de característica histórica; su uso como predictor no cambia el denominador observable de tasas, escenarios y ponderación del error.'),
('Construcción del candidato','StandardScaler y Ridge estiman el residual respecto de persistencia. La predicción suma referencia y residual y se trunca a [0,100]. Alpha=10 permanece congelado. Cada ejemplo utiliza características anteriores al objetivo y el escalador se ajusta con entrenamiento. Las contribuciones del modelo son algebraicas, no causas individuales o efectos de una política.'),
('Cortes temporales','Para evaluar 2021 se entrena con etiquetas 2015 y 2018; para 2024, con 2015, 2018 y 2021. La proyección 2027 incorpora etiquetas 2015, 2018, 2021 y 2024. El volumen de registros no crea más ocasiones electorales: hay seis procesos y solo tres intermedias, una limitación de transferencia temporal.'),
('Selección congelada','La regla fijada para 2021 exige al menos 1% de mejora en MAE y ausencia de empeoramiento del MAE ponderado y precisión top50. Ridge cumple esa regla. 2021 es selección, no prueba independiente posterior a selección. Los nuevos análisis no se utilizan para reajustar alpha, cambiar retrospectivamente la regla o ocultar 2024.')]),
('04 / EVIDENCIA','La mejora no se transfiere de forma consistente',[
('Comparación temporal','La tabla usa las mismas cohortes para ambos métodos dentro de cada corte. MAE es error absoluto medio en puntos porcentuales. MAE ponderado utiliza SV+NV del objetivo histórico, corrigiendo referencias narrativas previas a LN. Top50 cuenta coincidencias entre los 50 valores predichos más altos y los 50 observados más altos dentro de la cohorte evaluable.'),
('TABLE_METRICS',''),
('Lectura del resultado','En 2021 el MAE baja aproximadamente 23.9% y top50 pasa de 16 a 19 coincidencias. Eso deja 31 municipios del top observado fuera de la lista Ridge. En 2024 el MAE sube aproximadamente 52.2%, el ponderado empeora y ambos métodos recuperan 27/50. La coincidencia del ranking no compensa automáticamente el deterioro en tasas.'),
('Qué sostiene esta evidencia','Ridge puede conservarse como alternativa exploratoria conforme a la selección original, con persistencia visible. No hay evidencia de ganador universal. 2024 es presidencial y no valida directamente una elección intermedia de 2027. El desempeño es condicional a municipios con antecedentes y objetivos de calidad suficiente, no al universo nacional.'),
('Comparar sin cambiar la pregunta','Las métricas responden preguntas complementarias: precisión de tasas, error sobre población observable y recuperación de prioridades. Una mejora en una no acredita mejora en todas. No se transforma el error retrospectivo en probabilidad de abstención futura; tampoco se usan los resultados para inferir eficacia de una intervención.')]),
('05 / ANÁLISIS POSTERIORES','Orden, tercio alto y tamaño municipal',[
('Un análisis posterior identificado','Las ampliaciones se definen después del experimento original y antes de calcularlas. Describen utilidad operativa y heterogeneidad del error, con modelo, alpha y selección congelados. No son una prueba independiente del diseño inicial.'),
('Ordenamiento: Spearman','Correlación entre rangos observados y predichos, con rangos promedio en empates. Resume concordancia global de orden. Puede coexistir con fallos en los primeros N; se conserva top50 y revisión de listas específicas.'),
('Tercio alto con umbral aprendido','El percentil 2/3 se aprende con etiquetas de entrenamiento y se congela para evaluar ambos métodos. Precisión: fracción de clasificados altos realmente altos. Recobrado: fracción de altos observados recuperada. Umbrales: 47.814% en 2021 y 47.726% en 2024; no se redefine el umbral con el objetivo de prueba.'),
('Error por tamaño','Percentil 90 del error absoluto por denominador observable previo: <10 mil, 10 mil a <100 mil y ≥100 mil. Cada banda informa n. Describe heterogeneidad por escala; no es intervalo calibrado para 2027.'),
('Resultados complementarios','ADD_RESULTS'),
('Lectura conjunta','NS 5, 10 y 20 alteran las cohortes: no comparan idénticas muestras. La exclusión por calidad exige diagnóstico de datos. Estas métricas no autorizan asignación definitiva de recursos.')]),
('06 / SEMÁFORO','Nivel relativo y estabilidad de la selección',[
('Clasificación interpretable','Bajo, medio y alto corresponden a tercios relativos de estimaciones nacionales válidas. Alto identifica el tercio superior de tasas estimadas; no significa una probabilidad calibrada de deterioro. Gris significa que la información no permite estimación. Los umbrales base se mantienen fijos al comparar Base, Con intervención y cambio, para que el color no se redefina entre escenarios.'),
('Seis variantes, una frecuencia descriptiva','Se combinan persistencia y Ridge con límites NS de 5, 10 y 20%. Los entrenamientos siguen el procedimiento original. Para el N, filtro y criterio activos se cuenta cuántas veces cada municipio entra en la selección entre las seis variantes. Una variante no elegible cuenta como no seleccionada; la elegibilidad se informa por separado.'),
('Cómo usar la estabilidad','Entrar en seis de seis variantes define un núcleo robusto respecto a esas alternativas, no a todos los modelos posibles. Tres de seis indica dependencia de decisiones metodológicas. Cero de seis puede reflejar calidad insuficiente y no necesariamente baja tasa. La frecuencia no es probabilidad, confianza calibrada ni garantía de permanecer prioritario en 2027.'),
('Incertidumbre histórica y territorial','El rango técnico estimación ±21.05 pp conserva el p90 retrospectivo de Ridge en 2021, truncado a [0,100]. Es ilustrativo y amplio; no garantiza cobertura prospectiva de 90%. Se da mayor saliencia a estabilidad de selección y calidad. El catálogo territorial es un indicador separado: no acredita límites históricos equivalentes.'),
('Revisión de lentes','Tasa, volumen estimado sobre observados y deterioro respecto del último proceso del mismo tipo responden objetivos distintos. La concordancia entre listas ayuda a detectar municipios sensibles al criterio. La revisión debe registrar qué objetivo se eligió y por qué: una lista estable bajo tasa puede cambiar al priorizar volumen o deterioro.')]),
('07 / ESCENARIOS','Población observable y supuestos explícitos',[
('Base corregida','Para cada municipio O = SV2024 + NV2024. O limita cobertura, es el denominador de la reducción de tasa y pondera la agregación. NS se informa aparte y no se incluye como población alcanzable dentro de esta simulación. O es una referencia histórica observable; no es población proyectada de 2027. Nuevos datos deben aportar O, sin reemplazo silencioso por LN.'),
('Fórmula operativa','Sea a la tasa estimada (%), A el alcance supuesto y r la respuesta supuesta (%). Alcance efectivo E = mínimo(A,O). Participación adicional hipotética H = E × a/100 × r/100. Tasa con intervención = a - 100 × H/O. La tasa agregada se pondera por O sobre los mismos municipios seleccionados. Respuesta cero conserva la base.'),
('Ejemplo hipotético, no resultado medido','Si O=20,000, a=60%, A=1,000 y r=10%, E=1,000 y H=60 personas hipotéticas. La tasa sería 59.7%, una reducción de 0.3 pp. El ejemplo solo explica unidades y fórmula; no es un municipio real ni una estimación causal. El mecanismo supone que las personas alcanzadas presentan la tasa base y que la respuesta convierte una fracción de abstenciones.'),
('Inversión para evaluar factibilidad','Para bajar a un umbral t, se requiere H = O × (a-t)/100 cuando a>t. Con r positivo y a positivo, E requerido = O × (a-t)/(a × r/100). Si excede O o el alcance disponible, el objetivo es inviable bajo esos límites. Respuesta cero, denominador ausente o capacidad nula se tratan explícitamente, evitando divisiones inválidas.'),
('Comparación y recursos','Base, Con intervención y cambio permiten inspeccionar el mismo conjunto y umbrales. Personas alcanzadas son una unidad de recurso, no costo monetario ni electores adicionales garantizados. El plan exportado debe registrar supuestos y factibilidad. El escenario no estima efectos causales, movilización individual ni cambios en el tamaño del electorado.')]),
('08 / PREVENCIÓN','Fichas ligadas a condiciones observables',[
('Ficha A | Persistencia alta','Condición: tasa histórica y prioridad actual altas con datos válidos. Acción: sesiones neutrales de información sobre el proceso y rutas institucionales de consulta. Responsable propuesto: área de educación cívica y enlace local, sujetos a confirmación. Cobertura: municipios seleccionados y alcance aprobado. Recurso: personas alcanzadas, sesiones y horas de facilitación. Medición: comprensión antes/después y asistencia agregada. Hipótesis: reducir barreras informativas podría favorecer participación; el modelo no demuestra ese mecanismo.'),
('Ficha B | Deterioro respecto al mismo tipo','Condición: estimación mayor que el antecedente comparable y señal persistente al variar método. Acción: diagnóstico local previo y revisión de información accesible sobre fechas, ubicación y procedimientos. Responsable propuesto: coordinación territorial y educación cívica. Cobertura: conjunto elegible por deterioro, con alcance limitado por O. Recurso: consultas atendidas y personas informadas. Medición: consultas resueltas, comprensión y participación agregada futura. Hipótesis: una brecha informativa explica parte del deterioro; debe comprobarse antes de ampliar.'),
('Ficha C | Barreras de acceso por verificar','Condición: composición agregada rural o etaria relevante, sin inferir características de cada habitante. Acción: probar formatos accesibles y puntos presenciales de información tras consulta local. Responsable propuesto: enlace local y equipo de accesibilidad. Cobertura: puntos confirmados y alcance medible. Recurso: personas atendidas, materiales y horas. Medición: acceso, comprensión y satisfacción agregada. Hipótesis: adecuar el formato mejora alcance; no atribuir abstención a edad o ruralidad como causas.'),
('Ficha D | Información insuficiente','Condición: NS alto, historial incompleto o duda territorial. Acción: revisar fuente, clave y agregación antes de priorizar una intervención. Responsable propuesto: equipo de datos con enlace territorial. Cobertura: municipios excluidos y discrepancias detectadas. Recurso: registros revisados y horas de validación. Medición: casos resueltos, cobertura recuperada y motivos documentados. Hipótesis: mejor información reduce decisiones erróneas; no se interpreta gris como baja necesidad.'),
('Asignación y registro','Las fichas son propuestas de trabajo, no programas aprobados. Cada responsable debe validar pertinencia, lenguaje neutral, cobertura real y recursos disponibles. El registro operativo une condición, acción, encargado confirmado, calendario, alcance y medición. La respuesta del simulador se etiqueta como hipótesis, sin convertirla en compromiso de resultados.')]),
('09 / PILOTO','Aprender antes de ampliar una intervención',[
('Población y acuerdo previo','Se propone un piloto entre municipios elegibles alrededor del corte de capacidad, definido antes de asignar acciones. La cercanía del score no acredita equivalencia entre territorios ni causalidad. Se requiere acuerdo institucional previo y, cuando corresponda, consentimiento de participantes antes de aleatorizar. Ninguna actividad individual se desprende automáticamente de los datos agregados.'),
('Asignación aleatoria y balance','Dentro del conjunto acordado, asignar intervención y comparación mediante sorteo reproducible. Usar bloques o estratos definidos previamente por entidad, tamaño observable, tasa histórica y calidad; comprobar balance y reportar desequilibrios. Establecer criterios de inclusión, tamaño factible, calendario y regla de análisis antes de observar resultados. No seleccionar comparadores porque produzcan un efecto favorable.'),
('Resultado primario y proceso','Definir una medida primaria de comprensión o alcance efectivo para un piloto corto; la participación agregada futura exige un proceso electoral y comparabilidad territorial. Registrar implementación, personas alcanzadas, intensidad y eventos externos. Mantener costos de operación como medición futura, sin inventar cifras. Si la asignación es municipal, las unidades de inferencia deben respetar esa agrupación.'),
('Interpretación causal limitada','Una diferencia entre escenarios calculados no es impacto. Un piloto aleatorio bien ejecutado permitiría estimar el efecto de ofrecer la acción en su conjunto elegible, con incertidumbre y posibles problemas de contaminación o incumplimiento. Analizar por asignación original y describir desvíos. El resultado no se generaliza automáticamente a municipios excluidos, otros años o acciones distintas.'),
('Condiciones de pausa y ampliación','Pausar ante barreras de acceso, implementación insuficiente, reclamos o datos no comparables. Ampliar solo tras revisar ejecución, balance, efecto e incertidumbre y capacidad institucional. La medición puede concluir que la intervención no funciona. El piloto busca aprender y ajustar operación; no garantiza una reducción de abstención ni transforma el score en diagnóstico causal.')]),
('10 / OPERACIÓN','Una revisión territorial con evidencia visible',[
('Flujo propuesto','Primero definir objetivo, capacidad y territorio. Después revisar calidad y catálogo, comparar persistencia y Ridge, inspeccionar estabilidad bajo seis variantes y confirmar los municipios con conocimiento local. Finalmente seleccionar fichas, registrar responsables y recursos, formular escenario y exportar el plan. La decisión institucional debe conservar una justificación para aceptar o desplazar prioridades.'),
('Vista por entidad','La revisión por entidad permite distribuir atención y leer cobertura de municipios estimables y excluidos. No se inventa correspondencia distrital ausente. Las claves constituyen la unión territorial; nombres sirven para lectura y requieren revisión cuando cambian. Un catálogo constante es una señal conservadora y no una certificación de comparabilidad de límites.'),
('Límites que afectan uso','La proyección tiene escasa profundidad temporal, resultado adverso en 2024 y selección por calidad que puede excluir zonas con necesidades altas. El agregado municipal oculta heterogeneidad interna. La intervención usa una respuesta no estimada y población observable histórica. Estas limitaciones deben acompañar el plan, incluso si una lista es estable bajo las seis variantes.'),
('Qué verifican las pruebas','Los controles de software pueden verificar fórmulas, filtros, respuesta cero, estado gris, denominador obligatorio, frecuencia y exportación consistente. No prueban precisión futura, límites históricos armonizados o eficacia preventiva. El mapa local debe abrirse sin depender de servicios remotos y conservar datos incrustados para la revisión del jurado.'),
('Responsabilidad y seguimiento','El área usuaria confirma responsables y alcance; el equipo técnico conserva versión de insumos, parámetros y plan exportado. Se recomienda revisar incidencias, cambios territoriales y fuentes antes de cada uso. No se utiliza información personal ni se prescribe persuasión partidista. La finalidad es educación cívica neutral y planeación revisable con información agregada.')]),
('11 / REPRODUCIBILIDAD','Fuentes, archivos y cierre administrativo',[
('Evidencia local para revisar cifras','modelado/salidas/metricas.json conserva métricas y metadatos; backtest_predicciones.csv permite reconstruir errores y rankings; evaluacion_adicional.json documenta análisis posteriores cuando está disponible. La base municipios_historico_con_calidad.csv sustenta conteos. ejecutar.py fija cortes, referencia y Ridge; el código de ampliación conserva la separación entre experimento original y análisis posteriores.'),
('Regeneración del documento','Ejecutar python entrega/reporte/generar_reporte.py desde el directorio del track o mediante ruta completa. Requiere reportlab, pymupdf y pypdf; instalar en entrega/reporte/.packages con pip --target si faltan. El script lee métricas, produce este PDF, fuente Markdown y renders, y verifica 12 páginas, texto extraíble y límites geométricos. La revisión visual sigue siendo necesaria.'),
('Referencias oficiales','[1] INE, Convocatoria Hackea la participación, 2026. Página 3: reto 2; página 4: reporte de 10-15 cuartillas, mapa y entregables generales; página 5: envío y evaluación. https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf\n[2] INE, Conteos Censales de Participación Ciudadana 2009-2024. https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/\n[3] INE, mapas y cartografía consultados como referencia visual. https://pautas.ine.mx/transparencia/mapas/index_2025.html'),
('Entrega técnica y requisitos humanos','La convocatoria requiere presentación de máximo 10 diapositivas, código o repositorio cuando corresponda y cartas firmadas por todas las personas integrantes. El ZIP debe identificarse por equipo y eje. Este reporte no acredita registro, firmas, elegibilidad de integrantes o envío. Esos actos requieren a las personas participantes; la versión técnica no se presenta como entrega final certificada.'),
('Criterio de uso responsable','La evidencia disponible permite explorar prioridades y documentar decisiones. Una adopción institucional exige revisión territorial, contraste de calidad y un piloto evaluable. Mantener la referencia sencilla, el deterioro de 2024 y las hipótesis visibles es parte del método, no una nota secundaria. El resultado puede cambiar con nuevas fuentes y futuras elecciones.')])]

def add_results():
 p=ROOT/'modelado/salidas/evaluacion_adicional.json'
 if not p.exists(): return 'Las definiciones de esta página constituyen el protocolo posterior. Las cifras completas se consultan en evaluacion_adicional.json al generarse; no se imputan resultados ausentes. La tabla del corte original permanece como evidencia medida disponible.'
 data=json.loads(p.read_text(encoding='utf-8'))
 parts=[]
 for yr in ['2021','2024']:
  for method in ['persistencia','ridge']:
   a=data['cuts'][yr][method]
   parts.append(f"{yr} {method}: Spearman {a['spearman']:.3f}; precisión alta {a['precision_rojo']*100:.1f}%; recobrado {a['recobrado_rojo']*100:.1f}%.")
 parts.append('P90 de error Ridge por tamaño (<10 mil / 10-100 mil / ≥100 mil):')
 for yr in ['2021','2024']:
  a=data['error_by_size'][yr+'_ridge']
  parts.append(yr+': '+' / '.join(f"{a[k]['p90_abs_error_pp']:.2f} pp (n={a[k]['n']})" for k in ['menos_10000','10000_99999','100000_mas'])+'.')
 parts.append('En 2024 la alta precisión de Ridge se acompaña de bajo recobrado: identifica pocos altos. No corrige su deterioro en MAE.')
 return '\n'.join(parts)

def main():
 for f,name in [('arial.ttf','Arial'),('arialbd.ttf','Arial-Bold')]:
  p=Path('C:/Windows/Fonts')/f
  if p.exists():pdfmetrics.registerFont(TTFont(name,str(p)))
 regular='Arial' if 'Arial' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
 bold='Arial-Bold' if 'Arial-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
 style=ParagraphStyle('body',fontName=regular,fontSize=10.7,leading=16.3,textColor=HexColor('#253b3b'),spaceAfter=9)
 hstyle=ParagraphStyle('head',fontName=bold,fontSize=12,leading=17,textColor=HexColor('#12645e'))
 pdf=HERE/'Umbral_reporte_metodologico_preventivo.pdf'
 c=canvas.Canvas(str(pdf),pagesize=(612,792));c.setTitle('Umbral | Reporte metodológico y preventivo')
 md=['# Umbral: reporte metodológico y preventivo','Versión técnica para revisión | 5 de octubre de 2026']
 for i,(label,title,sections) in enumerate(PAGES,1):
  c.setFillColor(HexColor('#edf4f0'));c.rect(0,692,612,100,fill=1,stroke=0)
  c.setFillColor(HexColor('#12645e'));c.setFont(bold,10);c.drawString(48,753,label)
  c.setFont(bold,22);c.drawString(48,715,title)
  y=670;md+=['',f'## Página {i}: {title}']
  for heading,body in sections:
   if heading=='TABLE_METRICS':
    rows=[['Corte / método','n','MAE pp','Pond. pp','Top50']]
    for yr in ['2021','2024']:
     for name in ['persistencia','ridge']:
      a=M['checks'][yr][name];rows.append([yr+' / '+('Referencia' if name=='persistencia' else 'Ridge'),str(a['n']),f"{a['mae']:.3f}",f"{a['mae_ponderado']:.3f}",f"{round(a['precision_top']*50)}/50"])
    t=Table(rows,colWidths=[185,50,75,75,65]);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),regular),('FONTSIZE',(0,0),(-1,-1),10),('BACKGROUND',(0,0),(-1,0),HexColor('#12645e')),('TEXTCOLOR',(0,0),(-1,0),HexColor('#ffffff')),('BACKGROUND',(0,1),(-1,-1),HexColor('#edf4f0')),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9)]))
    w,h=t.wrap(516,y);t.drawOn(c,48,y-h);y-=h+17
    md+=['','| Corte / método | n | MAE pp | Ponderado pp | Top50 |','|---|---:|---:|---:|---:|']+['| '+' | '.join(r)+' |' for r in rows[1:]];continue
   if body=='ADD_RESULTS':body=add_results()
   md+=['',f'### {heading}',body]
   for txt,st in [(heading,hstyle),(body,style)]:
    p=Paragraph(html.escape(txt).replace('\n','<br/>'),st);w,h=p.wrap(516,700);y-=h;p.drawOn(c,48,y);y-=7
   y-=7
  if y<50:raise RuntimeError(f'Page {i} overflows: {y}')
  c.setStrokeColor(HexColor('#c4d8cf'));c.line(48,42,564,42);c.setFillColor(HexColor('#526a62'));c.setFont(regular,8);c.drawString(48,27,'UMBRAL  /  TRACK 2  /  VERSIÓN TÉCNICA PARA REVISIÓN');c.drawRightString(564,27,f'{i:02d} / 12');c.showPage()
 c.save();(HERE/'Umbral_reporte_fuente.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 doc=fitz.open(pdf);assert len(doc)==12
 render=HERE/'revision_visual';render.mkdir(exist_ok=True)
 checks=[]
 for i,p in enumerate(doc,1):
  text=p.get_text();assert len(text)>1200,(i,len(text))
  violations=[b[:4] for b in p.get_text('blocks') if b[0]<0 or b[1]<0 or b[2]>613 or b[3]>793]
  assert not violations,(i,violations)
  p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(render/f'pagina_{i:02d}.png')
  checks.append({'page':i,'text_chars':len(text),'bounds_ok':True})
 from PIL import Image,ImageOps,ImageDraw
 sheet=Image.new('RGB',(4*306,3*420),'#dfe8e3')
 for i in range(12):
  img=Image.open(render/f'pagina_{i+1:02d}.png');img.thumbnail((296,395));sheet.paste(img,((i%4)*306+5,(i//4)*420+20))
 sheet.save(render/'contacto.png')
 (HERE/'verificacion.json').write_text(json.dumps({'pages':len(doc),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'checks':checks},indent=2),encoding='utf-8')
 print('12 páginas generadas, texto y geometría verificados:',pdf)
if __name__=='__main__':main()

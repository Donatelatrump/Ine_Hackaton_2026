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
sys.path.insert(0,str(HERE/'.packages'))
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
ROOT=HERE.parents[1]
FIG=ROOT/'demo/verificacion'
M=json.loads((ROOT/'modelado/salidas/metricas.json').read_text(encoding='utf-8'))
PAGES=[
('UMBRAL','Resumen ejecutivo',[
('Reporte metodológico y preventivo · Reto 2','Tecnocalidos. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Versión técnica para revisión, 6 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios 2009-2024. Presupuesto de 15 páginas; este documento usa 14.'),
('Resumen ejecutivo','Umbral apoya una decisión acotada: con capacidad para atender N municipios, ¿cuáles revisar primero, con qué respaldo y qué puede hacerse después? El método compara una referencia sencilla (última elección del mismo tipo) con un ajuste Ridge regularizado, con calidad de datos visible y análisis posteriores congelados. Hallazgo principal: Ridge mejora el error en 2021 y empeora frente a la referencia en 2024; no se declara ganador. La propuesta preventiva son fichas revisables con acción, responsable, cobertura y medición, más un piloto aleatorio propuesto alrededor del corte de capacidad. El alcance de uso es la deliberación institucional; no es asignación automática de recursos.'),
('Qué es y qué no es','Es una herramienta de priorización auditable y un registro explícito de supuestos. No es un predictor validado de 2027, no es un asignador automático de recursos y no demuestra efectos causales de una intervención.')]),
('01 / PROBLEMA Y DECISIÓN','Para qué sirve y para quién',[
('Pregunta operativa','Si un área de educación cívica dispone de capacidad para atender N municipios, ¿cuáles conviene revisar primero, qué antecedentes respaldan su prioridad y cómo cambia un escenario al variar alcance y respuesta supuesta?'),
('Criterio de prioridad y selector','La prioridad principal es la tasa de abstención estimada, no el número absoluto ni el deterioro. El prototipo permite elegir entre tres lentes que responden preguntas distintas: tasa (proporción estimada), volumen sobre la población observable (cuántas abstenciones) y deterioro frente a la última elección del mismo tipo. Cambiar el lente cambia la lista; la elección responde al objetivo institucional declarado, no a un valor universal.'),
('Persona usuaria y flujo de uso','La persona usuaria es un área de educación cívica o planeación territorial que define territorio y capacidad. Flujo en cuatro pasos: 1) definir territorio, capacidad y criterio; 2) revisar mapa y lista priorizada; 3) inspeccionar calidad, estabilidad y antecedentes; 4) descargar el plan con supuestos y escenario.')]),
('02 / DATOS Y VARIABLES (1/2)','De conteos a una base comparable',[
('Fuente y volumen auditado','Conteos Censales de Participación Ciudadana del INE [2], seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y 2024, agregados y disociados, sin datos personales. Se auditaron 54,872,712 filas de 192 CSV con integridad CRC, duplicados y reconciliación de conteos, y se generaron 14,779 registros municipio-año y 2,477 claves. Prisión preventiva y voto anticipado se conservan como fuentes separadas. Fuente: auditoria/ y datos_preparados/.'),
('Definiciones','SV: participación registrada. NV: no participación. NS: participación no especificada. LN = SV + NV + NS. Abstención observable (%) = 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. La suma de conteos precede al cálculo de porcentajes: una tasa vacía es denominador cero, no abstención de cero.'),
('Reglas de calidad y cobertura','Se exige NS ≤10% en el antecedente más reciente y en el del mismo tipo; la evaluación exige además objetivo observable con NS ≤10%. En 2027 hay 1,783 municipios con estimación y 694 sin estimación sobre 2,477 claves. La exclusión por calidad puede apartar zonas con necesidad alta: es un sesgo de cohorte que debe declararse. Fuente: modelado/salidas/metricas.json.'),
('Límite territorial','Una clave municipal constante no prueba límites ni población constantes. No hay armonización histórica de fronteras y los conteos no se redistribuyeron a los límites de 2024. Se excluyen edades mayores de 120 al construir proporciones etarias, conservando los conteos originales.')]),
('02 / DATOS Y VARIABLES (2/2)','Variables usadas, omitidas y trazabilidad',[
('TABLE_VARIABLES',''),
('Variables omitidas y por qué','Sexo, escolaridad y variables externas no verificadas no forman parte del predictor. Sexo existe en la fuente y se usa solo en la capa explicativa posterior (sección de prevención); el modelo conserva variables agregadas verificables para reducir sobreajuste y fuga. La representación etaria es agregada; no se infieren características individuales.'),
('Trazabilidad','Cada cifra proviene de archivos citados en el pie de tabla o en el texto: datos_preparados/municipios_historico_con_calidad.csv, modelado/salidas/metricas.json, evaluacion_adicional.json y perfil_demografico.json. El diccionario de datos y las tablas largas viven en la base CSV y el repositorio, no en este PDF.')]),
('03 / MODELO (1/2)','Referencia simple y ajuste regularizado',[
('Referencia','Predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye por otro tipo electoral. Es interpretable y constituye la exigencia mínima que la complejidad debe superar.'),
('Ajuste Ridge','Ridge estima el residual respecto de la referencia con doce características agregadas, incluidas interacciones entre elección intermedia y las tasas históricas. StandardScaler y Ridge se ajustan solo con entrenamiento anterior a cada corte; alpha se elige por validación temporal expansiva; la predicción se limita a [0,100]. Se compara también un challenger ponderado por SV+NV.'),
('Flujo simple','Antecedentes observados con calidad verificada → Referencia del mismo tipo → Ajuste Ridge del residual → Estimación 2027 → Semáforo relativo, estabilidad y decisión con capacidad.')]),
('03 / MODELO (2/2)','Construcción, cortes y regla de selección',[
('Cortes temporales','Para evaluar 2021 se entrena con etiquetas 2015 y 2018; para 2024, con 2015, 2018 y 2021. La proyección 2027 incorpora 2015, 2018, 2021 y 2024. Cada ejemplo usa características anteriores a su año objetivo. Hay seis procesos y solo tres intermedias: el volumen de registros no crea más ocasiones electorales.'),
('Regla de selección','Fijada para 2021: adoptar Ridge solo si mejora el MAE al menos 1%, no empeora el MAE ponderado ni la precisión top50 y no aumenta la magnitud del sesgo más de 3 pp. Ridge cumple esa regla en 2021. El corte 2024 se conserva como comprobación y documenta transferencia desfavorable.'),
('2021 es selección, no prueba','2021 se usó para elegir; no es una prueba independiente posterior a la selección. Los análisis posteriores (rango, tamaño, estabilidad) tampoco reajustan el modelo: describen su comportamiento con parámetros congelados.')]),
('04 / EVIDENCIA Y LÍMITES (1/2)','La mejora no se transfiere de forma consistente',[
('Tabla de resultados','TABLE_METRICS'),
('Lectura honesta','En 2021 el MAE baja aproximadamente 23.9% y top50 pasa de 16 a 19 coincidencias; eso deja 31 municipios del top observado fuera de la lista Ridge. En 2024 el MAE sube aproximadamente 52.2%, el ponderado empeora y ambos métodos recuperan 27/50. No hay ganador universal: Ridge se conserva como alternativa exploratoria con la referencia visible.'),
('Métricas posteriores congeladas','Se definieron después del experimento original y antes de calcularlas: Spearman; precisión y recobrado del tercio alto con umbral aprendido en entrenamiento y congelado por corte; error P90 por tamaño municipal. En 2024 la precisión roja alta de Ridge convive con recobrado bajo: identifica pocos altos y no corrige su deterioro en MAE. Fuente: modelado/salidas/evaluacion_adicional.json.')]),
('04 / EVIDENCIA Y LÍMITES (2/2)','Estabilidad, incertidumbre y límites',[
('Estabilidad del top N','Se combinan dos métodos × umbrales NS 5/10/20 para seis variantes. En seis de seis, un municipio forma parte del núcleo robusto; entre una y cinco, de la zona de revisión; cero, queda fuera. La frecuencia es descriptiva, no probabilidad calibrada. Las variantes comparten datos y pueden equivocarse juntas. En capacidad humana se usa N municipal equivalente, sin recalcular el presupuesto por variante; filtro mínimo con N previo al filtro y ficha/frontera con N final. Fuente: demo/decision.js y demo/aplicacion.js.'),
('Incertidumbre de prioridad, no de intervalo','La interfaz responde «si solo puedo intervenir N municipios, ¿puedo confiar en que este esté entre ellos?» comunicando esa frecuencia y el acuerdo de puesto entre referencia y Ridge. El rango ±20.61 pp (P90 retrospectivo de Ridge 2021, truncado a [0,100]) se conserva solo como error histórico, no como intervalo prospectivo.'),
('Error por tamaño y límites','El P90 del error por denominador observable previo (<10 mil, 10-100 mil, ≥100 mil) describe heterogeneidad por escala, no un intervalo para 2027. Límites: seis ocasiones electorales y tres intermedias; 2024 es presidencial y no valida 2027; sin causalidad; selección por calidad que puede excluir zonas con necesidad alta.')]),
('05 / SEMÁFORO','Clasificación territorial y estabilidad',[
('Tercios relativos','Bajo, medio y alto son tercios de las estimaciones nacionales válidas. Alto es el tercio superior de tasas estimadas; no es probabilidad calibrada de deterioro. Gris significa información insuficiente para estimar, se muestra con motivo de exclusión y nunca recibe riesgo cero.'),
('Eje de estabilidad','La calidad (NS), la estabilidad entre seis variantes y el acuerdo entre métodos se informan como dimensión separada del color, en la lista y en la ficha. Los umbrales base permanecen fijos al comparar escenarios para que el color no se redefina entre ellos.'),
('Sensibilidad de umbrales','Mover el corte cambia el número de municipios por nivel; el informe incluye variación por tamaño municipal y por umbral NS. Ejemplo: alternar el filtro de catálogo constante pasa de 1,144 a 1,783 estimaciones. Fuente: modelado/salidas/metricas.json.'),
('FIGURE_MAP_STATES','')]),
('06 / ESCENARIOS','Sin intervención y con intervención hipotética',[
('Fórmulas del escenario','O = SV2024 + NV2024 por municipio. Alcance efectivo E = mínimo(alcance supuesto, O). Participación adicional hipotética H = E × tasa/100 × respuesta/100. Tasa del escenario = tasa − 100 × H / O. La agregación se pondera por O sobre los mismos municipios seleccionados.'),
('Supuestos explícitos','Las personas alcanzadas presentan la tasa estimada; la respuesta es hipótesis del usuario; O es referencia histórica observable, no electorado de 2027. NS queda fuera del escenario. Respuesta cero conserva la base; entradas inválidas bloquean la exportación.'),
('FIGURE_TRIPLE',''),
('Escenario invertido y ejemplo','Para bajar de nivel, H = O × (tasa − umbral)/100 con tasa > umbral, y el alcance requerido = H / ((tasa/100) × (respuesta/100)). Si excede O o el alcance, el objetivo es inviable. Ejemplo trabajado con capacidad de 50 municipios: el efecto local por municipio es visible, mientras el efecto agregado es pequeño.')]),
('07 / PREVENCIÓN (1/3)','Tipologías observables y línea de acción',[
('Tipologías por perfil observable','Se derivan tipologías de información agregada, no de personas: territorio con menor proporción urbana; proporción joven 18-29 ≥25%; proporción 60+ ≥25%; y calidad insuficiente (NS alto o antecedentes incompletos). Cada tipología lleva una línea de acción: información electoral accesible, talleres en espacios educativos y comunitarios, material legible, o revisión de datos antes de priorizar.'),
('El perfil no decide, explica','La prioridad la fija el modelo; la tipología orienta a quién podría dirigirse una intervención. El perfil CCPC por edad, sexo y tipo de sección es una capa explicativa posterior que nunca alimenta al modelo y no implica causalidad; los grupos con muestra insuficiente se marcan como tales. Fuente: modelado/salidas/perfil_demografico.json.'),
('Mecanismo como hipótesis','La reducción de barreras informativas podría favorecer la participación; es una hipótesis a evaluar, no un hallazgo del modelo.')]),
('07 / PREVENCIÓN (2/3)','Ficha tipo y ejemplo completo',[
('Ficha tipo','Cada recomendación registra: condición observable, acción, responsable propuesto, cobertura, condiciones de aplicación, recurso (personas y horas), medición y mecanismo hipotético.'),
('Caso 23008: SOLIDARIDAD (catálogo histórico)','Con filtros nacionales, catálogo constante, tasa, Ridge y capacidad 50, ocupa el puesto 1; referencia, el 3. Estimación 62.11%; antecedente 2021: 66.30%; NS 2021/2024: 9.60%/2.28%. Estabilidad 4/6, elegible 4/6: queda en zona de revisión por NS 2021 >5%. Perfil joven 28.26% y urbano 91.02% de LN. Acción propuesta: talleres abiertos sobre requisitos y procedimiento. Responsable: educación cívica y junta local, por validar. Alcance supuesto 1,000, respuesta 25% y SV+NV 2024 de 255,362: H=155.27 hipotéticos, 62.11% a 62.05%; sigue alto. Validar sedes y capacidad; registrar alcance, horas y conocimiento previo/posterior. Efecto sobre participación requiere piloto aleatorio con protocolo y potencia previos. Caso ampliado: entrega/CASO_MUNICIPAL.md.'),
('El resto, en el CSV','La ficha completa de cada municipio seleccionado se exporta en el plan CSV; este PDF incluye un ejemplo representativo.')]),
('07 / PREVENCIÓN (3/3)','Priorización de recursos y diseño de evaluación',[
('Priorización de recursos','El plan ordena por capacidad, con el criterio elegido y la estabilidad mínima declarada. Comunica núcleo robusto y zona de revisión para no tratar la frontera como certeza. En modo de capacidad humana, el presupuesto se expresa en personas alcanzables y se agota por prioridad.'),
('Diseño de evaluación propuesto','Aleatorizar atención inmediata o diferida entre municipios cercanos al corte de capacidad, con balance por entidad, tamaño, calidad y contexto; indicadores de cobertura y comprensión; y regla de análisis fijada antes de observar resultados. La cercanía del score no acredita equivalencia ni causalidad.'),
('Vista operativa','El resumen por entidad apoya la distribución regional con la cobertura de municipios estimables y excluidos. No se inventa correspondencia distrital: la base no la contiene y no se certifica.')]),
('08 / VIABILIDAD','Qué se puede defender hoy y qué falta',[
('TABLE_VIABILITY',''),
('Riesgos de uso','Uso automático de la lista como asignación definitiva; lectura causal del escenario; y falacia ecológica al pasar del municipio a la persona. Se mitigan con revisión humana, etiquetando el escenario como hipótesis y sin inferir comportamiento individual del agregado.'),
('Reproducibilidad y cierre','Abrir el mapa con doble clic en demo/index.html (o servidor local); regenerar cifras con modelado/imprimir_cifras.py; el código, la demo y los insumos están en el repositorio y el paquete. La revisión visual comprueba estas 14 páginas. Umbral convierte la incertidumbre del modelo en diseño institucional: prioriza, muestra por qué y qué tan robusta es cada decisión, y propone cómo evaluar una acción. Se invita a pilotear alrededor del corte de capacidad antes de ampliar.')]),
]

VARIABLES=[['Variable','Uso y por qué'],
['Abstención del mismo tipo','Antecedente comparable; base de la referencia y de la estabilidad entre elecciones del mismo tipo.'],
['Abstención del último proceso','Señal más reciente del territorio.'],
['Diferencia último − mismo tipo','Capta deterioro o mejora reciente.'],
['log(LN)','Escala del padrón sin dominar el ajuste.'],
['Proporción 18-29','Composición joven agregada; patrón documentado de mayor abstención.'],
['Proporción 60+ (sin >120)','Composición de mayor edad; reduce valores extremos.'],
['Proporción urbana','Contexto territorial agregado.'],
['NS de ambos antecedentes','Calidad del dato como condición de inclusión.'],
['Tipo de elección (intermedia)','Distingue intermedias de presidenciales.']]

VIABILITY=[['Se puede defender hoy','Falta evidencia o validación'],
['Marco de decisión con capacidad y criterio explícitos','Aceptación institucional del flujo y de los responsables.'],
['Auditoría de datos y calidad visible','Armonización histórica de límites municipales.'],
['Comparación honesta con la referencia (2021 y 2024)','Validación prospectiva; 2024 adverso no se oculta.'],
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
 md=['# Umbral: reporte metodológico y preventivo','Versión técnica para revisión | 6 de octubre de 2026',f'Estructura de {total} páginas (8 secciones)']
 def paragraph(txt,st):
  nonlocal y
  p=Paragraph(html.escape(txt).replace('\n','<br/>'),st);w,h=p.wrap(516,700);y-=h;p.drawOn(c,48,y);y-=6
 def draw_table(rows,widths):
  nonlocal y
  t=Table(rows,colWidths=widths);t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),regular),('FONTSIZE',(0,0),(-1,-1),9),('LEADING',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),HexColor('#12645e')),('TEXTCOLOR',(0,0),(-1,0),HexColor('#ffffff')),('BACKGROUND',(0,1),(-1,-1),HexColor('#edf4f0')),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]))
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
   ps=[FIG/'mapa_base.png',FIG/'mapa_intervencion.png',FIG/'mapa_cambio.png']
   labels=['(a) Sin intervención','(b) Con intervención','(c) Δ cambio en pp']
   w=168;h=w*aspect(ps[0])
   for i,p in enumerate(ps):
    x=48+i*(w+6);c.drawImage(str(p),x,y-h,width=w,height=h,preserveAspectRatio=True,anchor='n')
    c.setFillColor(HexColor('#526a62'));c.setFont(regular,8);c.drawCentredString(x+w/2,y-h-10,labels[i])
   y-=h+16
   paragraph('Figura 2. Mismo conjunto y umbrales base fijos: sin intervención, con intervención y cambio hipotético. Ejemplo de la demo corregida.',note_style)
 for i,(label,title,sections) in enumerate(PAGES,1):
  c.setFillColor(HexColor('#edf4f0'));c.rect(0,692,612,100,fill=1,stroke=0)
  c.setFillColor(HexColor('#12645e'));c.setFont(bold,10);c.drawString(48,753,label)
  c.setFont(bold,21);c.drawString(48,715,title)
  y=670;md+=['',f'## Página {i}: {title}']
  for heading,body in sections:
   if heading=='TABLE_METRICS':
    rows=[['Corte / método','n','MAE pp','Pond. pp','Top50']]
    for yr in ['2021','2024']:
     for name in ['persistencia','ridge']:
      a=M['checks'][yr][name];rows.append([yr+' / '+('Referencia' if name=='persistencia' else 'Ridge'),str(a['n']),f"{a['mae']:.3f}",f"{a['mae_ponderado']:.3f}",f"{round(a['precision_top']*50)}/50"])
    draw_table(rows,[185,50,75,75,65]);md+=['','| '+' | '.join(rows[0])+' |','|'+'---|'*len(rows[0])]+['| '+' | '.join(r)+' |' for r in rows[1:]]
    paragraph('Fuente: modelado/salidas/metricas.json.',note_style);continue
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
 (HERE/'verificacion.json').write_text(json.dumps({'pages':len(doc),'structure':'8 secciones','pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'checks':checks},indent=2),encoding='utf-8')
 print(f'{total} páginas generadas, texto y geometría verificados:',pdf)
if __name__=='__main__':main()

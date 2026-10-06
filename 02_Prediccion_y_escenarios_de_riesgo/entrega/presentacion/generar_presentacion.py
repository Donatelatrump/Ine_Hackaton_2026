"""Umbral: PPTX editable y PDF con la misma composición. Python 3 + OOXML estándar/reportlab.
Ejecutar desde esta carpeta. Dependencias locales opcionales en .packages.
"""
from pathlib import Path
import sys, textwrap, json
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE/'.packages'),str(HERE.parent/'reporte'/'.packages')]
import zipfile, copy, xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

INK='15353B'; TEAL='10685F'; PAPER='F3F6F4'; MUTED='587177'; SAGE='E5EEEA'
CCPC='https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/'
CALL='https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf'
slides=[('UMBRAL',
  [('Atlas de decisión municipal', 28),
   ('Revisión territorial con evidencia, capacidad y supuestos visibles', 22),
   ('Tecnocalidos · Hackathon INE 2026 · Track 2', 18),
   ('Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum', 17),
   ('Versión técnica · 6 de octubre de 2026', 17)],
  'Datos agregados CCPC 2009–2024. Prototipo para revisión institucional.'),
 ('Territorio y cobertura total',
  [('Municipio, estado o país', 26),
   ('La persona usuaria elige territorio, acción con evidencia y cobertura total. SMS cuenta personas distintas previstas para '
    'envío. Llamada cuenta contactos efectivos.',
    21),
   ('Prioridad concentra por ranking. Proporcional reparte por SV+NV 2024 entre todos los elegibles, con redondeo por mayor '
    'resto y tope de población.',
    21),
   ('Estas reglas son decisiones de planeación propias.', 19)],
  'País: México, municipios con estimación incluidos. Los filtros y exclusiones delimitan el alcance.'),
 ('Cobertura y calidad visibles',
  [('1,783 con estimación', 36),
   ('694 sin estimación · 2,477 claves históricas', 24),
   ('Abstención observada = 100 × NV / (SV + NV)', 24),
   ('NS identifica participación no especificada. La regla principal exige NS ≤10% en ambos antecedentes relevantes.', 20),
   ('El catálogo constante orienta la revisión territorial. Falta comprobar equivalencia de límites históricos.', 20)],
  'Fuente: auditoría y base municipal del proyecto. CCPC: '
  'https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/'),
 ('La referencia también compite',
  [('Referencia: última elección del mismo tipo', 24),
   ('Para 2027 usa 2021. Ridge estima un ajuste con historia electoral, edad agregada, urbanización y calidad.', 22),
   ('Alpha = 10 permanece congelado. Cada corte aprende con resultados anteriores al año objetivo.', 22),
   ('2021 seleccionó el método. Ese corte no es una prueba independiente posterior a la selección.', 20)],
  'Fuente: modelado/METODOLOGIA.md y modelado/salidas/metricas.json. No hay ajuste para mejorar 2024.'),
 ('Ridge mejora en 2021 y empeora en 2024',
  [],
  'MAE en puntos porcentuales. Ponderación por SV+NV observado del objetivo. Top50 dentro de cada cohorte evaluable.'),
 ('Evidencia externa y escenario territorial',
  [('Acción y coeficiente publicado', 25),
   ('SMS Suecia: +0.30 pp ITT, intervalo 0.13–0.48. SMS EEUU: +0.25 pp ITT, intervalo 0.17–0.34. Llamada: +4.1 pp ATT, error '
    'estándar 1.7.',
    20),
   ('Votos adicionales hipotéticos = cobertura × coeficiente / 100, limitados por abstención esperada entre cubiertos. '
    'El coeficiente ya mide cambio en participación, sin otra tasa de respuesta.',
    21),
   ('La comparación conserva todo el territorio estimable, incluso municipios sin atención. Umbrales base fijos y ponderación '
    'SV+NV 2024.',
    20)],
  'DOI: 10.1017/S0007123424000504; 10.1007/s11109-026-10121-2; 10.1177/0956797609359326. Traslado a México: supuesto.'),
 ('Una ficha para revisar cada prioridad',
  [('¿Por qué este municipio?', 26),
   ('Puesto, antecedentes, calidad NS y acuerdo entre referencia y Ridge. Perfil CCPC por grupos como capa descriptiva separada.',
    21),
   ('Frecuencia entre seis variantes: dos métodos × NS 5/10/20. N equivale a municipios atendidos del plan actual.', 22),
   ('Compara rankings con N equivalente. No recalcula presupuesto ni reparto y no es probabilidad. El caso 23008 documenta '
    'por separado el ranking de referencia top50.',
    21)],
  'Frecuencia descriptiva. Las variantes comparten datos y pueden equivocarse juntas.'),
 ('Caso 23008: SMS con traslado hipotético',
  [('SOLIDARIDAD · catálogo histórico de Quintana Roo', 24),
   ('Puesto Ridge 1, referencia 3. Base 62.106806%. Estabilidad 4/6 del ranking de referencia top50. NS 2021: 9.60%, excluye '
    'umbral ≤5%.',
    20),
   ('1,000 personas distintas previstas para SMS Suecia: 3 votos adicionales hipotéticos, rango externo 1.3–4.8.', 23),
   ('Escenario 62.105631%. Reducción de 0.001175 pp. El efecto publicado proviene de Suecia y su traslado a México requiere '
    'evaluación.',
    21)],
  'Fuente: entrega/caso_municipal.json. SV+NV 2024: 255,362. SMS: Lindgren, Nyman y Oskarsson (2025), DOI '
  '10.1017/S0007123424000504.'),
 ('De la ficha a un plan verificable',
  [('Recursos, condiciones y medición', 25),
   ('Exportar territorio, acción y cita, cobertura total, distribución, supuestos y estabilidad del plan actual.', 21),
   ('Registrar alcance único agregado, horas y conocimiento previo/posterior. El perfil por edad describe grupos agregados y no '
    'demuestra barreras.',
    21),
   ('Validar límites, sedes y atribuciones. Un efecto sobre participación requiere evaluación comparativa y protocolo previo.',
    21)],
  'Caso completo: entrega/CASO_MUNICIPAL.md. Guion y demo de tres pasos: entrega/GUION_PRESENTACION.md.'),
 ('Siguiente decisión: un piloto acotado',
  [('Validación con el área usuaria', 26),
   ('Acordar objetivo de priorización, capacidad real y protocolo de revisión territorial. Elegir acciones con cobertura que '
    'pueda medirse.',
    22),
   ('Evaluación antes de ampliar', 26),
   ('Predefinir indicadores y asignación del piloto. Conservar la referencia y publicar resultados favorables y adversos.', 22),
   ('Equipo: Tecnocalidos. Firmas, registro y envío formal siguen pendientes.', 19)],
  '2024 es presidencial y no valida directamente 2027. No se promete superioridad predictiva o efectividad preventiva.')]

TEMPLATE=HERE/'plantilla_base.pptx'
if not TEMPLATE.exists(): TEMPLATE.write_bytes((HERE/'Umbral_presentacion.pptx').read_bytes())
with zipfile.ZipFile(TEMPLATE) as z: package={n:z.read(n) for n in z.namelist()}
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
for k,v in NS.items(): ET.register_namespace(k,v)
ET.register_namespace('r','http://schemas.openxmlformats.org/officeDocument/2006/relationships')
shape_template=ET.fromstring(package['ppt/slides/slide1.xml']).find('p:cSld/p:spTree/p:sp',NS)
def native_text(root,value,x,y,w,h,size,color,bold):
    shape=copy.deepcopy(shape_template)
    tree=root.find('p:cSld/p:spTree',NS)
    prop=shape.find('p:nvSpPr/p:cNvPr',NS); prop.set('id',str(len(tree)+1));prop.set('name','Texto editable')
    xfrm=shape.find('p:spPr/a:xfrm',NS)
    off=xfrm.find('a:off',NS); off.set('x',str(round(x*914400)));off.set('y',str(round(y*914400)))
    ext=xfrm.find('a:ext',NS);ext.set('cx',str(round(w*914400)));ext.set('cy',str(round(h*914400)))
    body=shape.find('p:txBody',NS)
    for el in list(body):
        if el.tag.endswith('}p'): body.remove(el)
    para=ET.SubElement(body,'{'+NS['a']+'}p');run=ET.SubElement(para,'{'+NS['a']+'}r')
    rp=ET.SubElement(run,'{'+NS['a']+'}rPr',{'sz':str(size*100),'b':'1' if bold else '0'})
    fill=ET.SubElement(rp,'{'+NS['a']+'}solidFill');ET.SubElement(fill,'{'+NS['a']+'}srgbClr',{'val':color})
    ET.SubElement(rp,'{'+NS['a']+'}latin',{'typeface':'Segoe UI'})
    ET.SubElement(run,'{'+NS['a']+'}t').text=value
    tree.append(shape)

fontpath=Path('C:/Windows/Fonts/segoeui.ttf'); boldpath=Path('C:/Windows/Fonts/segoeuib.ttf')
pdfmetrics.registerFont(TTFont('Segoe',str(fontpath))); pdfmetrics.registerFont(TTFont('SegoeBold',str(boldpath)))
pdf=canvas.Canvas(str(HERE/'Umbral_presentacion.pdf'),pagesize=(960,540))
def text(slide,value,x,y,w,h,size=22,color=INK,bold=False):
    pdf.setFillColor('#'+color); pdf.setFont('SegoeBold' if bold else 'Segoe',size)
    words=value.split(); lines=[]; current=''
    for word in words:
        test=(current+' '+word).strip()
        if pdfmetrics.stringWidth(test,'SegoeBold' if bold else 'Segoe',size)>w*72 and current: lines.append(current); current=word
        else: current=test
    if current: lines.append(current)
    native_text(slide,value,x,y,w,max(h,len(lines)*size*1.22/72+.08),size,color,bold)
    for i,line in enumerate(lines): pdf.drawString(x*72,540-y*72-size-i*size*1.22,line)
    return len(lines)*size*1.22/72

for num,(title,parts,foot) in enumerate(slides,1):
    slide=ET.fromstring(package[f'ppt/slides/slide{num}.xml'])
    tree=slide.find('p:cSld/p:spTree',NS)
    for shape in list(tree)[2:]: tree.remove(shape)
    pdf.setFillColor('#'+PAPER); pdf.rect(0,0,960,540,fill=1,stroke=0)
    text(slide,'UMBRAL · '+str(num).zfill(2),.65,.35,12,.3,12,TEAL,True)
    text(slide,title,.65,.9,12,1.2,44 if num==1 else 32,TEAL if num==1 else INK,True)
    if num==5:
        data=[['Corte / método','n','MAE (pp)','Ponderado','Top50'],['2021 · Referencia','1,490','12.12','8.05','16/50'],['2021 · Ridge','1,490','9.21','5.49','19/50'],['2024 · Referencia','1,476','5.64','3.54','27/50'],['2024 · Ridge','1,476','8.58','4.49','27/50']]
        old=ET.fromstring(package['ppt/slides/slide5.xml'])
        table=old.find('p:cSld/p:spTree/p:graphicFrame',NS)
        table=copy.deepcopy(table)
        table.find('p:nvGraphicFramePr/p:cNvPr',NS).set('id',str(len(tree)+1))
        tree.append(table)
        for r,row in enumerate(data):
            for c,value in enumerate(row):
                text_x=.75+sum([4,2,2,2,2][:c])
                pdf.setFillColor('#'+INK); pdf.setFont('SegoeBold' if r==0 else 'Segoe',20); pdf.drawString(text_x*72,540-(2.1+r*.52)*72-20,value)
        text(slide,'La evidencia no demuestra superioridad consistente.',.65,4.95,12,.5,25,TEAL,True)
        text(slide,'Spearman referencia / Ridge: 0.485 / 0.599 en 2021 y 0.827 / 0.811 en 2024. Análisis posterior, sin reajuste del modelo.',.65,5.6,12,.7,20)
    else:
        y=2.15 if num!=1 else 2.6
        for value,size in parts:
            h=text(slide,value,.65,y,11.9,1.0 if size<28 else .7,size,TEAL if size>=24 else INK,size>=24)
            y+=h+.22
    text(slide,foot,.65,6.83,11.9,.45,10,MUTED)
    package[f'ppt/slides/slide{num}.xml']=ET.tostring(slide,encoding='utf-8',xml_declaration=True)
    notes=ET.fromstring(package[f'ppt/notesSlides/notesSlide{num}.xml'])
    for t in notes.findall('.//a:t',NS): t.text=''
    texts=notes.findall('.//a:t',NS)
    if texts: texts[-1].text=foot+' Fuentes primarias: '+CCPC+' Convocatoria: '+CALL
    package[f'ppt/notesSlides/notesSlide{num}.xml']=ET.tostring(notes,encoding='utf-8',xml_declaration=True)
    pdf.showPage()
with zipfile.ZipFile(HERE/'Umbral_presentacion.pptx','w',zipfile.ZIP_DEFLATED) as z:
    for n,b in package.items(): z.writestr(n,b)
pdf.save()
import fitz
doc=fitz.open(HERE/'Umbral_presentacion.pdf')
for i,page in enumerate(doc): page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(HERE/f'QA_{i+1:02}.png')
from PIL import Image
thumbs=[]
for i in range(10):
    im=Image.open(HERE/f'QA_{i+1:02}.png'); im.thumbnail((590,332));thumbs.append(im)
montage=Image.new('RGB',(1200,1750),'#E5EEEA')
for i,im in enumerate(thumbs): montage.paste(im,(5+(i%2)*600,5+(i//2)*350))
montage.save(HERE/'QA_montaje.png')
print('Generadas 10 diapositivas PPTX editables, PDF y 10 vistas QA.')




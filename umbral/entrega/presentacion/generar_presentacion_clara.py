"""Presentación explicativa con capturas reales y exportación nativa de PowerPoint."""
from pathlib import Path
import sys,copy,zipfile,json,subprocess,csv,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE/'.packages'),str(HERE.parent/'reporte/.packages')]
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf
pdfmetrics.registerFont(TTFont('Segoe', 'C:/Windows/Fonts/segoeui.ttf'))
pdfmetrics.registerFont(TTFont('SegoeBold','C:/Windows/Fonts/segoeuib.ttf'))
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
for k,v in NS.items(): ET.register_namespace(k,v)
REL='http://schemas.openxmlformats.org/package/2006/relationships'
with zipfile.ZipFile(HERE/'plantilla_base.pptx') as z: package={n:z.read(n) for n in z.namelist()}
shape_template=ET.fromstring(package['ppt/slides/slide1.xml']).find('p:cSld/p:spTree/p:sp',NS)
INK='15353B'; TEAL='10685F'; MUTED='587177'
FIG=ROOT/'demo/verificacion/demo7'
population_path=ROOT.parent/'fuentes/Bases_de_datos_explicativos/pobproy_inddemo.csv'
with population_path.open(encoding='utf-8-sig') as f:
    population_row=next(row for row in csv.DictReader(f) if row['CLAVE']=='23008' and row['ANO']=='2027')
population=int(population_row['POB_MIT_MUN'])
municipality=next(row for row in json.loads((ROOT/'demo/data/resultados.json').read_text(encoding='utf-8'))['municipios'] if row['key']=='23008')
coverage=min(population,int(municipality['observed']))
votes=coverage*.30/100
number=lambda n: f'{n:,.0f}'
def text(slide,value,x,y,w,size=22,color=INK,bold=False):
    shape=copy.deepcopy(shape_template);tree=slide.find('p:cSld/p:spTree',NS)
    prop=shape.find('p:nvSpPr/p:cNvPr',NS);prop.set('id',str(len(tree)+1));prop.set('name',value[:40])
    lines=[];current='';font='SegoeBold' if bold else 'Segoe'
    for word in value.split():
        trial=(current+' '+word).strip()
        if current and pdfmetrics.stringWidth(trial,font,size)>w*72-12:lines.append(current);current=word
        else:current=trial
    lines.append(current);h=len(lines)*size*1.25/72+.13
    assert y+h<7.48,(value,y,h)
    xf=shape.find('p:spPr/a:xfrm',NS)
    for name,attrs in [('off',{'x':x,'y':y}),('ext',{'cx':w,'cy':h})]:
        e=xf.find('a:'+name,NS)
        for k,v in attrs.items():e.set(k,str(round(v*914400)))
    body=shape.find('p:txBody',NS)
    bp=body.find('a:bodyPr',NS)
    for e in list(bp):bp.remove(e)
    ET.SubElement(bp,'{'+NS['a']+'}noAutofit')
    for e in list(body):
        if e.tag.endswith('}p'):body.remove(e)
    for line in lines:
        para=ET.SubElement(body,'{'+NS['a']+'}p');run=ET.SubElement(para,'{'+NS['a']+'}r')
        rp=ET.SubElement(run,'{'+NS['a']+'}rPr',{'sz':str(size*100),'b':'1' if bold else '0'})
        fill=ET.SubElement(rp,'{'+NS['a']+'}solidFill');ET.SubElement(fill,'{'+NS['a']+'}srgbClr',{'val':color})
        ET.SubElement(rp,'{'+NS['a']+'}latin',{'typeface':'Segoe UI'})
        ET.SubElement(run,'{'+NS['a']+'}t').text=line
    tree.append(shape)
    return h
def image(slide,num,name,x,y,w,h,top_fraction=1):
    path=FIG/name; iw,ih=Image.open(path).size;ih*=top_fraction;scale=min(w/iw,h/ih);ww,hh=iw*scale,ih*scale
    x+=(w-ww)/2;y+=(h-hh)/2
    media='umbral_'+path.name;package['ppt/media/'+media]=path.read_bytes()
    rp=f'ppt/slides/_rels/slide{num}.xml.rels';rels=ET.fromstring(package[rp])
    rid='rIdUmbral'+str(len(rels)+1)
    ET.SubElement(rels,'{'+REL+'}Relationship',{'Id':rid,'Type':NS['r']+'/image','Target':'../media/'+media})
    package[rp]=ET.tostring(rels,encoding='utf-8',xml_declaration=True)
    tree=slide.find('p:cSld/p:spTree',NS)
    xml=f'''<p:pic xmlns:p="{NS['p']}" xmlns:a="{NS['a']}" xmlns:r="{NS['r']}"><p:nvPicPr><p:cNvPr id="{len(tree)+1}" name="Captura real de Umbral"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{round(x*914400)}" y="{round(y*914400)}"/><a:ext cx="{round(ww*914400)}" cy="{round(hh*914400)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''
    picture=ET.fromstring(xml)
    if top_fraction<1:
        fill=picture.find('p:blipFill',NS)
        fill.insert(1,ET.Element('{'+NS['a']+'}srcRect',{'b':str(round((1-top_fraction)*100000))}))
    tree.append(picture)
titles=['UMBRAL','El problema: decidir dónde actuar','Qué permite hacer Umbral','Cómo predice la abstención de 2027','Qué tan bien predice','Consultar el territorio antes de actuar','Simular una acción y comparar el cambio','Planes para las 32 entidades','SMS en Solidaridad: cobertura municipal','Referencias y documentos consultados']
notes=[]
for n,title in enumerate(titles,1):
    slide=ET.fromstring(package[f'ppt/slides/slide{n}.xml']);tree=slide.find('p:cSld/p:spTree',NS)
    for e in list(tree)[2:]:tree.remove(e)
    if n>1:
        text(slide,title,.55,.35,12.3,34,TEAL,True)
    foot='Umbral · aguas.exe · Reto 2'; note=''
    if n==1:
        image(slide,n,'logo_umbral.png',.55,.3,1.05,1.05)
        image(slide,n,str(HERE/'recursos/hackea_participacion_ine.png'),10.1,.3,2.65,1.15)
        text(slide,'Predicción de abstención electoral 2027',.55,1.55,6.1,30,INK,True)
        text(slide,'Información territorial, simulación de acciones y planes estatales.',.55,3.05,5.8,25)
        text(slide,'Martin Isai Nuñez Villeda\n y Cesar Donnet Hernandez Gastelum',.55,5.35,6,16)
        image(slide,n,'mapa_base.png',6.85,1.45,5.8,4.95)
    elif n==2:
        text(slide,'¿En qué municipios podría concentrarse la abstención en 2027?',.55,1.65,6.1,30,INK,True)
        text(slide,'La capacidad de atención es limitada. Hace falta elegir territorios y justificar esa elección.',.55,3.45,5.8,24)
        text(slide,'Umbral reúne la predicción y el contexto para preparar esa decisión.',.55,5.15,5.8,24,TEAL,True)
        image(slide,n,'recorrido_mexico.png',6.85,1.55,5.9,4.9)
    elif n==3:
        rows=[('01  PREDECIR','Estimar la abstención municipal de 2027.'),('02  INFORMAR','Consultar históricos, perfiles y fuentes.'),('03  SIMULAR','Comparar escenarios sin y con una acción.'),('04  PROPONER','Revisar planes adaptados al contexto estatal.')]
        for i,(a,b) in enumerate(rows):
            y=1.65+i*1.18;text(slide,a,.7,y,3.6,24,TEAL,True);text(slide,b,4.4,y,8.1,25)
    elif n==4:
        for x,big,small in [(.65,'2009–2024','Historia electoral del INE'),(4.9,'15 variables','Abstención, edad, urbanización y calidad'),(9.15,'2027','Predicción municipal')]:
            text(slide,big,x,1.65,3.5,32,TEAL,True);text(slide,small,x,2.45,3.5,22)
        text(slide,'Se comparan cuatro modelos; se selecciona HistGradientBoosting.',.65,4.2,11.9,25,INK,True)
        text(slide,'1,783 municipios con estimación. Otros 694 quedan sin estimación por información insuficiente.',.65,5.2,11.9,24)
        foot='Fuente: CCPC 2009–2024 y comparación de cuatro modelos. Datos agregados, sin información personal.'
    elif n==5:
        text(slide,'6.84 pp',.7,1.65,5.3,60,TEAL,True)
        text(slide,'Error absoluto medio del modelo en las evaluaciones de 2021 y 2024.',.7,3.1,5.4,24)
        text(slide,'Referencia simple: 8.88 pp',.7,4.65,5.5,24,INK,True)
        text(slide,'El modelo puede equivocarse.',7,1.85,5.6,30,INK,True)
        text(slide,'En 2024, la referencia identificó 27 de los 50 municipios con mayor abstención; el modelo, 19.',7,3,5.5,24)
        text(slide,'El acierto de 2027 se comprobará cuando existan resultados.',7,5,5.5,24)
        foot='pp = puntos porcentuales. Modelo seleccionado por error medio y desempate ponderado; selección retrospectiva.'
    elif n==6:
        image(slide,n,'ficha_plan_estatal.png',.55,1.4,7.55,4.95)
        text(slide,'Qué revisar',8.45,1.65,4.1,28,TEAL,True)
        text(slide,'Histórico de abstención.\n Calidad y cobertura de datos.\n Contexto y perfiles agregados.\n Estabilidad de la prioridad.',8.45,2.55,4.1,23)
        text(slide,'El mapa muestra dónde mirar; la información ayuda a interpretar el territorio.',8.45,5.15,4.1,21)
    elif n==7:
        for x,img,label in [(.55,'escenario_sin.png','1. Sin acción'),(4.8,'mapa_intervencion.png','2. Con acción'),(9.05,'mapa_cambio.png','3. Diferencia')]:
            text(slide,label,x,1.5,3.8,25,TEAL,True);image(slide,n,img,x,2.05,3.75,2.45)
        text(slide,'Elegir acción y cobertura → aplicar su coeficiente → comparar tasas.',.65,4.85,12,25,INK,True)
        text(slide,'Reparto por prioridad o proporcional. Los cálculos usan efectos publicados o supuestos identificados; se mantienen los umbrales del semáforo.',.65,5.65,12,22)
        foot='Capturas del escenario estatal de Quintana Roo: cobertura 10%, efecto supuesto de 1.5 pp. No son el caso SMS.'
    elif n==8:
        text(slide,'Contexto + investigación mexicana',.65,1.65,6.2,28,TEAL,True)
        text(slide,'Estudios de participación y abstencionismo, ENCUCI y ENCÍVICA ayudan a orientar las propuestas.',.65,2.65,6,24)
        text(slide,'Cada plan reúne acciones, actores propuestos, indicadores y horizonte.',.65,4.15,6,24)
        text(slide,'Escenario ilustrativo: 10% de cobertura y 1.5 pp de efecto supuesto.',.65,5.4,6,23,INK,True)
        image(slide,n,'plan_estatal_presentacion.png',7.15,1.5,5.6,4.95,.25)
        foot='Propuestas del proyecto; costos y operación requieren acuerdo local. El 1.5 pp no es eficacia medida de los planes.'
    elif n==9:
        text(slide,'SOLIDARIDAD · clave histórica 23008 · Quintana Roo',.65,1.5,12,25,INK,True)
        text(slide,f'Población proyectada 2027: {number(population)} habitantes.',.65,2.05,12,22)
        text(slide,'Investigación en Suecia: recordatorios electorales enviados por SMS.',.65,2.5,12,21)
        for x,big,small in [(.65,number(coverage),'Personas de la base electoral'),(4.9,'0.30 pp','Efecto publicado del recordatorio'),(9.15,'≈ '+number(votes)+' votos','Adicionales hipotéticos')]:
            text(slide,big,x,3.1,3.5,36,TEAL,True);text(slide,small,x,3.95,3.5,20)
        text(slide,f'{number(coverage)} × 0.30 / 100 = {votes:,.3f}',.65,4.75,12,29,INK,True)
        text(slide,'La cobertura se limita a SV+NV 2024, no a todos los habitantes. Reducción municipal: 0.30 pp, bajo el supuesto de cobertura total.',.65,5.65,12,22)
        foot='Población: proyección CONAPO 2027. SMS: Lindgren et al. (2025), transferencia hipotética. Estabilidad top50: 4/6.'
    elif n==10:
        references=[
          'INE. Conteos Censales de Participación Ciudadana 2009–2024 y manual de campos.',
          'INE (2016). Estudio censal de participación ciudadana: elecciones federales de 2015.',
          'INE (2024). Estudio muestral de participación ciudadana, proceso 2023–2024.',
          'INE / INEGI (2021). ENCUCI 2020: presentación ejecutiva.',
          'INE (2026). Acuerdo INE/CG61/2026. Implementación de ENCÍVICA 2024–2026.',
          'CONAPO. Proyecciones municipales: población a mitad de año, Solidaridad 2027.',
          'IFE. Informe preliminar sobre abstencionismo en México. González Rodríguez (2024): tesis sobre juventudes y redes.',
          'Central Electoral. Presentan en Durango investigación sobre participación política y electoral de las juventudes en México.',
          'Lindgren, Nyman y Oskarsson (2025). SMS, Suecia. DOI: 10.1017/S0007123424000504.',
          'Haenschen, Mann y DeMora (2026). SMS, EEUU. DOI: 10.1007/s11109-026-10121-2.',
          'Nickerson y Rogers (2010). Plan de voto por llamada. DOI: 10.1177/0956797609359326.',
          'aguas.exe (2026). Reporte Umbral, protocolo, comparación de modelos y planes estatales. Repositorio: Donatelatrump/Ine_Hackaton_2026.'
        ]
        for i,ref in enumerate(references):
            col=i//6;row=i%6
            text(slide,ref,.65+col*6.3,1.45+row*.87,5.95,16)
        foot='Copias de las fuentes mexicanas en Info_extra/ del ZIP. Referencias completas y rutas en las notas y en el reporte.'
    text(slide,foot,.55,7.02,12.2,10,MUTED)
    package[f'ppt/slides/slide{n}.xml']=ET.tostring(slide,encoding='utf-8',xml_declaration=True)
    notes=ET.fromstring(package[f'ppt/notesSlides/notesSlide{n}.xml'])
    ts=notes.findall('.//a:t',NS)
    for t in ts:t.text=''
    if ts:ts[-1].text=title+'. '+foot+' Fuentes: reporte metodológico; modelado/salidas/comparacion_modelos/resultados.json; entrega/caso_municipal.json; docs/FUENTES_COMPLEMENTARIAS_UMBRAL.md; docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md. DOI SMS: 10.1017/S0007123424000504.'
    package[f'ppt/notesSlides/notesSlide{n}.xml']=ET.tostring(notes,encoding='utf-8',xml_declaration=True)
ct=ET.fromstring(package['[Content_Types].xml']);ctns='http://schemas.openxmlformats.org/package/2006/content-types'
if not any(e.get('Extension')=='png' for e in ct):ET.SubElement(ct,'{'+ctns+'}Default',{'Extension':'png','ContentType':'image/png'})
package['[Content_Types].xml']=ET.tostring(ct,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(HERE/'Umbral_presentacion.pptx','w',zipfile.ZIP_DEFLATED) as z:
    for name,data in package.items():z.writestr(name,data)
script=HERE/'exportar_powerpoint.ps1'
subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(script)],check=True)
doc=pymupdf.open(HERE/'Umbral_presentacion.pdf');assert len(doc)==10
for i,p in enumerate(doc):p.get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(HERE/f'QA_{i+1:02}.png')
montage=Image.new('RGB',(1200,1750),'#dfe8e3')
for i in range(10):
    im=Image.open(HERE/f'QA_{i+1:02}.png');im.thumbnail((590,340));montage.paste(im,((i%2)*600+5,(i//2)*350+5))
montage.save(HERE/'QA_montaje.png')
print('10 diapositivas con capturas reales; PDF exportado por PowerPoint.')

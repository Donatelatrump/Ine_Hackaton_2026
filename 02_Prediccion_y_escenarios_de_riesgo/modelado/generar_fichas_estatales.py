"""Genera contexto descriptivo estatal; no recomienda intervenciones ni estima efectos."""
from pathlib import Path
import csv,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo/data'
SPECS=[
 ('Otras_fuentes_de_informacion','Insituto Federal Electoral.html','Estudio sobre abstencionismo en México · IFE','Estudio histórico sobre factores asociados al abstencionismo. No identifica causas actuales de cada estado.','Histórico / nacional'),
 ('Otras_fuentes_de_informacion','Martha Iris González Rodriguez.pdf','Participación juvenil y redes sociales · González Rodríguez, 2024','Tesis sobre las elecciones de 2018 en Gustavo A. Madero. Sus resultados no representan a todos los municipios.','Caso: Gustavo A. Madero, CDMX'),
 ('Otras_fuentes_de_informacion','Presentan en Durango investigación sobre participación política y electoral de las juventudes en México - Central Electoral.html','Presentación de investigación sobre juventudes · Central Electoral','Nota sobre una investigación presentada en Durango; la sede no convierte sus hallazgos en una medición estatal.','Nota de divulgación'),
 ('Datos_propuestas_estatales','CGex202602-26-ap-3.pdf','ENCÍVICA · Plan de implementación 2026','Acuerdo INE/CG61/2026 que aprueba el plan nacional. No es un plan específico para cada entidad ni demuestra efectos locales.','Nacional · acuerdo 2026'),
 ('Datos_propuestas_estatales','coe-3se-09-12-2024-p02.pdf','Estudio muestral de participación ciudadana 2024','Estudio del proceso concurrente 2023–2024. Sus estimaciones muestrales se distinguen de los conteos censales usados en el mapa.','Muestral · elección 2024'),
 ('Datos_propuestas_estatales','ENCUCI_2020_Presentacion_Ejecutiva.pdf','ENCUCI 2020 · principales resultados','Encuesta de cultura cívica sobre creencias, valores y prácticas. No se asignan porcentajes nacionales o regionales a municipios.','Encuesta 2020 · presentación 2021'),
 ('Datos_propuestas_estatales','Estudio-Censal-2015-VF.pdf','Estudio censal de participación ciudadana 2015','Antecedente de participación por entidad, edad, sexo y tipo de sección. Describe 2015, sin extrapolar sus resultados a 2027.','Censal · elección 2015')]
sources=[]
for folder,file,title,note,scope in SPECS:
 p=ROOT/folder/file
 sources.append(dict(path=f'{folder}/{file}',title=title,note=note,scope=scope,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
states={};inventory=[]
for p in sorted((ROOT/'Bases_de_datos_explicativos').glob('*.csv')):
 years=set();count=0;seen=set();duplicates=0
 with p.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);columns=reader.fieldnames
  for row in reader:
   count+=1;year=row.get('ANO',row.get('ANIO',''));years.add(year)
   if p.name!='pobproy_ggrupos.csv' or year not in ('2024','2027'):continue
   key=str(int(row['CLAVE'])).zfill(5)
   if key.endswith('000'):continue
   identity=(key,year,row['SEXO'])
   if identity in seen:duplicates+=1;continue
   seen.add(identity)
   st=str(int(row['CLAVE_ENT'])).zfill(2)
   if not 1<=int(st)<=32:continue
   item=states.setdefault(st,{'name':row['NOM_ENT'],'population':{},'municipalities':{}})
   item['population'][year]=item['population'].get(year,0)+float(row['POB_TOTAL'])
   item['municipalities'].setdefault(year,set()).add(key)
 inventory.append(dict(path='Bases_de_datos_explicativos/'+p.name,rows=count,years=sorted(years),columns=columns,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),duplicate_population_rows=duplicates))
for st in states.values():st['municipalities']={y:len(keys) for y,keys in st['municipalities'].items()}
payload={'sources':sources,'csv_inventory':inventory,'states':states,'population_source':'Bases_de_datos_explicativos/pobproy_ggrupos.csv','population_definition':'Suma de POB_TOTAL de HOMBRES y MUJERES por municipio y año, excluyendo claves terminadas en 000. Cada clave, año y sexo se suma una sola vez. Población total, no lista nominal.','scope':'Contexto descriptivo; no atribuye causas individuales ni recomienda acciones para modificar la participación.'}
(OUT/'fichas_estatales.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'fichas_estatales.js').write_text('window.UMBRAL_FICHAS_ESTATALES='+json.dumps(payload,ensure_ascii=False)+';\n',encoding='utf-8')
print(f'{len(sources)} documentos, {len(inventory)} CSV y {len(states)} entidades documentados.')

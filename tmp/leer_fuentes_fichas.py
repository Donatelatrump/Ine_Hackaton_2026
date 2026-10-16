from pathlib import Path
import sys,re,json,csv,hashlib
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/.packages'))
import fitz
OUT=ROOT/'tmp/fuentes_fichas';OUT.mkdir(exist_ok=True)
for folder in ['Otras_fuentes_de_informacion','Datos_propuestas_estatales']:
 for p in (ROOT/folder).iterdir():
  if p.suffix.lower()=='.pdf':
   doc=fitz.open(p)
   text='\n'.join(f'\nPÁGINA {i+1}\n'+page.get_text() for i,page in enumerate(doc))
  elif p.suffix.lower()=='.html':
   text=p.read_text(encoding='utf-8',errors='replace')
   text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',text,flags=re.S|re.I)
   text=unescape(re.sub('<[^>]+>',' ',text));text=re.sub(r'[ \t]+',' ',text)
  else:continue
  (OUT/(p.stem+'.txt')).write_text(text,encoding='utf-8')
  print(p.name, 'caracteres',len(text));print(text[:2300])

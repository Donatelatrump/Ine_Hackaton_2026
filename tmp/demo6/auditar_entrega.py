import json
from pathlib import Path
from html.parser import HTMLParser

ROOT=Path(__file__).resolve().parents[2]
before=json.loads((ROOT/'tmp/demo6/voto-vigia-before.json').read_text())
after={str(p.relative_to(ROOT)):[p.stat().st_size,p.stat().st_mtime_ns] for p in (ROOT/'voto-vigia').rglob('*') if p.is_file()}
assert before==after,'Se detectaron cambios en Voto Vigía'
DEMO=ROOT/'02_Prediccion_y_escenarios_de_riesgo/demo'
class Assets(HTMLParser):
    values=[]
    def handle_starttag(self,tag,attrs):
        for name,value in attrs:
            if name in ('src','href') and value and not value.startswith(('http','#')):
                self.values.append(value.split('?')[0].split('#')[0])
parser=Assets();parser.feed((DEMO/'demo6.html').read_text(encoding='utf-8'))
missing=[value for value in parser.values if not (DEMO/value).exists()]
assert not missing,missing
print(f'Voto Vigía intacto: {len(after)} archivos. Recursos locales comprobados: {len(parser.values)}.')

"""Inventario estático de Umbral: estructura, tamaño y recursos locales HTML.

No importa módulos del modelo, no inicia la web y no ejecuta pruebas.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json

TRACK=Path(__file__).resolve().parents[1]
EXCLUDE={'.packages','__pycache__','.analysis_tmp','archivo'}

class Assets(HTMLParser):
    def __init__(self):
        super().__init__();self.paths=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        value=attrs.get('src') if tag in ('script','img') else attrs.get('href') if tag=='link' else None
        if value and not urlsplit(value).scheme and not value.startswith('//'):
            self.paths.append(unquote(urlsplit(value).path))

def main():
    files=[p for p in TRACK.rglob('*') if p.is_file() and not EXCLUDE.intersection(p.relative_to(TRACK).parts)]
    sources=[p for p in files if p.suffix in {'.py','.js','.cjs','.css','.html'} and not {'data','salidas','vendor','assets'}.intersection(p.relative_to(TRACK).parts)]
    sizes=[{'path':p.relative_to(TRACK).as_posix(),'bytes':p.stat().st_size,'lines':len(p.read_text(encoding='utf-8',errors='replace').splitlines())} for p in sources]
    pages={}
    for p in sorted((TRACK/'demo').glob('*.html')):
        parser=Assets();parser.feed(p.read_text(encoding='utf-8'))
        pages[p.name]={'resources':parser.paths,'missing':[v for v in parser.paths if not (p.parent/v).is_file()]}
    payload={'scope':'Umbral; excluye Voto Vigía, dependencias instaladas, archivo de depuración y cachés. Referencias HTML estáticas, sin ejecutar navegador o pruebas.','file_count':len(files),'extensions':dict(Counter(p.suffix or '[sin extensión]' for p in files)),'sources':sorted(sizes,key=lambda r:r['lines'],reverse=True),'pages':pages}
    dest=TRACK/'arquitectura/inventario.json';dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(files),'source_files':len(sources),'pages':{k:{'resources':len(v['resources']),'missing':v['missing']} for k,v in pages.items()}},ensure_ascii=True))

if __name__=='__main__':main()

"""Entrega estricta: convocatoria INE, bases sexta (Reto 2) y septima."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, quote
from html import escape
import base64
import hashlib
import json
import mimetypes
import os
import re
import zipfile
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'umbral/demo'
DEST = ROOT / 'Aguas.exe_Reto_2_Prediccion_y_escenarios_de_riesgo_de_abstencion.zip'
STAGE = ROOT / 'tmp/entrega_oficial'
REPO = 'https://github.com/Donatelatrump/Ine_Hackaton_2026'
REPORT = 'Umbral_reporte_metodologico_preventivo.pdf'
PRESENTATION = 'Umbral_presentacion.pdf'
HISTORY = 'Umbral_base_historica.csv'
FORECAST = 'Umbral_proyecciones_2027.csv'
FILES = {
    REPORT: 'umbral/entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf',
    PRESENTATION: 'umbral/entrega/presentacion/Umbral_presentacion.pdf',
    'Carta_de_cesion_de_derechos_firmada.pdf': 'umbral/entrega/Carta de cesion de derechos.pdf',
    'Carta_de_decir_verdad_firmada.pdf': 'umbral/entrega/carta decir la verdad.pdf',
    HISTORY: 'umbral/datos_preparados/municipios_historico_con_calidad.csv',
    FORECAST: 'umbral/modelado/salidas/comparacion_modelos/proyeccion_2027.csv',
}

def data_uri(path):
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def extra_info():
    """Preserve the research originals and the resources of saved web pages."""
    return {'Info_extra/'+p.relative_to(ROOT/'fuentes').as_posix():p.read_bytes()
            for p in sorted((ROOT/'fuentes').rglob('*'))
            if p.is_file() and p.suffix.lower() not in {'.md','.pyc'}
            and '__pycache__' not in p.parts}

def research_links():
    catalog=json.loads((DEMO/'data/fichas_estatales.json').read_text(encoding='utf-8'))
    def link(path,label):
        target=path.replace('fuentes/','Info_extra/',1)
        return '<li><a href="'+quote(target,safe='/')+'" target="_blank" rel="noopener">'+escape(label)+'</a></li>'
    documents=''.join(link(row['path'],row['title']) for row in catalog['sources'])
    datasets=''.join(link(row['path'],Path(row['path']).name) for row in catalog['csv_inventory'])
    return ('<article id="info-extra"><h3>Investigaciones y fuentes complementarias</h3>'
            '<p>Estudios, documentos y bases consultados. Los enlaces abren las copias incluidas en Info_extra.</p>'
            '<h4>Investigaciones y documentos</h4><ul>'+documents+'</ul>'
            '<details><summary>Bases de contexto demográfico</summary><ul>'+datasets+'</ul></details></article>')

def standalone():
    html = (DEMO/'demo7.html').read_text(encoding='utf-8')
    # These development-only cards are not requested deliverables.
    html = re.sub(r'<article class="d7-delivery">.*?</article>', '', html, flags=re.S)
    html = re.sub(r'<article><h3>Mapa de municipios</h3>.*?</article>', '', html, flags=re.S)
    html = re.sub(r'<a\b[^>]*href="[^"]+\.pptx"[^>]*>.*?</a>', '', html, flags=re.S)
    html = re.sub(r'<a\b[^>]*href="[^"]+resultados\.json"[^>]*>.*?</a>', '', html, flags=re.S)
    links = {
        '../entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf': REPORT,
        '../entrega/presentacion/Umbral_presentacion.pdf': PRESENTATION,
        '../datos_preparados/municipios_historico_con_calidad.csv': HISTORY,
        '../modelado/salidas/comparacion_modelos/proyeccion_2027.csv': FORECAST,
        '../datos_preparados/README.md': REPORT,
        '../modelado/METODOLOGIA.md': REPORT,
        'DEMO7.md': REPO,
    }
    for old,new in links.items(): html=html.replace('href="'+old+'"','href="'+new+'"')
    html=html.replace('Abrir guía de Demo7','Consultar código del proyecto')
    html=html.replace('Demo7 funciona con archivos locales. Conserva las carpetas del proyecto para abrir también sus fuentes y documentos.', 'Abre index.html para consultar el mapa sin instalación ni conexión. Los PDF y CSV incluidos completan la entrega. El código está disponible en el repositorio enlazado.')
    html=html.replace('14 páginas · Demo7','14 páginas · Umbral')
    html=html.replace('<article id="report-status">',research_links()+'\n<article id="report-status">')
    scripts=[]
    def inline_script(match):
        path=DEMO/unquote(urlsplit(match.group(1)).path)
        source=path.read_text(encoding='utf-8')
        if path.name=='fichas_estatales.js': source=source.replace('fuentes/','Info_extra/')
        source=source.replace('../../docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md',REPO+'/blob/main/docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md')
        source=source.replace('//# sourceMappingURL=leaflet.js.map','')
        source=re.sub(r'</script',r'<\\/script',source,flags=re.I)
        tag=' id="umbral-aplicacion"' if path.name=='demo7.js' else ' id="umbral-decision"' if path.name=='decision.js' else ''
        scripts.append('<script'+tag+'>\n'+source+'\n</script>')
        return ''
    html=re.sub(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>\s*</script>',inline_script,html)
    def inline_style(match):
        path=DEMO/unquote(urlsplit(match.group(1)).path)
        css=path.read_text(encoding='utf-8')
        def resource(m):
            raw=m.group(1).strip('"\' ')
            if raw.startswith(('data:','#')): return m.group(0)
            asset=path.parent/raw
            # Leaflet's optional marker/layer images are not used by this canvas map.
            return 'url("'+data_uri(asset)+'")' if asset.is_file() else 'none'
        css=re.sub(r'url\(([^)]+)\)',resource,css)
        tag=' id="umbral-estilos"' if path.name=='demo7.css' else ''
        return '<style'+tag+'>\n'+css+'\n</style>'
    html=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>',inline_style,html)
    html=re.sub(r'(<img\b[^>]*src=")([^"]+)(")',lambda m:m[1]+data_uri(DEMO/m[2])+m[3],html)
    license_text=(DEMO/'vendor/LICENSE').read_text(encoding='utf-8')
    html=html.replace('</body>','<!-- Leaflet license\n'+license_text.replace('--','- -')+'\n-->\n'+'\n'.join(scripts)+'\n</body>')
    assert not re.search(r'<script[^>]+src=',html)
    return html.encode('utf-8')

class Links(HTMLParser):
    def __init__(self): super().__init__(); self.paths=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in {'src','href'} and value:
                url=urlsplit(value)
                if not url.scheme and url.path and not value.startswith('//'):
                    self.paths.append(unquote(url.path))

def project_code():
    """Only the active web build and the four-model experiment, not old demos."""
    payload={}
    config=json.loads((DEMO/'build.demo7.config.json').read_text(encoding='utf-8'))
    def clean(path):
        return path.replace('src/demo6/','src/compartido/').replace('src/demo7/','src/aplicacion/').replace('styles/demo6/','styles/compartido/').replace('styles/demo7.css','styles/umbral.css')
    for path in [config['analytics'],*config['scripts'],*config['styles']]:
        source=(DEMO/path).read_text(encoding='utf-8')
        source=source.replace('../../docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md',REPO+'/blob/main/docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md')
        payload['codigo/aplicacion/'+clean(path)]=source.encode('utf-8')
    plans=(ROOT/config.pop('state_plan_markdown')).read_text(encoding='utf-8')
    config['state_plan_json']='planes_estatales.json'
    config['analytics']=clean(config['analytics'])
    config['scripts']=[clean(p) for p in config['scripts']]
    config['styles']=[clean(p) for p in config['styles']]
    payload['codigo/aplicacion/build.config.json']=json.dumps(config,ensure_ascii=False,indent=2).encode('utf-8')
    payload['codigo/aplicacion/planes_estatales.json']=json.dumps(plans,ensure_ascii=False).encode('utf-8')
    payload['codigo/aplicacion/decision.js']=(DEMO/'decision.js').read_bytes()
    for name in ['core.py','comparar_modelos.py','requirements_comparacion.lock.txt']:
        source=(ROOT/'umbral/modelado'/name).read_text(encoding='utf-8')
        if name=='comparar_modelos.py':
            source=source.replace("SOURCE=ROOT/'datos_preparados/municipios_historico_con_calidad.csv'", "SOURCE=ROOT.parent/'Umbral_base_historica.csv'")
            source=source.replace('Leer PROTOCOLO_COMPARACION_4_MODELOS.md antes de ejecutar.', 'Consultar el reporte metodologico incluido en la entrega.')
        payload['codigo/modelado/'+name]=source.encode('utf-8')
    payload['codigo/construir_web.py']=BUILDER.encode('utf-8')
    return payload

BUILDER = r'''"""Reconstruye index.html desde el codigo activo. Ejecutar con Python 3."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent
APP=ROOT/'aplicacion'
config=json.loads((APP/'build.config.json').read_text(encoding='utf-8'))
read=lambda name:(APP/name).read_text(encoding='utf-8')
plans=json.loads(read(config['state_plan_json']))
js="(() => {\n'use strict';\nconst analyticsModule={exports:{}};\n(function(module){\n"
js+=read(config['analytics'])+'\n})(analyticsModule);\nconst UmbralAnalytics=analyticsModule.exports;\n'
js+='const statePlanMarkdown='+json.dumps(plans,ensure_ascii=False)+';\n'
js+='\n'.join(read(name) for name in config['scripts'])+'\n})();\n'
css='\n'.join(read(name) for name in config['styles'])
path=ROOT.parent/'index.html'
html=path.read_text(encoding='utf-8')
js=re.sub(r'</script',r'<\\/script',js,flags=re.I)
html,n=re.subn(r'(<script id="umbral-aplicacion">).*?(</script>)',lambda m:m[1]+'\n'+js+'\n'+m[2],html,flags=re.S)
assert n==1
html,n=re.subn(r'(<style id="umbral-estilos">).*?(</style>)',lambda m:m[1]+'\n'+css+'\n'+m[2],html,flags=re.S)
assert n==1
decision=re.sub(r'</script',r'<\\/script',read('decision.js'),flags=re.I)
html,n=re.subn(r'(<script id="umbral-decision">).*?(</script>)',lambda m:m[1]+'\n'+decision+'\n'+m[2],html,flags=re.S)
assert n==1
path.write_text(html,encoding='utf-8')
print('Umbral: index.html reconstruido.')
'''

def main():
    payload={name:(ROOT/source).read_bytes() for name,source in FILES.items()}
    payload['index.html']=standalone()
    assert len(payload)==7
    payload.update(extra_info())
    parser=Links(); parser.feed(payload['index.html'].decode('utf-8'))
    assert all(path in payload for path in parser.paths),parser.paths
    payload.update(project_code())
    assert not any(name.endswith('.md') or re.search(r'demo[0-9]',name) for name in payload)
    STAGE.mkdir(parents=True,exist_ok=True)
    for name,data in payload.items():
        target=STAGE/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(data)
    subprocess.run([sys.executable,str(STAGE/'codigo/construir_web.py')],check=True)
    payload['index.html']=(STAGE/'index.html').read_bytes()
    temporary=DEST.with_suffix('.zip.part')
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,data in payload.items(): archive.writestr(name,data)
    with zipfile.ZipFile(temporary) as archive:
        assert set(archive.namelist())==set(payload)
        assert archive.testzip() is None
        for name,data in payload.items(): assert archive.read(name)==data
    os.replace(temporary,DEST)
    print(json.dumps({'zip':DEST.name,'files':len(payload),'top_level':[n for n in payload if '/' not in n]+['codigo/','Info_extra/'],'extra_files':sum(n.startswith('Info_extra/') for n in payload),'bytes':DEST.stat().st_size,'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'integrity':'OK','signed_letters':'identical to originals'},ensure_ascii=True,indent=2))

if __name__=='__main__': main()

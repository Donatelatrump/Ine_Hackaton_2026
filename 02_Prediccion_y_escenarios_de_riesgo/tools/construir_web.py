"""Construye recursos estáticos de demo6 sin npm ni dependencias externas.

Las fuentes comparten una clausura privada: no publican estado mutable en window.
"""
from pathlib import Path
import hashlib,json

DEMO=Path(__file__).resolve().parents[1]/'demo'

def main():
    config=json.loads((DEMO/'build.config.json').read_text(encoding='utf-8'))
    provenance={}
    def read(relative):
        path=(DEMO/relative).resolve()
        if not path.is_relative_to(DEMO.resolve()):raise ValueError('Fuente fuera de demo: '+relative)
        content=path.read_text(encoding='utf-8')
        provenance[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
        return content
    analytics=read(config['analytics'])
    js="/* Generado por tools/construir_web.py. Editar fuentes, no este archivo. */\n(() => {\n'use strict';\n"
    js+="const analyticsModule={exports:{}};\n(function(module){\n"+analytics+"\n})(analyticsModule);\nconst UmbralAnalytics=analyticsModule.exports;\n"
    for source in config['scripts']:
        js+='\n/* SOURCE: '+source+' */\n'+read(source)+'\n'
    js+='\n})();\n'
    css='/* Generado por tools/construir_web.py; orden de cascada en build.config.json. */\n'
    for source in config['styles']:css+='\n/* SOURCE: '+source+' */\n'+read(source)+'\n'
    out=DEMO/'assets';out.mkdir(exist_ok=True)
    (out/'demo6.js').write_text(js,encoding='utf-8')
    (out/'demo6.css').write_text(css,encoding='utf-8')
    outputs={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['demo6.js','demo6.css']}
    (out/'build.json').write_text(json.dumps({'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((DEMO/'build.config.json').read_bytes()).hexdigest(),'sources':provenance,'outputs':outputs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Demo6: {len(config["scripts"])+1} fuentes JS y {len(config["styles"])} CSS -> assets/demo6.js y assets/demo6.css')

if __name__=='__main__':main()

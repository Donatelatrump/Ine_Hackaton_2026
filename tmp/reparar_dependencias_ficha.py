from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];D=R/'02_Prediccion_y_escenarios_de_riesgo/demo'
p=D/'src/demo6/views/state-profile.js';s=p.read_text(encoding='utf-8')
s=s.replace("  if(typeof window!=='undefined'&&window._umbralRuntime){\n    window._umbralRuntime.renderProfile=function(selection,records){",'  runtime.renderProfile=function(selection,records){',1)
end='    };\n  }\n})();'
if end not in s:raise ValueError('Cierre del registro inesperado')
s=s.replace(end,'  };\n})();',1)
p.write_text(s,encoding='utf-8')
p=D/'src/demo6/app/runtime.js';s=p.read_text(encoding='utf-8')
s=s.replace("if(typeof window!=='undefined')window._umbralRuntime=runtime;\n",'')
p.write_text(s,encoding='utf-8')
p=D/'build.config.json';c=json.loads(p.read_text(encoding='utf-8'))
c['scripts']=[v.replace('views/state-context.js','views/state-profile.js') for v in c['scripts']]
p.write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
p=D/'demo6.html';s=p.read_text(encoding='utf-8')
s='\n'.join(line for line in s.split('\n') if '<script' not in line or 'src/demo6/views/state-profile.js' not in line)
s=s.replace('assets/demo6.js?v=20261016-runtime-fix','assets/demo6.js?v=20261016-analytics-fix').replace('assets/demo6.js?v=20261016-ficha03','assets/demo6.js?v=20261016-analytics-fix')
p.write_text(s,encoding='utf-8')

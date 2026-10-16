from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];D=R/'02_Prediccion_y_escenarios_de_riesgo/demo'
p=D/'build.config.json';config=json.loads(p.read_text(encoding='utf-8'))
config['scripts']=[s.replace('views/state-profile.js','views/state-context.js') for s in config['scripts']]
p.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
p=D/'src/demo6/app/runtime.js';s=p.read_text(encoding='utf-8')
s=re.sub(r"^.*window\._umbralRuntime\s*=\s*runtime;.*\n?",'',s,flags=re.M)
p.write_text(s,encoding='utf-8')
p=D/'demo6.html';s=p.read_text(encoding='utf-8')
s=re.sub(r'^.*<script[^>]+src="src/demo6/views/state-profile\.js[^\"]*"[^>]*></script>.*\n?','',s,flags=re.M)
s=re.sub(r'^.*<script[^>]+src="src/demo6/domain/state-plans\.js[^\"]*"[^>]*></script>.*\n?','',s,flags=re.M)
s=re.sub(r'assets/demo6\.js\?v=[^\"]+', 'assets/demo6.js?v=20261016-private-context-2',s)
p.write_text(s,encoding='utf-8')

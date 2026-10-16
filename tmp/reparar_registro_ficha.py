from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
D=R/'02_Prediccion_y_escenarios_de_riesgo/demo'
source=R/'tmp/demo6/antes_arranque/src/views/state-profile.js'
text=source.read_text(encoding='utf-8').replace('window.renderDemo6Ficha','runtime.renderProfile')
(D/'src/demo6/views/state-context.js').write_text(text,encoding='utf-8')
p=D/'build.config.json';config=json.loads(p.read_text(encoding='utf-8'))
config['scripts']=[s.replace('src/demo6/views/state-profile.js','src/demo6/views/state-context.js') for s in config['scripts']]
p.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
p=D/'demo6.html';text=p.read_text(encoding='utf-8')
text='\n'.join(line for line in text.split('\n') if 'src/demo6/domain/state-plans.js' not in line and 'src/demo6/views/state-profile.js' not in line)
text=text.replace('assets/demo6.js?v=20261016-modular','assets/demo6.js?v=20261016-runtime-fix')
p.write_text(text,encoding='utf-8')

from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/'02_Prediccion_y_escenarios_de_riesgo/demo'
p=D/'demo6.html';s=p.read_text(encoding='utf-8')
block='''        <section class="panel d6-action-plan" id="d6-action-plan" aria-labelledby="d6-action-plan-title">
          <h3 id="d6-action-plan-title">Plan de acción recomendado</h3>
          <div id="d6-action-plan-content"></div>
        </section>
'''
if block not in s:raise ValueError('No se encontró el apartado separado')
s=s.replace(block,'',1).replace('20261016-apartado03','20261016-ficha03').replace('20261016-runtime-fix','20261016-ficha03')
p.write_text(s,encoding='utf-8')
p=D/'src/demo6/views/state-context.js';s=p.read_text(encoding='utf-8')
anchor='      <div class="d6-profile-body">'
if anchor not in s:raise ValueError('No se encontró el cuerpo de la ficha')
section='''      <section class="d6-action-plan" id="d6-action-plan" aria-labelledby="d6-action-plan-title">
        <h4 id="d6-action-plan-title">Plan de acción recomendado</h4>
        <div id="d6-action-plan-content"></div>
      </section>
'''
s=s.replace(anchor,section+anchor,1)
p.write_text(s,encoding='utf-8')

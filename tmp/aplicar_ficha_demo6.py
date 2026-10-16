from pathlib import Path
p=Path(__file__).resolve().parents[1]/'02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html'
s=p.read_text(encoding='utf-8')
s=s.replace('<script defer src="demo6.js?v=20261016-modelos"></script>','<script defer src="data/fichas_estatales.js?v=20261016-fichas"></script>\n  <script defer src="demo6-ficha.js?v=20261016-fichas"></script>\n  <script defer src="demo6.js?v=20261016-fichas"></script>')
s=s.replace('demo6.css?v=20261016-modelos','demo6.css?v=20261016-fichas')
s=s.replace('<span>03</span> Simulación','<span>03</span> Contexto')
s=s.replace('<small>SIMULACIÓN</small>','<small>CONTEXTO</small>')
s=s.replace('Simula una<br><em>acción.</em>','Conoce tu<br><em>estado.</em>')
s=s.replace('OPCIONAL<br>SUPUESTOS<br>VISIBLES','CONTEXTO<br>FUENTES<br>VISIBLES')
s=s.replace('Elige una acción, territorio y alcance para comparar escenarios. La simulación es hipotética y no demuestra un efecto causal en México.','Consulta primero los antecedentes y las fuentes de tu estado. Si eliges un municipio, esta ficha conserva su alcance estatal.')
s=s.replace('        <section class="panel intervention" id="paso-3">','        <section class="panel d6-state-profile" id="d6-state-profile" aria-label="Ficha informativa estatal" aria-live="polite"></section>\n        <details class="d6-optional-simulation"><summary>Después del contexto: explorar una simulación hipotética</summary>\n        <section class="panel intervention" id="paso-3">')
s=s.replace('</section><section class="panel evidence-brief" id="evidencia">','</section></details><section class="panel evidence-brief" id="evidencia">')
p.write_text(s,encoding='utf-8')

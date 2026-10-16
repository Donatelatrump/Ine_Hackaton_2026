from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TRACK=ROOT/'02_Prediccion_y_escenarios_de_riesgo'
p=ROOT/'ANALISIS_GENERAL_DEL_PROYECTO.md';s=p.read_text(encoding='utf-8')
s=s.replace('(../modelado/','(02_Prediccion_y_escenarios_de_riesgo/modelado/').replace('(README.md)','(02_Prediccion_y_escenarios_de_riesgo/arquitectura/README.md)')
p.write_text(s,encoding='utf-8')
for p,link in [(TRACK/'README.md','arquitectura/README.md'),(TRACK/'demo/README.md','../arquitectura/README.md')]:
 s=p.read_text(encoding='utf-8');p.write_text('## Organización actual del código\n\nDemo6 usa `demo/src/demo6/` y `demo/styles/demo6/` dentro del track. Consultar [arquitectura y comandos]('+link+'). Las capturas y copias de depuración están en `demo/archivo/depuracion/`.\n\n---\n\n'+s,encoding='utf-8')
p=TRACK/'demo/DEMO6.md';s=p.read_text(encoding='utf-8')
s=s.replace('selección común y presentación de resumen, gráfica, evaluación y escenarios.','selección común, coordinación y eventos. Las vistas descriptivas están en `src/demo6/views/`.')
p.write_text(s,encoding='utf-8')
p=ROOT/'CONTRIBUTING.md';s=p.read_text(encoding='utf-8')
s+='\n## Organización de demo6\n\nEl código actual está en `demo/src/demo6/` y los estilos propios en `demo/styles/demo6/`, dentro del track. Las vistas reciben dependencias explícitas; las fórmulas descriptivas pertenecen a `domain/analytics.js`. Consultar `arquitectura/README.md` antes de cambiar rutas. Las entradas HTML y los comandos de generadores se conservan. Los datos publicados se modifican mediante su generador.\n'
p.write_text(s,encoding='utf-8')
# Aplanar el cuerpo de las vistas: mantener helpers locales sin un render anidado redundante.
for file,fn in [('summary','renderSummary'),('history','renderHistory'),('evidence','renderEvidence')]:
 p=TRACK/f'demo/src/demo6/views/{file}.js';s=p.read_text(encoding='utf-8')
 s=s.replace('  function '+fn+'(){\n','',1)
 s=s.replace('\n  }\n\n    '+fn+'();','',1)
 p.write_text(s,encoding='utf-8')

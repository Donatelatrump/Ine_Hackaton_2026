from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
demo = root/'02_Prediccion_y_escenarios_de_riesgo/demo'
if (demo/'src/demo7/planning.js').exists():
    raise SystemExit('Demo7 ya tiene fuentes propias. Para reconstruir sus recursos usa tools/construir_demo7.py; este script solo prepara la versión inicial.')
html = (demo/'demo6.html').read_text(encoding='utf-8')
html = html.replace('assets/demo6.css?v=20261016-ficha03','assets/demo7.css?v=7-impact').replace('assets/demo6.js?v=20261016-const-fix','assets/demo7.js?v=7-impact')
html = html.replace('Demo 6','Demo 7').replace('Demo 6','Demo 7')
html = html.replace('Tres pasos · Un recorrido','RETO 2 · HACKATÓN INE 2026')
html = re.sub(r'<p class="hero-lede">.*?</p>', '<p class="hero-lede">Identifica municipios con mayor abstención estimada para 2027 y compara acciones preventivas con una cobertura definida.</p><p class="d7-project-credit">Una propuesta independiente de aguas.exe para el hackatón del INE.</p>', html)
html = html.replace('<div class="hero-actions">','<div class="hero-actions"><button class="button d7-example" id="d7-example" type="button">Ver un caso de ejemplo <span aria-hidden="true">↗</span></button>')
html = html.replace('<span class="seal-overline">HACKATHON</span>','<span class="seal-overline">PROPUESTA PARA EL</span>').replace('<span class="seal-caption">INSTITUTO NACIONAL<br>ELECTORAL</span>','<span class="seal-caption">HACKATÓN 2026<br>RETO 2 · AGUAS.EXE</span>')
html = html.replace('<div class="hero-art"','<div class="hero-art"').replace('<div class="art-orbit orbit-one">','<button id="d7-pause-motion" class="d7-pause" type="button" aria-pressed="false">Pausar animación</button><div class="art-orbit orbit-one">',1)
html = html.replace('  <main id="inicio">','  <div class="d7-context-bar" role="region" aria-label="Territorio y año de consulta"><p id="d7-context-label" aria-live="polite">Preparando territorio…</p><button id="d7-back-forecast" type="button" hidden>Volver a 2027</button><a href="#modulo-3" id="d7-context-action">Comparar acciones ↓</a></div>\n  <main id="inicio">')
html = html.replace('id="settings" open','id="settings"').replace('id="historical-settings" open','id="historical-settings"')
html = html.replace('Mapa histórico por elección','Año de consulta: histórico o proyección').replace('Ver abstención observada en año:','Elección o proyección:')
html = html.replace('<h4 id="d6-plan-comparison-title">Predicción 2027 y escenario con el plan</h4>','<h4 id="d6-plan-comparison-title">Proyección estatal y acción bajo supuestos</h4>')
html = html.replace('<p class="d6-note" id="d6-plan-comparison-note"></p>','<p class="d6-note" id="d6-plan-comparison-note"></p><button type="button" class="d7-prepare-plan" id="d7-prepare-plan">Preparar ejemplo: información práctica</button>')
html = html.replace('Consulta el plan de acción de tu estado y, debajo, explora escenarios hipotéticos de intervención.','Revisa el diagnóstico y las acciones propuestas. En la misma tarjeta, configura cobertura y compara escenarios con el mismo método de predicción.')
maps = '''<section class="d7-map-comparison" aria-labelledby="d7-maps-title"><div class="d7-block-heading"><div><span class="eyebrow">MISMO TERRITORIO · MISMA ESCALA</span><h3 id="d7-maps-title">¿Dónde cambiaría la abstención?</h3></div><button type="button" id="d7-fit-maps">Recentrar mapas</button></div><p id="d7-maps-context" class="d6-note"></p><div class="d7-map-grid"><article><h4>Sin intervención</h4><div id="d7-map-before" class="d7-map" role="region" aria-label="Mapa de abstención proyectada sin intervención"></div></article><article><h4>Con acción hipotética</h4><div id="d7-map-after" class="d7-map" role="region" aria-label="Mapa de abstención proyectada con acción hipotética"></div></article></div><div id="d7-map-legend" class="legend"></div><p class="d6-note">Los mapas comparten umbrales y encuadre. Un efecto pequeño puede no producir un cambio de categoría; consulta también la diferencia numérica. Cartografía de referencia: límites históricos sin armonizar.</p></section>'''
html = html.replace('<div id="simulation-results" hidden>','<div id="simulation-results" hidden>'+maps)
html = html.replace('href="#paso-2" data-scenario-map','href="#paso-1-map" data-scenario-map')
html = html.replace('>Opcional. Elige una acción y cuántas personas podrías alcanzar.<','>Elige una acción, define el alcance y revisa su efecto hipotético. Los resultados usan estos controles.<')
html = html.replace('La evidencia y sus límites','Evidencia, fuentes y límites')
html = html.replace('Ridge se contrasta con la referencia de la elección previa; 2021 selecciona el método y 2024 revisa su transferencia.','Se comparan cuatro modelos con una referencia de 2021. Los cortes de 2021 y 2024 participan en la selección retrospectiva; no validan 2027.')
html = html.replace('Cada corte usa únicamente datos anteriores; 2021 selecciona el método y 2024 comprueba su transferencia a una presidencial.','Cada corte usa únicamente datos anteriores. Los cortes de 2021 y 2024 participan en la selección entre cuatro modelos; no son una validación futura independiente de 2027.')
html = html.replace('Perfil CCPC observado como capa explicativa','Perfil CCPC observado y contexto de la recomendación')
html = html.replace('nunca alimenta a Ridge ni a la prioridad, y no implica causalidad.','esta ficha descriptiva se presenta por separado. El modelo usa variables agregadas históricas de edad y urbanización; ninguna asociación demuestra causalidad.')
# Reduce the first screen of evidence to a readable takeaway; keep full metrics accessible.
html = html.replace('<div class="d6-metrics-wrap">','<p id="d7-model-takeaway" class="d7-takeaway"></p><details class="d7-model-details"><summary>Ver comparación técnica de los cuatro modelos</summary><div class="d6-metrics-wrap">',1)
html = html.replace('<details><summary>Factores del modelo Ridge</summary>','</details><details><summary>Factores de Ridge (no explican los otros modelos)</summary>',1)
html = html.replace('<article id="report-status">','<article class="d7-delivery"><h3>Entrega del reto 2</h3><p>Reporte de 10–15 cuartillas, presentación de hasta 10 diapositivas, mapa con y sin intervención y base CSV/XLSX. Las cartas y el registro se verifican por separado.</p><a href="https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf" target="_blank" rel="noopener noreferrer">Consultar requisitos oficiales ↗</a></article><article id="report-status">')
html=html.replace('Proyección estatal y acción bajo supuestos','Impacto aproximado del plan estatal')
html=html.replace('<div class="d6-plan-comparison-values" id="d6-plan-comparison-values"></div>','<div class="d6-plan-comparison-values" id="d6-plan-comparison-values"></div><div class="d7-plan-impact-metrics" id="d7-plan-impact-metrics"></div>')
plan_content='<div id="d6-state-plan-content" aria-live="polite"><p class="d6-note">Selecciona un estado para consultar su plan.</p></div>'
html=html.replace(plan_content,'',1).replace('<section class="intervention" id="paso-3">',plan_content+'\n<section class="intervention" id="paso-3">',1)
(demo/'demo7.html').write_text(html,encoding='utf-8')
config=json.loads((demo/'build.config.json').read_text(encoding='utf-8'))
config['scripts']=[x for x in config['scripts'] if x!='src/demo6/ui/motion.js']
config['scripts']=[x.replace('src/demo6/controller.js','src/demo7/controller.js').replace('src/demo6/views/state-context.js','src/demo7/state-context.js') for x in config['scripts']]
config['scripts']=[x.replace('src/demo6/views/municipality.js','src/demo7/municipality.js') for x in config['scripts']]
config['scripts'].insert(-1,'src/demo7/experience.js')
config['styles'].append('styles/demo7.css')
(demo/'src/demo7').mkdir(parents=True,exist_ok=True)
controller=(demo/'src/demo6/controller.js').read_text(encoding='utf-8').replace("'Proyección exploratoria de 2027. Compara Ridge con la referencia de 2021.'", "'Proyección exploratoria de 2027 con el método seleccionado. Compara con la referencia de 2021.'")
(demo/'src/demo7/controller.js').write_text(controller,encoding='utf-8')
municipality=(demo/'src/demo6/views/municipality.js').read_text(encoding='utf-8')
municipality=municipality.replace('Capa descriptiva posterior: no alimenta a Ridge ni a la prioridad. Las diferencias frente al promedio nacional no son efectos.','Ficha descriptiva de contexto. El modelo usa proporciones agregadas históricas de edad y urbanización; esta visualización no es una explicación causal. Las diferencias frente al promedio nacional no son efectos.')
(demo/'src/demo7/municipality.js').write_text(municipality,encoding='utf-8')
state=(demo/'src/demo6/views/state-context.js').read_text(encoding='utf-8')
start=state.index('  const percentage=')
end=state.index('  runtime.renderStatePlan=')
state=state[:start]+"  function renderComparison(selection,rows){runtime.renderPlanComparison?.(selection,rows);}\n\n"+state[end:]
(demo/'src/demo7/state-context.js').write_text(state,encoding='utf-8')
(demo/'build.demo7.config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
print('Demo7 HTML, configuration and independent view sources created.')

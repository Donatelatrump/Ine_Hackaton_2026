from pathlib import Path

DEMO=Path('02_Prediccion_y_escenarios_de_riesgo/demo')


def replace(s,a,b):
    assert a in s,a[:100]
    return s.replace(a,b)


s=(DEMO/'demo6.html').read_text(encoding='utf-8')
s=s.replace('Demo 5','Demo 6').replace('Exploración municipal v2','Exploración y evidencia')
s=s.replace('<script defer src="decision.js"></script>', '<script defer src="decision.js"></script>\n  <script defer src="demo6-core.js?v=1"></script>')
for old,new in [('geografia.js?v=20261016r','demo6-geografia.js?v=1'),('buscadores.js?v=20261016m','demo6-buscadores.js?v=1'),('aplicacion.js?v=20261016q','demo6-app.js?v=1'),('demo5.js?v=20261016u','demo6-map.js?v=1')]:
    s=replace(s,old,new)
s=replace(s,'<script defer src="demo6-map.js?v=1"></script>', '<script defer src="demo6-map.js?v=1"></script>\n  <script defer src="demo6.js?v=1"></script>')
s=replace(s,'<link rel="stylesheet" href="demo5.css?v=20261016u">','<link rel="stylesheet" href="demo5.css?v=20261016u">\n  <link rel="stylesheet" href="demo6.css?v=1">')
s=s.replace('<option value="ridge" selected>','<option value="ridge">').replace('<option value="baseline">','<option value="baseline" selected>')
s=replace(s,'<label class="check"><input id="stable"','<p class="d6-note" id="d6-method-note"></p>\n         <label class="check"><input id="stable"')
s=replace(s,'<div class="workspace-top">','''<div class="d6-toolbar"><p id="d6-selection-label" aria-live="polite">Preparando consulta…</p><div><button type="button" onclick="volverAMexico()">Vista nacional</button> <button type="button" id="d6-export">Descargar consulta CSV</button></div></div>
        <div class="d6-summary" id="d6-summary" aria-live="polite"></div>
        <p class="d6-note" id="d6-summary-note"></p>
        <div class="d6-context" id="d6-context" hidden></div>
        <div class="workspace-top">''')
s=replace(s,'<section class="analysis panel" id="paso-2">','''<div class="d6-model-note" id="d6-historical-notice" hidden>Consulta histórica: este año contiene resultados observados. <button type="button" id="d6-return-2027">Ver la proyección de 2027</button></div>
        <section class="analysis panel" id="paso-2">''')
s=replace(s,'<details class="panel missing-panel" id="sin-estimacion">','''<section class="d6-chart-box" aria-labelledby="d6-history-title"><h3 id="d6-history-title">La abstención a través de las elecciones</h3>
         <div id="d6-history-chart"></div><div class="d6-chart-legend"><span>Territorio seleccionado</span><span class="reference" id="d6-reference-legend" hidden>Promedio estatal</span><span class="forecast" id="d6-forecast-legend">Proyección 2027</span></div>
         <p class="d6-note">Promedios ponderados por personas con dato de voto. Las elecciones presidenciales e intermedias tienen comportamientos distintos. Los límites municipales históricos no están armonizados; la cobertura puede cambiar entre años.</p>
         <details><summary>Consultar los valores de la gráfica</summary><div class="table-wrap"><table><thead><tr><th>Año</th><th>Abstención</th><th>Municipios con dato</th><th>Base SV+NV</th></tr></thead><tbody id="d6-history-table"></tbody></table></div></details></section>
         <section class="d6-evidence" aria-labelledby="d6-evidence-title"><h3 id="d6-evidence-title">Qué tan bien funcionaron los métodos</h3><p class="d6-model-note" id="d6-model-note"></p>
         <div class="d6-metrics-wrap"><table><thead><tr><th>Elección</th><th>Método</th><th>Municipios</th><th>Error medio (pp)</th><th>Error ponderado (pp)</th><th>Aciertos top 50</th></tr></thead><tbody id="d6-metrics"></tbody></table></div>
         <p class="d6-note">Un error menor es mejor. Los aciertos indican coincidencias entre los 50 municipios prioritarios y los 50 de mayor abstención real. 2021 participa en la selección; 2024 es una comprobación presidencial y no valida 2027.</p>
         <details><summary>Factores del modelo Ridge</summary><p class="d6-note">Coeficientes estandarizados del ajuste Ridge exportado. El signo indica dirección del ajuste condicional a las demás variables; la longitud representa su magnitud. No son porcentajes, efectos causales ni explicaciones individuales. La referencia de 2021 no utiliza estos coeficientes.</p><div class="d6-factors" id="d6-factors"></div></details></section>
         <details class="panel missing-panel" id="sin-estimacion">''')
s=replace(s,'<label for="action">¿Qué acción quieres simular?</label>','''<div class="d6-presets"><button type="button" data-d6-preset="sms">Ejemplo: 1,000 SMS</button><button type="button" data-d6-preset="call">Ejemplo: 1,000 llamadas completadas</button><button type="button" data-d6-preset="reset">Sin acción</button></div><p class="d6-note" id="d6-preset-note">Los ejemplos preparan una cobertura editable. Revisa población, canal y evidencia antes de interpretar el resultado.</p>
  <label for="action">¿Qué acción quieres simular?</label>''')
s=replace(s,'<div id="simulation-results" hidden>','''<div id="simulation-results" hidden>
  <section class="d6-scenario-compare" id="d6-scenario-comparison" hidden><h3>Abstención antes y después de la acción</h3><div id="d6-scenario-bars"></div><p class="d6-note" id="d6-scenario-detail"></p></section>''')
s=s.replace('href="../entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf"','href="../entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf"')
(DEMO/'demo6.html').write_text(s,encoding='utf-8')

s=(DEMO/'demo6-app.js').read_text(encoding='utf-8')
a=s.index("  if(typeof demo5ModoHistorico !== 'undefined' && demo5ModoHistorico && (demo5EstadoActivo || currentMapYear!==2027)){")
b=s.index('  syncSearchablePickers();',a)
s=s[:a]+s[b:]
# El motor de demo6 pinta una sola capa; los cálculos y fichas siguen en la app.
a=s.index(" const confOn=$('confidence').checked;layer.setStyle")
b=s.index(" $('confidence-note').textContent",a)
s=s[:a]+s[b:]
s=s.replace('const detailLimitText = histDemo5 ?', 'const detailLimitText = histDemo5 ?')
s=s.replace('pct(r.range_low)', 'pct(Math.max(0,r.risk-UmbralAnalytics.historicalError(metadata,$(\'method\').value)))')
s=s.replace('pct(r.range_high)', 'pct(Math.min(100,r.risk+UmbralAnalytics.historicalError(metadata,$(\'method\').value)))')
s=s.replace('±21.05 pp, p90 retrospectivo de Ridge 2021', '${UmbralAnalytics.historicalError(metadata,$(\'method\').value).toFixed(2)} pp, p90 retrospectivo de ${UmbralAnalytics.methodName($(\'method\').value)} en 2021')
s=s.replace("if(id==='state'||id==='search'){geographyFocusKey=null;", "if(id==='state'||id==='search'){geographyFocusKey=null;")
s=s.replace("$('ranking').addEventListener", "$('ranking').addEventListener")
# La nota no contiene un alpha fijo que pueda quedar obsoleto.
s=s.replace('congelados por corte.', 'congelados por corte.')
(DEMO/'demo6-app.js').write_text(s,encoding='utf-8')

s=(DEMO/'demo6-map.js').read_text(encoding='utf-8')
a=s.index('function renderStatePlan(stateKey){')
b=s.index('function initDemo5(){',a)
s=s[:a]+"function renderStatePlan(){if($('state-plan-panel'))$('state-plan-panel').hidden=true;}\n\n"+s[b:]
# En demo6 la aplicación actualiza datos y el controlador repinta sin encuadrar.
a=s.index('    const updateOriginal = update;')
b=s.index('    initDemo5();',a)
s=s[:a]+s[b:]
s=s.replace('if(!demo5ModoHistorico || !demo5LayerMunicipal) return;', 'if(!demo5LayerMunicipal) return;')
s=s.replace("    if(paneState) paneState.style.visibility = 'visible';", "    if(paneState) paneState.style.visibility = 'visible';")
# No mostrar los polígonos nativos detrás de los de demo6.
s=s.replace("  const esPrediccion2027 = (year === 2027);  const enEstado = demo5EstadoActivo;", "  const esPrediccion2027 = (year === 2027);  const enEstado = demo5EstadoActivo;\n  layer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});\n  stateLayer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});")
s=s.replace('reconstruirMapa(year);','reconstruirMapa(currentMapYear);')
# El clic en estado reinicia el foco antes de refrescar los datos.
s=s.replace('        demo5EstadoActivo = state;\n        sincronizarSelectores(state);\n        $(\'search\').value = \'\';', "        demo5EstadoActivo = state;\n        geographyFocusKey=null;activeKey=null;\n        $('search').value='';\n        sincronizarSelectores(state);")
s=s.replace("  demo5EstadoActivo = stateKey || null;", "  demo5EstadoActivo = stateKey || null;\n  geographyFocusKey=null;activeKey=null;")
s=s.replace("function volverAMexico(){\n  demo5EstadoActivo = null;", "function volverAMexico(){\n  geographyFocusKey=null;activeKey=null;geographyHistory.length=0;\n  demo5EstadoActivo = null;")
s=s.replace('  reconstruirMapa(currentMapYear);\n}\n\n/* Cambiar', '  update();\n  reconstruirMapa(currentMapYear);\n}\n\n/* Cambiar')
s=s.replace('guarda la vista anterior', 'guarda la vista anterior')
(DEMO/'demo6-map.js').write_text(s,encoding='utf-8')

s=(DEMO/'demo6-geografia.js').read_text(encoding='utf-8')
a=s.index('function goBackGeography() {')
b=s.index('const municipalBaseStyles',a)
s=s[:a]+'''function goBackGeography() {
 if(geographyFocusKey || $('search').value){
  geographyFocusKey=null;activeKey=null;geographyHistory.length=0;
  $('search').value='';
  update();paintMunicipalityFocus();
  const polygon=stateLayer.getLayers().find(p=>p.feature.properties.state===$('state').value);
  if(polygon)map.fitBounds(polygon.getBounds(),{padding:[12,12],animate:true});
 } else if($('state').value){volverAMexico();}
}
'''+s[b:]
a=s.index('function updateGeography(dataChanged = true) {')
s=s[:a]+s[a:].replace('function updateGeography(dataChanged = true) {','function updateGeography(dataChanged = true) {\n  if(typeof demo5Iniciado!==\'undefined\' && demo5Iniciado)return;',1)
(DEMO/'demo6-geografia.js').write_text(s,encoding='utf-8')

s=(DEMO/'demo6-buscadores.js').read_text(encoding='utf-8')
a=s.index("   $('search').value=option.label;")
b=s.index('\n  });',a)
s=s[:a]+"   if(window.Umbral6){window.Umbral6.selectMunicipality(option.key);}\n   else { $('search').value=option.label; $('search').dispatchEvent(new Event('input',{bubbles:true})); }"+s[b:]
(DEMO/'demo6-buscadores.js').write_text(s,encoding='utf-8')
print('Demo6 preparada con archivos propios.')

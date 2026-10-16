function initMapLayers(){
  if(mapInitialized){return;}
  mapInitialized = true;
  map.attributionControl.addAttribution('Islas: INEGI · Marco Geoestadístico 2025');
  // Evitar la escala temporal del SVG: Leaflet reproyecta los trazos al finalizar
  // y produce un salto visible en los bordes y en la geometría simplificada.
  const fitBoundsDemo5 = map.fitBounds.bind(map);
  let transicionVista = null;
  map.fitBounds = function(bounds, options = {}){
    map.stop();
    if(transicionVista){
      transicionVista.cancel();
      transicionVista = null;
    }
    const resultado = fitBoundsDemo5(bounds, {...options, animate:false});
    // Animar la aparición de la nueva vista, sin escalar los trazos del SVG.
    // El encuadre se aplica de inmediato para mantener sincronizada la navegación.
    const pane = map.getPane('mapPane');
    if(pane && pane.animate && options.animate !== false &&
       !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      transicionVista = pane.animate(
        [{opacity:0}, {opacity:1}],
        {duration:260, easing:'ease-out'}
      );
    }
    return resultado;
  };
  console.log('Umbral map: inicializando');
  populateMapYearSelector();
  const sel = $('map-year');
  if(sel){
    sel.addEventListener('change',()=>{
      const y = Number(sel.value);
      if(!isNaN(y)){
        historicalMapEnabled = true;
        currentMapYear = y;
        activeMapState = $('state').value || null;
        updateExplorationAnalysis();
        renderStatePlan(activeMapState);
        if(!activeMapState && $('state-plan-panel')){$('state-plan-panel').hidden=true;}
        reconstruirMapa(y,{encuadrar:false});
      }
    });
  }
  if($('search')){
    $('search').addEventListener('input',()=>{
      const exact = records.find(r=>r.state===activeMapState && (r.key===$('search').value||r.name===$('search').value));
      if(exact && activeMapState){
        renderStatePlan(activeMapState);
      }
    });
  }
  const stateInput=$('state-picker');
  if(stateInput){
    stateInput.addEventListener('input',()=>{  if(activeMapState&&historicalMapEnabled&&$('state').value){
        renderStatePlan(activeMapState);
      }
    });
  }
  map.on('contextmenu', syncMapLevel);
  reconstruirMapa(currentMapYear);
  console.log('Umbral map: listo');
}


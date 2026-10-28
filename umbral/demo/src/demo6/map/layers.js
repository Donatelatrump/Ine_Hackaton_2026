function removeMapLayers(){
  if(contextLayer){
    map.removeLayer(contextLayer);
    contextLayer=null;
  }
  if(municipalityLayer){
    try{map.removeLayer(municipalityLayer);}catch(e){}
    municipalityLayer = null;
  }
  if(stateOverlayLayer){
    try{map.removeLayer(stateOverlayLayer);}catch(e){}
    stateOverlayLayer = null;
  }
  if(boundaryLayer){
    try{map.removeLayer(boundaryLayer);}catch(e){}
    boundaryLayer = null;
  }
}

function limpiarPaneMunicipalNativo(){
  if(typeof map==='undefined' || !map) return;
  const paneMun = map.getPane && map.getPane('municipal-geography');
  if(paneMun) paneMun.style.visibility = 'visible';
}

function limpiarPaneEstadoNativo(){
  if(typeof map==='undefined' || !map) return;
  const paneState = map.getPane && map.getPane('state-geography');
  if(paneState) paneState.style.visibility = 'visible';
}

function cerrarPickers(){
  if(typeof statePicker!=='undefined' && statePicker && typeof statePicker.close==='function'){statePicker.close();}
  if(typeof municipalityPicker!=='undefined' && municipalityPicker && typeof municipalityPicker.close==='function'){municipalityPicker.close();}
}

function sincronizarSelectores(stateKey){
  const selEstado = $('state');
  if(!selEstado) return;
  if(selEstado.value !== stateKey){
    selEstado.value = stateKey;
  }
  cerrarPickers();
  const searchInput = $('search');
  const munToggle = $('municipality-toggle');
  if(searchInput){
    searchInput.disabled = !stateKey;
    searchInput.placeholder = stateKey ? 'Escribe o elige un municipio' : 'Elige primero un estado';
  }
  if(munToggle){munToggle.disabled = !stateKey;}
  const statePickerInput = $('state-picker');
  if(typeof pickerState==='undefined' || pickerState !== stateKey){
    pickerState = stateKey;
    if(statePickerInput && statePickerInput.value != (stateKey?'—':'Todo México')){
      statePickerInput.value = stateKey ? (records.find(r=>r.state===stateKey)?.state_name || stateKey) : 'Todo México';
      if(typeof statePicker!=='undefined' && statePicker && typeof statePicker.close==='function'){statePicker.close();}
    }
  }
  if(stateKey && searchInput){
    const exact = records.find(r=>r.state===stateKey && (r.key===searchInput.value || r.name===searchInput.value));
    if(!exact && searchInput.value) searchInput.value = '';
  }
  if(stateKey){
    const planPanel = $('state-plan-panel');
    if(planPanel){planPanel.hidden = false;}
    renderStatePlan(stateKey);
  } else {
    const planPanel = $('state-plan-panel');
    if(planPanel){planPanel.hidden = true;}
  }
  const mapYear = $('map-year');
  if(mapYear){mapYear.disabled = false;}
  if(stateKey && mapInitialized && historicalMapEnabled){ update(); }
}

function crearLayerMunicipioEstado(year, estadoSeleccionado){
  if(!municipalityRenderer){
    municipalityRenderer = L.svg({pane:'municipal-geography'});
  }
  return L.geoJSON(window.UMBRAL_GEO,{
    filter:f=>byKey.get(f.properties.key)?.state === estadoSeleccionado,
    noClip:true,
    bubblingMouseEvents:false,
    renderer: municipalityRenderer,
    onEachFeature:(f,l)=>{
      const r=byKey.get(f.properties.key);
      if(!r) return;
      const node=document.createElement('span');
      node.textContent=r.name+' · '+r.key;
      l.bindTooltip(node);
      l.on('click',(ev)=>{
        L.DomEvent.stopPropagation(ev);
        const clave = f.properties.key;
        const mun = byKey.get(clave);
        map.stop();
        // focusMunicipality guarda la vista anterior antes de seleccionar el municipio.
        if(typeof focusMunicipality==='function'){
          focusMunicipality(clave,l);
        } else {
          if(mun && $('search')){ $('search').value = mun.name; }
          map.fitBounds(l.getBounds(),{padding:[30,30],maxZoom:10,animate:true});
        }
      });
    },
    style: estiloMunicipal(year, estadoSeleccionado)
  });
}

function paintMapSelection(){
  if(!municipalityLayer) return;
  const base=estiloMunicipal(currentMapYear,activeMapState);
  municipalityLayer.eachLayer(polygon=>{
    const key=polygon.feature.properties.key;
    const selected=key===geographyFocusKey;
    polygon.setStyle({...base(polygon.feature),
      ...(selected?{fillOpacity:1,opacity:1,weight:2}: {})});
    const path=polygon.getElement();
    if(path){
      path.classList.toggle('municipality-out-of-focus',!!geographyFocusKey && !selected);
    }
    if(selected)polygon.bringToFront();
  });
}

function ocultarCapasMunicipalesNativasEnPane(paneMun){
  if(typeof map==='undefined' || !map) return;
  if(!paneMun) return;
  map.eachLayer(l=>{
    if(l && l.options && l.options.pane === paneMun && l !== municipalityLayer && l !== boundaryLayer){
      try{ l.setStyle({fillOpacity:0,opacity:0,color:'#000000',weight:0}); }catch(e){}
    }
  });
}

function ocultarCapasMunicipalesNativas(){
  const paneMun = map.getPane && map.getPane('municipal-geography');
  ocultarCapasMunicipalesNativasEnPane(paneMun);
}

function reconstruirMapa(year, {encuadrar=true}={}){
  if(typeof map === 'undefined' || !map ||
     typeof byKey === 'undefined' || !byKey ||
     typeof thresholds === 'undefined' ||
     typeof window === 'undefined' || !window.UMBRAL_GEO ||
     !window.UMBRAL_STATES){
    console.warn('Umbral map: dependencias no listas');
    return;
  }
  const esPrediccion2027 = (year === 2027);  const enEstado = activeMapState;
  layer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});
  stateLayer.eachLayer(p=>{const path=p.getElement();if(path)path.style.display='none';});

  /* Control de panes originales ANTES de tocar capas, para que no se pinte sobre lo viejo */
  const paneMun = map.getPane && map.getPane('municipal-geography');
  const paneState = map.getPane && map.getPane('state-geography');
  if(enEstado){
    if(paneState) paneState.style.visibility = 'hidden';
    if(paneMun) paneMun.style.visibility = 'visible';
  } else {
    if(paneState) paneState.style.visibility = 'visible';
    if(paneMun) paneMun.style.visibility = 'hidden';
  }

  if(enEstado){
    /* Reutilizar los municipios mientras siga seleccionada la misma entidad. */
    if(!municipalityLayer || !map.hasLayer(municipalityLayer) || municipalityLayerState !== enEstado){
      if(municipalityLayer && map.hasLayer(municipalityLayer)){ try{map.removeLayer(municipalityLayer);}catch(e){} municipalityLayer=null; }
      if(contextLayer){map.removeLayer(contextLayer);}
      if(!municipalityRenderer){municipalityRenderer=L.svg({pane:'municipal-geography'});}
      contextLayer=L.geoJSON(window.UMBRAL_STATES,{
        filter:f=>f.properties.state!==enEstado,
        renderer:municipalityRenderer,
        noClip:true,
        interactive:false,
        className:'state-out-of-focus',
        style:estiloEstado(year)
      }).addTo(map);
      municipalityLayer = crearLayerMunicipioEstado(year, enEstado).addTo(map);
      municipalityLayerState = enEstado;
      ocultarCapasMunicipalesNativas();
    } else {
      municipalityLayer.setStyle(estiloMunicipal(year, enEstado));
      if(contextLayer){contextLayer.setStyle(estiloEstado(year));}
    }

    paintMapSelection();
    if(!boundaryLayer){
      boundaryLayer = L.geoJSON(window.UMBRAL_STATES,{
        noClip:true,
        renderer: municipalityRenderer,
        style: {color:'#000000',weight:1.2,fillOpacity:0,opacity:.7,clickable:false},
        interactive:false
      }).addTo(map);
    }
    boundaryLayer.eachLayer(polygon=>{
      polygon.getElement()?.classList.toggle('state-out-of-focus',polygon.feature.properties.state!==enEstado);
    });

    const polyEstado = stateLayer ? stateLayer.getLayers().find(p=>p.feature.properties.state===enEstado) : null;
    if(polyEstado && encuadrar){ map.stop(); map.fitBounds(polyEstado.getBounds(),{padding:[12,12],maxZoom:9,animate:true,duration:.25}); }
  } else {
    if(municipalityLayer){map.removeLayer(municipalityLayer);municipalityLayer=null;}
    if(contextLayer){map.removeLayer(contextLayer);contextLayer=null;}
    if(boundaryLayer){map.removeLayer(boundaryLayer);boundaryLayer=null;}
    if(!stateRenderer){stateRenderer=L.svg({pane:'state-geography'});}

    /* VISTA NACIONAL: capa de estados + límites */
    if(!stateOverlayLayer){
    stateOverlayLayer = L.geoJSON(window.UMBRAL_STATES,{
      noClip:true,
      renderer: stateRenderer,
      onEachFeature:(f,l)=>{
        const state=f.properties.state;
        const name = records.find(r=>r.state===state)?.state_name || state;
      l.bindTooltip(name+' · '+state);
      l.on('click',(ev)=>{
        L.DomEvent.stopPropagation(ev);
        activeMapState = state;
        geographyFocusKey=null;activeKey=null;
        $('search').value='';
        sincronizarSelectores(state);
        reconstruirMapa(currentMapYear);
      });
      },
      style: estiloEstado(year)
    });    stateOverlayLayer.addTo(map);
    }
    stateOverlayLayer.bringToFront();
    stateOverlayLayer.setStyle(estiloEstado(year));
    if(encuadrar){map.fitBounds(stateOverlayLayer.getBounds(),{padding:[12,12],animate:true});}

    /* En vista nacional el pane municipal permanece oculto: solo se muestran los colores promedio de estado. */
    limpiarPaneEstadoNativo();
  }

  /* Actualizar textos */
  if($('map-caption')){
    $('map-caption').textContent = esPrediccion2027 ?
      'Estimación exploratoria para 2027. Colores por tercios del método activo. Gris = sin estimación.' :
      'Abstención observada en la elección de ' + year + '. Colores por tercios del método activo. Gris = sin dato en ese año.';
  }
  const legend = document.querySelector('.legend');
  if(legend){
    legend.innerHTML =
      '<span><i class="low" style="background:'+colors.bajo+'"></i>Menor abstención</span>' +
      '<span><i class="medium" style="background:'+colors.medio+'"></i>Intermedia</span>' +
      '<span><i class="high" style="background:'+colors.alto+'"></i>Mayor abstención</span>' +
      '<span><i class="missing"></i>'+(esPrediccion2027?'Sin estimación':'Sin dato en '+year)+'</span>';
  }
  const guide = document.querySelector('.map-guide');
  if(guide){
    guide.textContent = esPrediccion2027 ?
      'Mapa de estimación 2027: los estados se colorean con su abstención promedio estimada para 2027. Click en un estado para ver municipios.' :
      'Mapa histórico: los estados se colorean con su abstención promedio observada en '+year+'. Click en un estado para explorar municipios.';
  }
  console.log('Umbral map: mapa reconstruido para año', year, esPrediccion2027 ? '(estimación 2027)' : '(histórico)', enEstado ? 'estado:'+enEstado : 'nacional');
  document.dispatchEvent(new CustomEvent('umbral:maprebuilt'));
}


/* ===== DEMO 5: mapa histórico por año y plan recomendado por estado ===== */
let currentMapYear = 2027;
let demo5Iniciado = false;
let demo5ModoHistorico = true;
let demo5LayerMunicipal = null;
let demo5LayerEstado = null;
let demo5LayerLimites = null;
let demo5LayerContexto = null;
let demo5EstadoActivo = null;
let demo5EstadoCapaMunicipal = null;
let demo5RendererMunicipal = null;

function getAvailableYears(){
  const years = new Set();
  if(typeof records === 'undefined' || !records) return [2027];
  for(const r of records){
    for(const h of (r.history||[])){
      if(Number.isFinite(h.year)){
        years.add(h.year);
      }
    }
  }
  years.add(2027);
  return [...years].sort((a,b)=>a-b);
}

function populateMapYearSelector(){
  const sel = $('map-year');
  if(!sel){return;}
  sel.replaceChildren();
  const years = getAvailableYears();
  for(const y of years){
    sel.add(new Option(String(y),String(y)));
  }
  if(years.length){sel.value = String(currentMapYear);}
  console.log('demo5: años disponibles:', years);
}

function stateRiskLevel(stateKey){
  if(typeof records === 'undefined' || !records) return {level:'sin_datos',label:'Sin datos',promedio:null,n:0};
  const stR = records.filter(r=>r.state===stateKey && Number.isFinite(r.risk));
  if(!stR.length){
    return {level:'sin_datos',label:'Sin datos',promedio:null,n:0};
  }
  const obs = stR.reduce((s,r)=>s+r.observed,0);
  const prom = obs ? stR.reduce((s,r)=>s+r.risk*r.observed,0)/obs : 0;
  let level='bajo';
  if(typeof thresholds !== 'undefined'){
    if(prom>=thresholds.high){level='alto';}
    else if(prom>=thresholds.low){level='medio';}
  }
  return {level:level,label:level==='alto'?'Rojo':level==='medio'?'Amarillo':'Verde',promedio:prom,n:stR.length};
}

function getJovenesPoblacionEstado(stateKey){
  if(typeof records === 'undefined' || !records) return {jovenes:0,total:0};
  const st = records.filter(r=>r.state===stateKey);
  let jovenes = 0;
  let total = 0;
  for(const r of st){
    const p=r.profile||{};
    if(Number.isFinite(p.young_pct) && Number.isFinite(r.ln)){
      jovenes += r.ln*(p.young_pct/100);
      total += r.ln;
    }
  }
  return {jovenes:Math.round(jovenes),total:Math.round(total)};
}

function calcularImpactoTeorico(poblacionJoven, abstencionPct){
  const tasa = abstencionPct/100;
  const posiblesNoVotan = poblacionJoven*tasa;
  const escenarios = [
    {label:'SMS (Suecia)', pp:0.30},
    {label:'Llamada plan de voto (EEUU)', pp:4.1},
    {label:'Campaña digital jóvenes (supuesto)', pp:2.0},
    {label:'Info institucional (supuesto)', pp:1.5}
  ];
  return escenarios.map(e=>{
    const reduccion = poblacionJoven*(e.pp/100);
    const votosAdicionales = Math.max(0, Math.min(reduccion, posiblesNoVotan));
    return {label:e.label, pp:e.pp, votosAdicionales:Math.round(votosAdicionales), reduccionPp:e.pp};
  });
}

function estiloMunicipal(year, estadoSeleccionado){
  return function(feature){
    const r = byKey.get(feature.properties.key);
    if(!r){return {color:'#000000',weight:1.2,fillColor:colors.sin_datos,fillOpacity:.85,opacity:1};}
    const esPrediccion2027 = (year === 2027);
    let rate = null;
    if(esPrediccion2027){
      rate = Number.isFinite(r.risk) ? r.risk : null;
    } else {
      const h = r.history.find(x=>x.year===year);
      rate = h && Number.isFinite(h.risk) ? h.risk : null;
    }
    let color = colors.sin_datos;
    if(rate!==null){
      color = rate>=thresholds.high ? colors.alto : rate>=thresholds.low ? colors.medio : colors.bajo;
    }
    const esDelEstado = estadoSeleccionado && r.state === estadoSeleccionado;
    return {
      color:'#000000',
      weight: esDelEstado ? 1.2 : .3,
      fillColor: color,
      fillOpacity: esDelEstado ? .85 : .20,
      opacity: esDelEstado ? 1 : .30
    };
  };
}

function estiloEstado(year){
  return function(feature){
    const state = feature.properties.state;
    const munis = records.filter(r=>r.state===state);
    let rate = null;
    if(munis.length){
      const esPrediccion2027 = (year === 2027);
      if(esPrediccion2027){
        const vals = munis.map(r=>r.risk).filter(Number.isFinite);
        rate = vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;
      } else {
        const vals = munis.map(r=>{
          const h=r.history.find(x=>x.year===year);
          return h&&Number.isFinite(h.risk)?h.risk:null;
        }).filter(Number.isFinite);
        rate = vals.length?vals.reduce((a,b)=>a+b,0)/vals.length:null;
      }
    }
    let color = colors.sin_datos;
    if(rate!==null){
      color = rate>=thresholds.high ? colors.alto : rate>=thresholds.low ? colors.medio : colors.bajo;
    }
    return {color:'#000000',weight:1,fillColor:color,fillOpacity:.85,opacity:1};
  };
}

function removerCapasDemo5(){
  if(demo5LayerContexto){
    map.removeLayer(demo5LayerContexto);
    demo5LayerContexto=null;
  }
  if(demo5LayerMunicipal){
    try{map.removeLayer(demo5LayerMunicipal);}catch(e){}
    demo5LayerMunicipal = null;
  }
  if(demo5LayerEstado){
    try{map.removeLayer(demo5LayerEstado);}catch(e){}
    demo5LayerEstado = null;
  }
  if(demo5LayerLimites){
    try{map.removeLayer(demo5LayerLimites);}catch(e){}
    demo5LayerLimites = null;
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
  if(stateKey && demo5Iniciado && demo5ModoHistorico){ update(); }
}

function crearLayerMunicipioEstado(year, estadoSeleccionado){
  if(!demo5RendererMunicipal){
    demo5RendererMunicipal = L.svg({pane:'municipal-geography'});
  }
  return L.geoJSON(window.UMBRAL_GEO,{
    filter:f=>byKey.get(f.properties.key)?.state === estadoSeleccionado,
    noClip:true,
    bubblingMouseEvents:false,
    renderer: demo5RendererMunicipal,
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

function demo5PintarSeleccionMunicipal(){
  if(!demo5ModoHistorico || !demo5LayerMunicipal) return;
  const base=estiloMunicipal(currentMapYear,demo5EstadoActivo);
  demo5LayerMunicipal.eachLayer(polygon=>{
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
    if(l && l.options && l.options.pane === paneMun && l !== demo5LayerMunicipal && l !== demo5LayerLimites){
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
    console.warn('demo5: dependencias no listas');
    return;
  }
  const esPrediccion2027 = (year === 2027);  const enEstado = demo5EstadoActivo;

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
    if(!demo5LayerMunicipal || !map.hasLayer(demo5LayerMunicipal) || demo5EstadoCapaMunicipal !== enEstado){
      if(demo5LayerMunicipal && map.hasLayer(demo5LayerMunicipal)){ try{map.removeLayer(demo5LayerMunicipal);}catch(e){} demo5LayerMunicipal=null; }
      if(demo5LayerContexto){map.removeLayer(demo5LayerContexto);}
      if(!demo5RendererMunicipal){demo5RendererMunicipal=L.svg({pane:'municipal-geography'});}
      demo5LayerContexto=L.geoJSON(window.UMBRAL_STATES,{
        filter:f=>f.properties.state!==enEstado,
        renderer:demo5RendererMunicipal,
        noClip:true,
        interactive:false,
        className:'state-out-of-focus',
        style:estiloEstado(year)
      }).addTo(map);
      demo5LayerMunicipal = crearLayerMunicipioEstado(year, enEstado).addTo(map);
      demo5EstadoCapaMunicipal = enEstado;
      ocultarCapasMunicipalesNativas();
    } else {
      demo5LayerMunicipal.setStyle(estiloMunicipal(year, enEstado));
      if(demo5LayerContexto){demo5LayerContexto.setStyle(estiloEstado(year));}
    }

    demo5PintarSeleccionMunicipal();
    if(!demo5LayerLimites){
      demo5LayerLimites = L.geoJSON(window.UMBRAL_STATES,{
        noClip:true,
        renderer: demo5RendererMunicipal,
        style: {color:'#000000',weight:1.2,fillOpacity:0,opacity:.7,clickable:false},
        interactive:false
      }).addTo(map);
    }
    demo5LayerLimites.eachLayer(polygon=>{
      polygon.getElement()?.classList.toggle('state-out-of-focus',polygon.feature.properties.state!==enEstado);
    });

    const polyEstado = stateLayer ? stateLayer.getLayers().find(p=>p.feature.properties.state===enEstado) : null;
    if(polyEstado && encuadrar){ map.stop(); map.fitBounds(polyEstado.getBounds(),{padding:[12,12],maxZoom:9,animate:true,duration:.25}); }
  } else {
    removerCapasDemo5();

    /* VISTA NACIONAL: capa de estados + límites */
    demo5LayerEstado = L.geoJSON(window.UMBRAL_STATES,{
      noClip:true,
      renderer: L.svg({pane:'state-geography'}),
      onEachFeature:(f,l)=>{
        const state=f.properties.state;
        const name = records.find(r=>r.state===state)?.state_name || state;
      l.bindTooltip(name+' · '+state);
      l.on('click',(ev)=>{
        L.DomEvent.stopPropagation(ev);
        demo5EstadoActivo = state;
        sincronizarSelectores(state);
        $('search').value = '';
        reconstruirMapa(year);
      });
      },
      style: estiloEstado(year)
    });    demo5LayerEstado.addTo(map);
    demo5LayerEstado.bringToFront();
    demo5LayerEstado.setStyle(estiloEstado(year));
    if(encuadrar){map.fitBounds(demo5LayerEstado.getBounds(),{padding:[12,12],animate:true});}

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
  console.log('demo5: mapa reconstruido para año', year, esPrediccion2027 ? '(estimación 2027)' : '(histórico)', enEstado ? 'estado:'+enEstado : 'nacional');
}

function volverAMexico(){
  demo5EstadoActivo = null;
  if($('state')){$('state').value='';}
  if($('search')){$('search').value='';}
  const mapYear=$('map-year');
  if(mapYear){mapYear.disabled=false;}
  sincronizarSelectores(null);
  reconstruirMapa(currentMapYear);
}

/* Cambiar de entidad desde el buscador tiene que rehacer las capas y los paneles del modo histórico.
   El buscador solo actualiza el <select> y dispara input/change; en modo histórico update() y
   updateGeography() se saltan el cambio de nivel, así que sin este paso la escala quedaba nacional
   con el panel municipal visible (divisiones por municipio sobre todo el país) y la bandera obsoleta. */
function demo5SeleccionarEstado(stateKey){
  demo5EstadoActivo = stateKey || null;
  if($('search')){ $('search').value = ''; }
  sincronizarSelectores(demo5EstadoActivo);
  /* En modo histórico el nivel del mapa (paneles y encuadre) lo decide demo5; tras una
     simulación manda la app base, que ya ajusta paneles y encuadre por su cuenta. */
  if(typeof demo5ModoHistorico !== 'undefined' && demo5ModoHistorico){ reconstruirMapa(currentMapYear); }
}

/* Red de seguridad de la vuelta atras (clic derecho): el nivel del mapa tiene que coincidir con el
   selector de estado. Si un clic derecho termina a escala nacional pero la capa de municipios sigue
   a la vista, se ven las divisiones por municipio sobre los estados; aqui se reconstruye el nivel. */
function demo5SincronizarNivel(){
  if(typeof map === 'undefined' || !map) return;
  if(typeof demo5ModoHistorico === 'undefined' || !demo5ModoHistorico) return;  /* en modo simulacion manda la app base */
  const esperado = $('state') ? ($('state').value || '') : '';
  const paneMunicipal = map.getPane && map.getPane('municipal-geography');
  const municipiosALaVista = !!(paneMunicipal && paneMunicipal.style.visibility === 'visible');
  if(esperado === (demo5EstadoActivo || '') && (esperado || !municipiosALaVista)) return;
  demo5EstadoActivo = esperado || null;
  sincronizarSelectores(demo5EstadoActivo);
  if(!esperado){
    if($('search')){$('search').value = '';}
    const mapYear = $('map-year');
    if(mapYear){mapYear.disabled = false;}
  }
  reconstruirMapa(currentMapYear);
}

function renderStatePlan(stateKey){
  const panel = $('state-plan-panel');
  const content = $('state-plan-content');
  if(!panel || !content){return;}
  if(demo5ModoHistorico && currentMapYear!==2027){panel.hidden=true;return;}
  panel.hidden = false;
  if(typeof records === 'undefined' || !records){return;}
  const rState = records.find(r=>r.state===stateKey);
  const level = stateRiskLevel(stateKey);
  const jovenes = getJovenesPoblacionEstado(stateKey);
  const nombreEstado = rState ? rState.state_name : 'Estado';
  const claseRiesgo = level.level==='alto' ? 'risk-rojo' : level.level==='medio' ? 'risk-amarillo' : 'risk-verde';
  const impactos = calcularImpactoTeorico(jovenes.jovenes, level.promedio||0);

  const botones = impactos.map(e=>{
    return '<button type="button" class="primary" onclick="simularImpactoEstado(\''+esc(stateKey)+'\', \''+esc(e.label)+'\', '+e.pp+', '+jovenes.jovenes+')">'+esc(e.label)+' · ≈ '+fmt.format(e.votosAdicionales)+' votos</button>';
  }).join('');

  const btnEstado = '<button type="button" onclick="simularEstadoCompleto(\''+esc(stateKey)+'\')">Simular todos los municipios del estado →</button>';
  const btnVolver = '<button type="button" onclick="volverAMexico()">← Volver a vista nacional</button>';

  let html =
    '<div class="plan-card '+claseRiesgo+'">' +
    '<h4>'+esc(nombreEstado)+' · Clave '+stateKey+'</h4>' +
    '<div class="plan-grid">' +
    '<div class="plan-item"><strong>'+fmt.format(level.n)+'</strong><small>municipios con estimación</small></div>' +
    '<div class="plan-item"><strong>'+(level.promedio===null?'—':level.promedio.toFixed(1)+'%')+'</strong><small>abstención promedio (territorio)</small></div>' +
    '<div class="plan-item"><strong>'+fmt.format(jovenes.jovenes)+'</strong><small>jóvenes 18–29 estimados (base SV+NV)</small></div>' +
    '<div class="plan-item"><strong>'+level.label+'</strong><small>nivel de riesgo estatal</small></div>' +
    '</div>' +
    '<p class="hint">Plan recomendado para un estado '+level.label.toLowerCase()+'. Impacto teórico sobre población joven 18–29, supuestos no causales.</p>' +
    '<div class="plan-actions">'+botones+btnEstado+btnVolver+'</div>' +
    '<p class="hint">Los votos adicionales son una estimación supuesta (población joven × tasa de abstención × efecto pp). No son personas observadas ni efecto probado.</p>' +
    '</div>';
  content.innerHTML = html;
}

function simularImpactoEstado(stateKey, accion, pp, poblacionJoven){
  if(typeof applySimulationScope !== 'function'){return;}
  $('simulation-scope').value='estado';
  $('simulation-state').value=stateKey;
  applySimulationScope();
  if($('action')){$('action').value='personalizada';}
  if($('reach')){$('reach').value=poblacionJoven;}
  if($('simulation-inputs')){$('simulation-inputs').hidden=false;}
  if(typeof update === 'function'){update();}
  demo5ModoHistorico = false;
  demo5EstadoActivo = stateKey;
}

function simularEstadoCompleto(stateKey){
  if(typeof applySimulationScope !== 'function'){return;}
  $('simulation-scope').value='estado';
  $('simulation-state').value=stateKey;
  applySimulationScope();
  if($('simulation-map-controls')){$('simulation-map-controls').hidden=false;}
  if($('confidence')){$('confidence').checked=false;}
  if(typeof update === 'function'){update();}
  demo5ModoHistorico = false;
  demo5EstadoActivo = stateKey;
}

function initDemo5(){
  if(demo5Iniciado){return;}
  demo5Iniciado = true;
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
  console.log('demo5: inicializando');
  populateMapYearSelector();
  const sel = $('map-year');
  if(sel){
    sel.addEventListener('change',()=>{
      const y = Number(sel.value);
      if(!isNaN(y)){
        demo5ModoHistorico = true;
        currentMapYear = y;
        demo5EstadoActivo = $('state').value || null;
        updateExplorationAnalysis();
        renderStatePlan(demo5EstadoActivo);
        if(!demo5EstadoActivo && $('state-plan-panel')){$('state-plan-panel').hidden=true;}
        reconstruirMapa(y,{encuadrar:false});
      }
    });
  }
  if($('search')){
    $('search').addEventListener('input',()=>{
      const exact = records.find(r=>r.state===demo5EstadoActivo && (r.key===$('search').value||r.name===$('search').value));
      if(exact && demo5EstadoActivo){
        renderStatePlan(demo5EstadoActivo);
      }
    });
  }
  const stateInput=$('state-picker');
  if(stateInput){
    stateInput.addEventListener('input',()=>{  if(demo5EstadoActivo&&demo5ModoHistorico&&$('state').value){
        renderStatePlan(demo5EstadoActivo);
      }
    });
  }
  map.on('contextmenu', demo5SincronizarNivel);
  reconstruirMapa(currentMapYear);
  console.log('demo5: listo');
}

/* Espera a que aplicacion.js defina todo, luego envuelve update para forzar repintado */
const demo5Timer = setInterval(() => {
  const listo = typeof records !== 'undefined' && records &&
                typeof map !== 'undefined' && map &&
                typeof byKey !== 'undefined' && byKey &&
                typeof thresholds !== 'undefined' && thresholds &&
                typeof update === 'function' &&
                typeof window !== 'undefined' && window.UMBRAL_GEO &&
                typeof window !== 'undefined' && window.UMBRAL_STATES;
  if (listo && !demo5Iniciado) {
    clearInterval(demo5Timer);
    const updateOriginal = update;
    update = function(){
      const resultado = updateOriginal.apply(this, arguments);
      if(demo5ModoHistorico && typeof currentMapYear !== 'undefined'){
        if(!demo5EstadoActivo){
          requestAnimationFrame(()=>{
            if(demo5ModoHistorico && !demo5EstadoActivo){ reconstruirMapa(currentMapYear); }
          });
        }
      }
      return resultado;
    };
    initDemo5();
    window.addEventListener('beforeunload', ()=>{ window.__backToNacional._demo5Attached = true; });
  }
}, 50);

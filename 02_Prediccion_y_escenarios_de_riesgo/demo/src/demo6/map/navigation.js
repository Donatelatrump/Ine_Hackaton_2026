function volverAMexico(){
  geographyFocusKey=null;activeKey=null;geographyHistory.length=0;
  activeMapState = null;
  if($('state')){$('state').value='';}
  if($('search')){$('search').value='';}
  const mapYear=$('map-year');
  if(mapYear){mapYear.disabled=false;}
  sincronizarSelectores(null);
  update();
  reconstruirMapa(currentMapYear);
}

/* Cambiar de entidad desde el buscador tiene que rehacer las capas y los paneles del modo histórico.
   El buscador solo actualiza el <select> y dispara input/change; en modo histórico update() y
   updateGeography() se saltan el cambio de nivel, así que sin este paso la escala quedaba nacional
   con el panel municipal visible (divisiones por municipio sobre todo el país) y la bandera obsoleta. */
function selectMapState(stateKey){
  activeMapState = stateKey || null;
  geographyFocusKey=null;activeKey=null;
  if($('search')){ $('search').value = ''; }
  sincronizarSelectores(activeMapState);
  /* En modo histórico el nivel del mapa (paneles y encuadre) lo decide demo5; tras una
     simulación manda la app base, que ya ajusta paneles y encuadre por su cuenta. */
  if(typeof historicalMapEnabled !== 'undefined' && historicalMapEnabled){ reconstruirMapa(currentMapYear); }
}

/* Red de seguridad de la vuelta atras (clic derecho): el nivel del mapa tiene que coincidir con el
   selector de estado. Si un clic derecho termina a escala nacional pero la capa de municipios sigue
   a la vista, se ven las divisiones por municipio sobre los estados; aqui se reconstruye el nivel. */
function syncMapLevel(){
  if(typeof map === 'undefined' || !map) return;
  if(typeof historicalMapEnabled === 'undefined' || !historicalMapEnabled) return;  /* en modo simulacion manda la app base */
  const esperado = $('state') ? ($('state').value || '') : '';
  const paneMunicipal = map.getPane && map.getPane('municipal-geography');
  const municipiosALaVista = !!(paneMunicipal && paneMunicipal.style.visibility === 'visible');
  if(esperado === (activeMapState || '') && (esperado || !municipiosALaVista)) return;
  activeMapState = esperado || null;
  sincronizarSelectores(activeMapState);
  if(!esperado){
    if($('search')){$('search').value = '';}
    const mapYear = $('map-year');
    if(mapYear){mapYear.disabled = false;}
  }
  reconstruirMapa(currentMapYear);
}

function renderStatePlan(){if($('state-plan-panel'))$('state-plan-panel').hidden=true;}


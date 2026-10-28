function initMapDecorations(){
  const mapElement = document.getElementById('map');
  if (!mapElement || typeof map === 'undefined') return;

  // Keep the ocean texture outside the country silhouette. The electoral
  // polygons intentionally use partial opacity, so give them an opaque land base.
  if (window.UMBRAL_STATES && map.createPane) {
    const municipalPane = map.getPane('municipal-geography');
    const statePane = map.getPane('state-geography');
    if (municipalPane) municipalPane.style.zIndex = '410';
    if (statePane) statePane.style.zIndex = '420';

    map.createPane('demo4-land-mask');
    const landPane = map.getPane('demo4-land-mask');
    landPane.style.zIndex = '399';
    landPane.style.pointerEvents = 'none';
    L.geoJSON(window.UMBRAL_STATES, {
      pane: 'demo4-land-mask',
      renderer: L.Browser.svg
        ? L.svg({ pane: 'demo4-land-mask' })
        : L.canvas({ pane: 'demo4-land-mask' }),
      interactive: false,
      noClip: true,
      style: {
        color: '#bac7bd',
        weight: 0.7,
        opacity: 0.8,
        fillColor: '#f4f1e9',
        fillOpacity: 1
      }
    }).addTo(map);
  }

  const coordinates = document.createElement('div');
  coordinates.className = 'map-coordinates';
  coordinates.setAttribute('aria-hidden', 'true');
  coordinates.textContent = 'N ↑   MUEVE EL CURSOR';
  mapElement.append(coordinates);

  const navigationHelp=document.createElement('aside');
  navigationHelp.id='map-navigation-help';
  navigationHelp.className='map-navigation-help';
  navigationHelp.setAttribute('aria-label','Cómo navegar por el mapa');
  navigationHelp.innerHTML='<strong>Cómo navegar</strong><dl><div><dt>Clic izquierdo</dt><dd>Entrar a un estado</dd></div><div><dt>Clic derecho</dt><dd>Volver un nivel</dd></div></dl><p>Después, elige un municipio.</p><span class="map-touch-help">Toca un estado para explorar sus municipios.</span>';
  mapElement.append(navigationHelp);

  const formatCoordinate = (value, positive, negative) => {
    const direction = value < 0 ? negative : positive;
    return `${Math.abs(value).toFixed(4)}° ${direction}`;
  };

  map.on('mousemove', ({ latlng }) => {
    coordinates.textContent = `${formatCoordinate(latlng.lat, 'N', 'S')} · ${formatCoordinate(latlng.lng, 'E', 'O')}`;
  });
  map.on('mouseout', () => {
    coordinates.textContent = 'N ↑   MUEVE EL CURSOR';
  });

}

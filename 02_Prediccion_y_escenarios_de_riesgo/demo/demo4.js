(() => {
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

  // Keep Leaflet's native zoom transition so the SVG geography stays visible
  // as a single transformed layer while the map moves to a selection.
  const fitBoundsImmediately = map.fitBounds.bind(map);
  map.options.zoomAnimationThreshold = Math.max(map.options.zoomAnimationThreshold || 4, 7);
  map.fitBounds = (bounds, options = {}) => {
    if (options.animate === false || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      return fitBoundsImmediately(bounds, { ...options, animate: false });
    }
    return fitBoundsImmediately(bounds, { ...options, animate: true });
  };
})();

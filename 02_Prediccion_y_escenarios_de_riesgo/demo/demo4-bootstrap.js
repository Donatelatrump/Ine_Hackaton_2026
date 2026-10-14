// demo4 usa SVG para las geometrías Leaflet. Canvas vuelve a dibujar los
// polígonos en cada fotograma del zoom y puede dejar el mapa vacío mientras
// termina de pintar los 2,477 municipios.
(() => {
  if (!window.L || !L.Browser.svg || typeof L.svg !== 'function') return;

  L.canvas = (options) => L.svg(options);
})();

/* Renderer local: no modifica L.canvas ni otras APIs de Leaflet. */
function createMapRenderer(options){
  return L.Browser.svg&&typeof L.svg==='function'?L.svg(options):L.canvas(options);
}

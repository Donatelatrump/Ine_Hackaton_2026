/* Arranque síncrono después de cargar datos y definiciones; sin sondeos por intervalos. */
try{
  load();
  initMapDecorations();
  initMapLayers();
  if(!runtime.startController())throw Error('No se pudo iniciar el controlador de demo6');
  document.dispatchEvent(new CustomEvent('umbral:ready'));
}catch(error){
  $('status').textContent='No se pudo iniciar la aplicación. Revisa los recursos locales.';
  console.error(error);
}

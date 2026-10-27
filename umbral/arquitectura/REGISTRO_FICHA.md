# Registro técnico de la ficha descriptiva

La ficha descriptiva activa es `demo/src/demo6/views/state-context.js`. Se incluye una sola vez mediante `demo/build.config.json`, dentro del paquete y de la misma clausura privada que `runtime` y `UmbralAnalytics`.

La reparación elimina la exposición manual de `window._umbralRuntime` al reconstruir el paquete desde el generador. No se carga una segunda copia del componente mediante una etiqueta HTML independiente. Se actualizó la versión del recurso en `demo6.html` para renovar la caché.

Los archivos `views/state-profile.js` y `domain/state-plans.js` se conservan en disco, pero no se cargan en esta configuración de la ficha descriptiva. La reparación no integra propuestas ni cálculos de impacto.

El constructor actualiza `assets/demo6.js`, `assets/demo6.css` y `assets/build.json`. Tras reconstruir se abrió la página en Edge y se seleccionó el municipio 08001 de Chihuahua: la ficha mostró CHIHUAHUA y no aparecieron errores JavaScript durante esa comprobación.

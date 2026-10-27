# Código de demo6

Las fuentes se compilan con `tools/construir_web.py` en un paquete con clausura privada. El navegador carga `assets/demo6.js`; no se cargan las fuentes individualmente.

| Carpeta | Responsabilidad |
| --- | --- |
| `app/runtime.js` | Vistas y conexiones explícitas entre componentes |
| `app/context.js` | Variables y utilidades privadas del motor |
| `app/bootstrap.js` | Cargar datos, crear mapa y registrar controles |
| `app/exploration.js` | Actualizar la exploración descriptiva |
| `app/render.js` | Coordinación del render existente, con hooks antes y después |
| `app/start.js` | Secuencia única de arranque y señal `umbral:ready` |
| `domain/analytics.js` | Agregaciones, observaciones, series y CSV; también CommonJS para pruebas |
| `map/context.js` | Estado privado de capas |
| `map/renderer.js` | Elegir SVG o Canvas sin alterar Leaflet |
| `map/years.js` | Años disponibles y selector |
| `map/styles.js` | Acceso a los estilos registrados por el controlador |
| `map/layers.js` | Construir, actualizar y retirar capas |
| `map/navigation.js` | Regreso por niveles y selección de estado |
| `map/start.js` | Preparar transiciones y eventos del mapa |
| `map/geography.js` | Foco municipal y navegación base |
| `map/decorations.js` | Base terrestre y coordenadas |
| `ui/` | Búsqueda, controles de criterio y movimiento de la página |
| `views/` | Resumen, histórico, evidencia, ficha estatal y detalle municipal |
| `legacy/` | Funciones existentes de escenarios, controles, exportación y evidencia |
| `controller.js` | Selección común y conexión de componentes |

## Contratos

`runtime` es privado. Contiene las vistas y los hooks `beforeUpdate`, `afterUpdate`, `afterExplore`, `afterFocus` y `afterScope`. Las funciones tienen una definición estable: el controlador registra callbacks en lugar de sobrescribir `update`, `focusMunicipality` o `applySimulationScope`.

`app/start.js` ejecuta, en orden, `load`, `initMapDecorations`, `initMapLayers` y el controlador. Solo después emite `umbral:ready`. No hay intervalos de sondeo de arranque.

La interfaz pública intencional es `window.Umbral6`: selección, actualización, ejemplos existentes, regreso nacional e `inspect()`. `inspect()` devuelve valores copiados y congelados para diagnóstico; no expone registros, mapas Leaflet ni cachés mutables. Los datos publicados y las bibliotecas siguen teniendo sus propios nombres públicos.

Las vistas descriptivas reciben datos y funciones por argumento. El resto del motor comparte variables léxicas privadas dentro del paquete; encapsularlas no equivale a haber eliminado toda dependencia entre componentes. `legacy/` conserva comportamiento sin rediseñar sus cálculos.

## Construir después de editar

Desde la raíz:

```powershell
python umbral/tools/construir_web.py
```

El orden está en `demo/build.config.json`. `assets/build.json` registra hashes del generador, configuración, fuentes y resultados. Incluir los recursos generados al compartir cambios. No editar `assets/demo6.js` o `.css` a mano.

Las fuentes CSS propias están en `styles/demo6/`: base, disposición, identidad, mapa, componentes y ficha. El orden de cascada se conserva en la configuración. Las demos anteriores mantienen sus propios archivos; demo6 ya no carga sus JS o CSS.

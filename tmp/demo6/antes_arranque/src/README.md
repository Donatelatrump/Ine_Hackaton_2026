# Código de demo6

| Directorio | Responsabilidad | Dependencias |
| --- | --- | --- |
| `domain/analytics.js` | Observaciones, agregación ponderada, series y exportación de consultas | JavaScript puro; también exporta CommonJS |
| `views/summary.js` | Resumen y comparación con el estado | Contexto recibido por argumento |
| `views/history.js` | Gráfica y tabla de antecedentes | Contexto recibido por argumento |
| `views/evidence.js` | Resultados del experimento y explicación de métodos | Contexto recibido por argumento |
| `views/state-profile.js` | Ficha descriptiva de la entidad | Catálogo generado, registros y dominio |
| `ui/search.js` | Controles de búsqueda | DOM y estado heredado |
| `map/geography.js` | Selección, foco y navegación geográfica | Leaflet y estado heredado |
| `map/layers.js` | Capas por año y nivel geográfico | Leaflet, registros y estado heredado |
| `controller.js` | Selección común, coordinación y eventos | Vistas, dominio y adaptadores heredados |
| `legacy/application.js` | Arranque y aplicación anterior compatible | Globales del motor existente |

## Contratos

- `window.UmbralDemo6Views` contiene los tres renderizadores descriptivos. Reciben explícitamente sus datos, selectores y funciones de formato; no leen el estado privado del controlador.
- `window.Umbral6` conserva la interfaz del controlador para la navegación existente.
- `window.UmbralAnalytics` es el dominio sin DOM; se carga antes de la aplicación.
- `window.UMBRAL_DATA`, `UMBRAL_MODEL_COMPARISON` y `UMBRAL_FICHAS_ESTATALES` son datos generados. No se editan manualmente.
- `demo6.html` declara el orden de scripts con `defer`. Se conserva este mecanismo para admitir apertura local y no introducir un empaquetador.
- Las rutas de documentos se resuelven respecto a `demo6.html`, aunque el archivo JS esté en una subcarpeta.

## Cambios futuros

Una nueva vista descriptiva va en `views/` y recibe sus dependencias. Las fórmulas de agregación van en `domain/`; no se copian a cada vista. Los cambios de selección se coordinan en `controller.js`. Los estilos propios están en `styles/demo6/` y las fuentes generadas en `data/`.

`legacy/` señala deuda técnica real: todavía hay variables globales, funciones redefinidas para compatibilidad y arranque por temporizadores. Esta reorganización no representa una migración completa a módulos ES ni un rediseño de los escenarios existentes.

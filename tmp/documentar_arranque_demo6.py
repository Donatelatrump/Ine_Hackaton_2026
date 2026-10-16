from pathlib import Path
R=Path(__file__).resolve().parents[1];T=R/'02_Prediccion_y_escenarios_de_riesgo';D=T/'demo'
(D/'src/demo6/README.md').write_text('''# Código de demo6

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
python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_web.py
```

El orden está en `demo/build.config.json`. `assets/build.json` registra hashes del generador, configuración, fuentes y resultados. Incluir los recursos generados al compartir cambios. No editar `assets/demo6.js` o `.css` a mano.

Las fuentes CSS propias están en `styles/demo6/`: base, disposición, identidad, mapa, componentes y ficha. El orden de cascada se conserva en la configuración. Las demos anteriores mantienen sus propios archivos; demo6 ya no carga sus JS o CSS.
''',encoding='utf-8')

(T/'arquitectura/README.md').write_text('''# Arquitectura y mantenimiento de Umbral

## Organización vigente

```text
02_Prediccion_y_escenarios_de_riesgo/
├── arquitectura/              # Guías e inventarios
├── tools/                     # Compilación, servidor e inventario
├── auditoria/                 # Calidad y preparación
├── cartografia/               # Fuentes y transformaciones geográficas
├── datos_preparados/          # Entradas del modelado
├── modelado/                  # Experimentos, publicación y tests
│   └── salidas/               # Resultados y procedencia
├── demo/
│   ├── demo6.html             # Entrada actual
│   ├── build.config.json      # Fuentes y orden de compilación
│   ├── src/demo6/
│   │   ├── app/               # Contexto privado, render y arranque
│   │   ├── domain/            # Cálculos descriptivos sin DOM
│   │   ├── map/               # Estado, años, capas y navegación
│   │   ├── ui/                # Controles y movimiento de página
│   │   ├── views/             # Presentación
│   │   ├── legacy/            # Comportamiento existente de escenarios
│   │   └── controller.js      # Selección y conexiones
│   ├── styles/demo6/          # Seis fuentes CSS propias
│   ├── assets/                # JS/CSS compilados y hashes
│   ├── data/                  # Datos generados
│   ├── vendor/                # Leaflet local
│   ├── archivo/depuracion/    # Instantáneas anteriores
│   └── verificacion/          # Evidencias conservadas
└── entrega/                   # Generadores y documentos
```

Las tres carpetas de insumos compartidos y Voto Vigía conservan sus ubicaciones en la raíz. Las entradas HTML anteriores, los generadores Python y los archivos congelados del experimento no se movieron.

## Flujo y arranque

Los insumos alimentan auditoría, preparación, experimentos y publicación en `demo/data/`. El generador de fichas usa un catálogo descriptivo independiente. El paquete web consume esos recursos locales; no entrena modelos al navegar.

`demo6.html` carga Leaflet, el motor compartido y los datos antes del paquete de la aplicación. El constructor reúne las fuentes en una clausura privada: registros, mapa, foco y cachés ya no son variables globales del navegador. `Umbral6` es la interfaz pública explícita.

El arranque es síncrono y ordenado: datos y controles, decoraciones, capas y controlador. Al terminar emite `umbral:ready`. Se eliminaron los dos sondeos con `setInterval`. Los hooks de `runtime` sustituyen las redefiniciones de funciones globales. El adaptador de transición del mapa permanece local a la instancia Leaflet.

La aplicación grande anterior se dividió por responsabilidades. También se separaron el estado del mapa, el selector de años, los estilos, la navegación y el arranque de capas. Se retiraron tres helpers sin referencias. Los escenarios conservan sus fórmulas y comportamiento existentes.

## Construcción y uso

Desde la raíz del repositorio:

```powershell
# Construir y servir la versión actual
python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py --build

# Solo construir, sin iniciar servidor
python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_web.py

# Inventario estático; no ejecuta navegador o modelos
python 02_Prediccion_y_escenarios_de_riesgo/tools/inventario.py
```

El servidor usa localhost:8000 y muestra la URL de demo6. Sirve desde la raíz para resolver los documentos de las fichas. La aplicación compilada también admite apertura por `file://`. La construcción utiliza solo Python estándar, sin npm ni descargas.

`build.config.json` declara las fuentes JS y CSS en orden. `assets/build.json` registra SHA-256 de fuentes y resultados. No editar los paquetes generados a mano. Los estilos propios de demo6 ya no dependen de cargar las hojas de demos anteriores; se conserva su cascada visual en seis fuentes con responsabilidades identificadas.

## Contratos de datos

`datos_embebidos.js` conserva el contrato histórico. Después, `comparacion_modelos.js` publica el experimento vigente y actualiza sus metadatos. Las fichas tienen otro catálogo. Los campos ausentes no se convierten en cero. El orden de publicación forma parte del contrato y no se modificó durante esta refactorización.

Los modelos se reproducen según `modelado/METODOLOGIA.md`, usando `.venv_modelos` y su lockfile. No se reentrenaron ni se editaron sus salidas durante este cambio.

## Pruebas realizadas

- 29 pruebas de Node: 25 existentes y cuatro de compilación, procedencia y carga.
- Navegador Edge: selección, históricos sin cambiar encuadre, regreso por niveles, agregación ponderada, métodos, CSV, escenario existente y ancho móvil.
- Inspección del encapsulamiento: los registros y el mapa interno no están expuestos como globales; el identificador HTML `map` sigue siendo un elemento DOM, según el comportamiento del navegador.
- Ficha del estado conservada al seleccionar municipio; simulación inicialmente cerrada.
- Capturas de escritorio y móvil revisadas. Evidencia en `tmp/demo6/modular/`.

Los scripts de pruebas conservan sus rutas; ahora usan la interfaz de diagnóstico en lugar de acceder a las variables internas. El inventario estático no sustituye estas pruebas.

## Límites que siguen siendo relevantes

El motor conserva dependencias léxicas internas y algunos métodos extensos. La cascada CSS contiene reglas heredadas que se preservan por compatibilidad visual; no se afirma que todos los selectores estén depurados. Una migración a componentes totalmente independientes sería otro cambio. No se alteraron metodología, criterios de selección o predicciones.

El primer registro `migracion_demo6.json` corresponde a los movimientos iniciales; el manifiesto de compilación y su procedencia representan la estructura actual. Las copias anteriores de documentación están en `docs/archivo/` de la raíz.
''',encoding='utf-8')

p=T/'tools/README.md';s=p.read_text(encoding='utf-8')
s=s.replace('| `python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py` |', '| `python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py --build` |')
s=s.replace('| --- | --- |','| --- | --- |\n| `python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_web.py` | Compilar las fuentes de demo6 en paquetes JS/CSS y registrar sus hashes |',1)
s=s.replace('Ambas herramientas utilizan','Estas herramientas utilizan')
p.write_text(s,encoding='utf-8')
p=R/'README.md';s=p.read_text(encoding='utf-8').replace('tools/servir_demo.py\n','tools/servir_demo.py --build\n')
s=s.replace('No editar manualmente los JSON/JS generados.','No editar manualmente los JSON/JS generados. Después de modificar fuentes web, reconstruir con `tools/construir_web.py` del track o iniciar el servidor con `--build`.')
p.write_text(s,encoding='utf-8')
p=D/'DEMO6.md';s=p.read_text(encoding='utf-8');start=s.index('## Archivos de demo6');end=s.index('La cartografía incluye',start)
s=s[:start]+'''## Archivos de demo6

- `demo6.html`: entrada; carga datos y los paquetes generados.
- `src/demo6/`: código organizado en app, dominio, mapa, interfaz, vistas y compatibilidad.
- `styles/demo6/`: estilos propios por responsabilidad.
- `build.config.json`: orden de construcción.
- `assets/demo6.js`, `assets/demo6.css`, `assets/build.json`: recursos generados y procedencia.
- `decision.js`, `data/*`: motor existente y datos locales compartidos.
- `verificar_demo6.py`, `build.test.cjs`: comprobaciones de comportamiento y construcción.

Guía de componentes, arranque y reconstrucción: [src/demo6/README.md](src/demo6/README.md). El estado interno está encapsulado; `Umbral6.inspect()` sustituye el acceso de las pruebas a variables globales.

'''+s[end:];p.write_text(s,encoding='utf-8')
p=R/'ANALISIS_GENERAL_DEL_PROYECTO.md';s=p.read_text(encoding='utf-8')
s=s.replace('| Globales y redefiniciones de funciones | Se identifica la aplicación heredada en `legacy/`; migración completa pendiente |','| Globales y redefiniciones de funciones | Estado encapsulado en el paquete y hooks explícitos; dependencias internas conservadas |')
s=s.replace('| Arranque por temporizadores | Pendiente reemplazar por una señal única de aplicación lista |','| Arranque por temporizadores | Dos sondeos eliminados; secuencia explícita y señal `umbral:ready` |')
s=s.replace('| Múltiples hojas CSS heredadas | Pendiente consolidación con revisión visual específica |','| Múltiples hojas CSS heredadas | Fuentes propias por responsabilidad y un paquete CSS; revisión de escritorio y móvil |')
s=s.replace('las capas de demo6 524 y la aplicación heredada unos 59 KB','el motor anterior de capas tenía 524 y la aplicación heredada unos 59 KB antes de dividirse')
s=s.replace('El motor anterior conserva compatibilidad dentro de `legacy/`.','Las funciones existentes de escenarios conservan compatibilidad dentro de `legacy/`. La aplicación anterior fue dividida y ya no existe como un único archivo.')
s=s.replace('No se ejecutaron pruebas automatizadas, pruebas de navegador ni entrenamientos durante esta reorganización. Las pruebas anteriores documentadas corresponden al experimento en su ejecución original.','La segunda etapa de reorganización pasó 29 pruebas de Node y las comprobaciones de navegador de demo6: navegación, históricos, métodos, agregaciones, exportaciones, ficha estatal, escenario existente y móvil, sin errores JavaScript. Se revisaron capturas. No se reentrenaron modelos.')
s=s.replace('1. Sustituir gradualmente los envoltorios de funciones globales por interfaces de selección y mapa.','1. Continuar reduciendo dependencias léxicas internas con interfaces de componentes más pequeñas.')
s=s.replace('2. Reemplazar los temporizadores por una señal de aplicación lista.','2. Mantener la secuencia de arranque y el contrato `umbral:ready`, ya implementados.')
s=s.replace('4. Consolidar CSS compartido con revisión visual.','4. Depurar selectores redundantes conservando la apariencia; el paquete y las fuentes propias ya están separados.')
p.write_text(s,encoding='utf-8')

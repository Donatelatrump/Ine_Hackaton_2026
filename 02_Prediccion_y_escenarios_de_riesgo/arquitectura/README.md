# Versión vigente: Demo7 · revisión del 21 de octubre de 2026

[Guía vigente de Demo7](../demo/DEMO7.md) · [Requisitos, evidencias y pendientes](../entrega/REVISION_REQUISITOS_INE.md). Reporte y presentación sincronizados con demo7; el contenido fechado anteriormente describe la etapa previa.

---

# Arquitectura y mantenimiento de Umbral

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

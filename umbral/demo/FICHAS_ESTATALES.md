# Fichas informativas estatales · demo6

La sección 03 presenta primero una ficha descriptiva de la entidad elegida. Al consultar un municipio conserva el estado de pertenencia y explicita que los indicadores son estatales. La simulación existente queda en un desplegable posterior y no se configura automáticamente a partir de la ficha. Esta sección conserva la disponibilidad para 2027 que ya tenía demo6.

## Contenido y fuentes

- Antecedentes electorales de 2015, 2018, 2021 y 2024: todos los registros de la entidad en la base de la demo, sin restringirlos a municipios con estimación para 2027 ni al filtro de catálogo constante. Abstención ponderada por SV+NV reconstruido desde LN y NS; se muestran municipios con dato. No se armonizan cambios de límites históricos.
- Población total 2024 y proyección 2027: `fuentes/Bases_de_datos_explicativos/pobproy_ggrupos.csv`. Se suman los registros municipales de hombres y mujeres por entidad y año. No se incluyen claves terminadas en 000; claves, año y sexo repetidos no se suman dos veces. No representa lista nominal ni electorado.
- Se recorren los seis CSV de `fuentes/Bases_de_datos_explicativos` para registrar columnas, años, filas y huellas SHA-256. Los archivos solapados de población no se suman entre sí. Defunciones e índices demográficos no se convierten en explicaciones del abstencionismo.
- Se extrajo texto de los cinco PDF y los dos HTML de `fuentes/Otras_fuentes_de_informacion` y `fuentes/Datos_propuestas_estatales`. El catálogo visible identifica el alcance de cada documento y ofrece un enlace local al original.

Los documentos incluyen un acuerdo nacional de implementación de ENCÍVICA, estudios muestrales y censales, la ENCUCI, un estudio histórico del IFE, una nota de divulgación y una tesis centrada en Gustavo A. Madero. La carpeta denominada `fuentes/Datos_propuestas_estatales` no equivale a disponer de 32 planes estatales validados.

## Límites

La ficha es contexto descriptivo. No personaliza mensajes, canales, presupuestos ni intervenciones electorales; no afirma causas individuales ni efectos causales. No traslada resultados nacionales o regionales de encuestas a municipios. La sede de presentación de una investigación tampoco define su representatividad geográfica. Los documentos históricos no certifican vigencia actual de programas.

## Reproducción

Desde la raíz:

```powershell
python umbral/modelado/generar_fichas_estatales.py
```

Genera `demo/data/fichas_estatales.json` y su versión incrustada `.js`. El JSON conserva el inventario y las huellas de los archivos originales. El componente `src/demo6/views/state-profile.js` calcula los antecedentes estatales con `UmbralAnalytics.summary`, sin alterar modelos, predicciones ni la selección del mapa. Voto Vigía no se modifica.

La generación procesó 7 documentos, 6 CSV y contexto demográfico para 32 entidades. Su implementación inicial no incluyó pruebas adicionales. En la refactorización posterior se comprobó en navegador que la ficha mantiene el estado al seleccionar un municipio y que la simulación comienza cerrada. El componente se incluye ahora en el paquete construido por `tools/construir_web.py` del track.

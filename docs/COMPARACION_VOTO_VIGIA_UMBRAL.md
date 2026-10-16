# Comparación de Voto Vigía y Umbral

Fecha: 16 de octubre de 2026.

Actualización posterior: ya se ejecutó la [comparación de cuatro regresores](../02_Prediccion_y_escenarios_de_riesgo/modelado/COMPARACION_4_MODELOS.md). Incluye CatBoostRegressor entrenado sobre los datos de Umbral, sin usar ni modificar el modelo de Voto Vigía. HistGradientBoosting quedó seleccionado y está disponible en demo6 junto a los demás métodos. Las recomendaciones de investigación que siguen describen la etapa previa a esa ejecución.

Actualización: las mejoras de consulta, evidencia y exportación de este análisis se implementaron en [demo6](../02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html). La [guía](../02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md) y la documentación activa describen la versión resultante. Las observaciones siguientes sobre el estado de Umbral corresponden a demo5 antes de esa implementación. La regla de selección del modelo se documentó sin reentrenar; CatBoost y la ampliación seccional permanecen como líneas de investigación.

Alcance: revisión del código, las plantillas y los artefactos locales de ambos proyectos. La versión de Umbral considerada es demo5. No se levantó el servidor de Voto Vigía, no se reentrenaron modelos y no se midió rendimiento visual. Las cifras se contrastaron con los archivos guardados; esto no reproduce ni valida sus experimentos.

## Conclusión

Voto Vigía aporta buenas ideas para resumir resultados y hacer visible la evaluación del modelo. Conviene adaptarlas a Umbral. Su código predictivo y su simulador necesitan correcciones antes de reutilizarse: las cifras mostradas, las coordenadas y algunas estimaciones de impacto no corresponden directamente a resultados calculados.

Umbral ya cuenta con cartografía municipal, consulta histórica, comparación con la elección homóloga y escenarios limitados por cobertura, con fuentes de las acciones. La mayor oportunidad inmediata es hacer más comprensible esa evidencia y mantener coherentes la interfaz, la documentación y los artefactos.

## Comparación de funciones

| Aspecto | Voto Vigía | Umbral actual | Oportunidad |
|---|---|---|---|
| Unidad de análisis | Secciones electorales | Municipios | Explorar secciones después de resolver cartografía y correspondencia histórica. |
| Objetivo del modelo | Clasificar participación relativa al estado en tres niveles | Estimar porcentaje de abstención; semáforo por tercios | Ofrecer contexto estatal como indicador adicional, explicando su diferencia con el nacional. |
| Consulta territorial | Estados reales y puntos seccionales generados artificialmente | Polígonos municipales y complemento insular oficial | Conservar la geometría real de Umbral. |
| Resultados | Tarjetas de indicadores y página de métricas | Ficha, ranking, tablas y opciones de calidad | Destacar resúmenes y comparaciones visuales. |
| Simulación | Presets, controles y gráfica antes/después | Acciones citadas, alcance, distribución, escenarios y exportación | Añadir presets y gráficas usando los cálculos de Umbral. |
| Explicación del modelo | Importancia global exportada a CSV | Coeficientes estandarizados en metadatos; perfil descriptivo | Exponer factores del modelo con sus límites. |
| Descargas | Resumen nacional y muestra de secciones críticas | Plan simulado y supuestos | Añadir descarga de la consulta histórica y de proyecciones sin exigir una simulación. |
| Operación | FastAPI, Docker y datos Parquet | Demo estática con datos locales | Mantener apertura local; considerar API si se amplía a secciones. |

## Qué tomar y cómo adaptarlo

### 1. Resumen territorial junto al mapa — prioridad alta

Tomar la idea de las tarjetas de resumen de `app/templates/index.html`.

En Umbral mostrar: territorio, año, abstención, participación, municipios con dato y cobertura de población observada. Para 2027 identificar claramente el método de estimación. Separar siempre los resultados observados de las proyecciones.

Calcular promedios territoriales con sus denominadores disponibles, sin promediar porcentajes de municipios por igual. El estilo estatal actual de demo5 usa media municipal simple; debe distinguirse de las agregaciones ponderadas de otras partes de la aplicación.

### 2. Comparación histórica con gráfica — prioridad alta

Adaptar las gráficas comparativas de `app/templates/simulador.html` a una serie temporal municipal: valores observados 2009–2024 y punto 2027 con apariencia distinta. Dejar huecos donde falten datos y explicar los cambios de tipo de elección y de límites territoriales.

Umbral ya tiene barras históricas en la ficha; la mejora sería darles mayor visibilidad y permitir compararlas con un promedio estatal ponderado. No es necesario añadir una librería remota para un gráfico pequeño.

### 3. Evaluación del modelo visible y consistente — prioridad alta

Tomar la separación de una página de métricas, alimentándola desde los mismos metadatos que usa la demo. Mostrar error en puntos porcentuales, comparación con referencia, tamaño de la cohorte, aciertos entre los 50 municipios prioritarios y exclusiones.

Los valores actualmente cargados por `demo/data/datos_embebidos.js` y `resultados.json` son:

| Corte | Referencia: MAE | Ridge: MAE | Referencia: aciertos top 50 | Ridge: aciertos top 50 |
|---|---:|---:|---:|---:|
| 2021 | 12.12 pp | 8.90 pp | 16/50 | 21/50 |
| 2024 | 5.64 pp | 8.96 pp | 27/50 | 21/50 |

Ridge mejora en 2021 y empeora en 2024. Estos valores difieren de los documentados en `modelado/RESULTADOS.md` (9.21 y 8.58 pp para Ridge). Los metadatos actuales indican `alpha_final=500`, mientras `METODOLOGIA.md` describe alpha fijo 10.

Además, `metadata.selected_model` es `persistencia`, pero demo5 abre el selector en Ridge. Hay que revisar la regla y el origen del artefacto y comunicar cuál es el método recomendado; no conviene cambiar el valor por defecto basándose solo en una bandera sin aclarar esa discrepancia. La definición del rango también identifica persistencia en los metadatos, mientras la ficha tiene texto fijo sobre Ridge y ±21.05 pp. Todas esas etiquetas deben derivarse de los artefactos vigentes.

### 4. Escenarios preconfigurados y comparación — prioridad media

Tomar de Voto Vigía los botones que preparan una configuración, el restablecimiento y las barras antes/después.

Aplicarlos a los controles de Umbral: tipo de acción, cobertura total, distribución y territorio. Un preset debe describir los supuestos que introduce. Usar las funciones existentes de `demo/decision.js`; no trasladar la conversión de probabilidades de Voto Vigía a votos.

### 5. Comparación con el contexto estatal — prioridad media

La idea de comparar cada territorio con su entidad es útil. Mostrar una brecha como «+6.3 puntos de abstención respecto al estado» aporta contexto sin sustituir la tasa absoluta ni el semáforo nacional.

La fórmula de Voto Vigía compara participación contemporánea de cada sección con la media y desviación del estado; no mide por sí misma una caída frente a la historia de esa sección. Si se adapta, el nombre debe describir esa comparación correctamente.

### 6. Explicación del modelo — prioridad media

Umbral ya exporta `coefficients_standardized`. Se puede presentar un gráfico de coeficientes del modelo y mantener aparte el perfil observado por edad, sexo y tipo de sección. Un coeficiente global no es una explicación individual completa ni demuestra causalidad.

Para explicar una predicción municipal concreta se necesitan también la transformación de variables, el modelo y sus componentes de referencia/ajuste. No basta con convertir coeficientes en porcentajes de importancia.

### 7. Secciones y CatBoost — investigación posterior

Estudiar el pipeline seccional y CatBoost como candidatos experimentales, sin sustituir Ridge todavía. Para comparar modelos deben compartir objetivo, cohorte, información disponible antes de la elección y cortes temporales. F1 seccional de clasificación y MAE municipal de regresión no son métricas intercambiables.

Una ampliación a secciones requiere geometría real, control de altas/bajas/divisiones y validación territorial. Parquet y una API pueden ayudar cuando el volumen lo justifique; añadir un servidor no mejora por sí mismo la predicción.

## Problemas de Voto Vigía que no conviene trasladar

1. **Métricas de interfaz diferentes a las guardadas.** `app/templates/metricas.html:29` muestra 85.4% de exactitud, pero `models/metrics_report.json` registra 65.93% y F1 macro 0.4442. La importancia juvenil mostrada (24.8%) tampoco coincide con `docs/feature_importance.csv` (~3.90%). `app/main.py:261` devuelve cifras fijas si falta el reporte.

2. **La evaluación 2024 participa en el ajuste.** `src/models/train.py:94` usa el conjunto 2024 como `eval_set` para parada temprana. Por ello no corresponde describirlo como prueba completamente ciega. También hay que acreditar la disponibilidad previa de las variables: `build_features.py` parte de las filas del año objetivo y conserva su composición demográfica y lista nominal.

3. **Referencia débil y detección crítica limitada.** Compara contra `DummyClassifier(strategy='stratified')`, no contra la elección homóloga. El reporte guardado da precisión de clase crítica de 14.59% y recuperación de 23.53%. La clase mayoritaria representa 79.65% de la prueba; predecir siempre esa clase superaría su 65.93% de exactitud global, aunque no serviría para detectar alertas. Conviene evaluar las clases y la priorización, no promocionar solo exactitud.

4. **Puntos sin ubicación geográfica real.** `app/main.py:114–137` genera posiciones alrededor de centroides estatales mediante `hash()`. No son coordenadas de las secciones. El CSV exporta esas posiciones y una muestra de puntos, no necesariamente el universo completo de alertas.

5. **Simulación sin identificación causal.** `what_if_engine.py:51` altera una variable histórica y vuelve a clasificar. Eso es sensibilidad del predictor. La conversión a votos multiplica cambios de probabilidad de clase crítica por lista nominal y por 0.15 (`:70–72`), sin que ese factor tenga una justificación visible en el código revisado. La probabilidad de pertenecer a una clase no es una tasa de abstención.

6. **Indicadores y controles desconectados.** La participación base es 58.4 o 51.8 según una condición, y la simulada usa una fórmula fija (`app/main.py:475–476`). `estrategia_focalizada` se declara en el request, pero no interviene en el cálculo revisado. Los tests comprueban principalmente respuesta y estructura, no esa diferencia de comportamiento.

7. **Reproducción incompleta en la copia recibida.** `src/data/ingest.py` solo procesa 2009. `validator.py`, `models/predict.py` y `docs/reporte_metodologico.md` están vacíos. Hay artefactos procesados para otros años, pero estos archivos no bastan para reconstruir todo el pipeline desde cero. Los requisitos tienen cotas inferiores de versiones, sin un lock de entorno.

## Orden de trabajo recomendado para Umbral

1. Alinear documentación, método recomendado, rangos y cifras de evaluación con los artefactos vigentes.
2. Unificar el estado de selección —año, entidad, municipio y método— entre mapa, ficha, ranking y simulación. Hoy está repartido entre `demo5.js`, `geografia.js`, `buscadores.js` y `aplicacion.js`.
3. Añadir resumen territorial y gráfica histórica con datos reales y denominadores consistentes.
4. Añadir exportación de resultados observados/proyecciones independiente del plan de intervención.
5. Mejorar la comparación visual de escenarios y los presets con supuestos explícitos.
6. Evaluar explicación de factores, análisis seccional y CatBoost como trabajos separados.

Este análisis no modifica la página ni importa el modelo de Voto Vigía.

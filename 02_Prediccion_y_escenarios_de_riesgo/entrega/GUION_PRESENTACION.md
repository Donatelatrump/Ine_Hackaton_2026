# Guion de demostración de Umbral demo6

Versión del 16 de octubre de 2026. Duración orientativa: tres minutos. Abrir demo/demo6.html con la carpeta completa.

## 1. Territorio y datos

Mostrar México y HistGradientBoosting, modelo seleccionado. El resumen informa 1,783 municipios estimables sobre 2,477 y cobertura de población observable, sin contar los faltantes como cero.

Seleccionar un estado y municipio. Mostrar la brecha con el promedio estatal. Cambiar a 2009 o 2024 conservando el territorio: son resultados observados, no proyecciones. Mostrar la gráfica y descargar el CSV de toda la consulta, independiente del plan.

## 2. Proyección y evaluación

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

Mostrar la tabla de los cuatro modelos y los tiempos. La referencia homóloga sigue disponible. No afirmar superioridad en todos los indicadores: en 2024 la referencia tiene más aciertos top50. Los factores Ridge no explican las predicciones de los otros modelos. El clic derecho vuelve al estado y después a México.

## 3. Acción bajo supuestos

Para reproducir el caso: Quintana Roo, SOLIDARIDAD (clave histórica 23008), año 2027, HistGradientBoosting y catálogo constante. Base 61.636222%, SV+NV 2024 de 255,362.

Seleccionar el ejemplo de 1,000 SMS Suecia. Con efecto ITT externo de 0.30 pp se obtienen 3 votos adicionales hipotéticos; posterior 61.635048% y reducción de 0.001175 pp. Las barras comparten escala y ese efecto pequeño puede no distinguirse visualmente.

La cobertura es editable y no constituye una capacidad institucional confirmada. El traslado a México requiere evaluación. Mostrar fuentes, supuestos y descarga del plan. El puesto del modelo seleccionado es 9, Ridge 4 y referencia 3; la frecuencia 4/6 es del ranking nacional top50 con catálogo constante, no del plan sobre un municipio.

## Cierre

Proponer revisión territorial y de capacidad antes de un piloto con protocolo previo. Los rangos de la ficha son errores retrospectivos por método, no intervalos prospectivos calibrados. La cartografía conserva límites históricos sin armonizar e incorpora un complemento insular oficial. La demo abre localmente con sus datos y librerías.

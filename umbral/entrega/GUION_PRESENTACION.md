# Guion de demostración de Umbral

Versión del 28 de octubre de 2026. Duración orientativa: cinco minutos. Abrir [Umbral](../demo/demo7.html) con la carpeta completa.

## 1. Territorio y datos

“Umbral predice la abstención municipal para 2027 y también permite informarse y simular acciones. Propone planes estatales apoyados en el contexto y en investigaciones mexicanas; las simulaciones usan coeficientes publicados o supuestos identificados. La predicción puede equivocarse y el efecto de una acción requiere evaluación local.”

Mostrar México y HistGradientBoosting, modelo seleccionado. El resumen informa 1,783 municipios estimables sobre 2,477 y cobertura de población observable, sin contar los faltantes como cero.

Seleccionar un estado y municipio. Mostrar la brecha con el promedio estatal. Cambiar a 2009 o 2024 conservando el territorio: son resultados observados, no proyecciones. Mostrar la gráfica y descargar el CSV de toda la consulta, independiente del plan.

## 2. Proyección y evaluación

“Comparamos cuatro modelos con los mismos datos. Elegimos HistGradientBoosting por la regla de evaluación: su error medio fue de 6.84 puntos porcentuales. LightGBM quedó prácticamente empatado, así que usamos el error ponderado por población para desempatar. Esto nos permite explorar 2027, pero todavía no sabemos qué tan cerca estará de esa elección.”

Explicar una unidad: pasar de 40% a 45% son cinco puntos porcentuales. Mostrar también el límite: en 2024, la referencia identificó 27 de los 50 municipios con más abstención y el modelo, 19. Un menor error promedio no garantiza encontrar mejor todos los municipios prioritarios.

Mostrar la tabla de los cuatro modelos y los tiempos. La referencia homóloga sigue disponible. No afirmar superioridad en todos los indicadores: en 2024 la referencia tiene más aciertos top50. Los factores Ridge no explican las predicciones de los otros modelos. El clic derecho vuelve al estado y después a México.

## 3. Acción bajo supuestos

Para reproducir el caso: Quintana Roo, SOLIDARIDAD (clave histórica 23008), año 2027, HistGradientBoosting y catálogo constante. Base 61.636222%, SV+NV 2024 de 255,362.

Seleccionar el ejemplo de 1,000 SMS Suecia. Con efecto ITT externo de 0.30 pp se obtienen 3 votos adicionales hipotéticos; posterior 61.635048% y reducción de 0.001175 pp. Las barras comparten escala y ese efecto pequeño puede no distinguirse visualmente.

La cobertura es editable y no constituye una capacidad institucional confirmada. El traslado a México requiere evaluación. Mostrar fuentes, supuestos y descarga del plan. El puesto del modelo seleccionado es 9, Ridge 4 y referencia 3; la frecuencia 4/6 es del ranking nacional top50 con catálogo constante, no del plan sobre un municipio.

## 4. Plan estatal y entrega

Volver al estado y abrir su plan. La comparación inicial supone alcanzar al 10% de la base estimable, con un efecto central de 1.5 pp entre personas alcanzadas; las variantes 0.3 y 3 pp son sensibilidad de un supuesto del proyecto. No atribuir eficacia demostrada al plan completo.

Comparar los mapas sin/con acción con los mismos umbrales nacionales por tercios; abrir diferencias para ver cambios pequeños. El cálculo del plan estatal es fijo. En el simulador de acciones, seleccionar SMS y cambiar el alcance a 0 personas: las tasas deben coincidir. Restaurar el alcance y descargar la distribución CSV: incluye antes/después, semáforo, método, fuentes y municipios sin estimación. Descargar la ficha imprimible.

En Documentos, mostrar reporte de 14 páginas, presentación de 10 diapositivas, base agregada y proyecciones vigentes. La entrega incluye las dos cartas con firmas visibles. Registro, elegibilidad y envío siguen sin acreditarse mediante estos documentos. La demo y sus documentos no equivalen a una inscripción aceptada.

## Cierre

Proponer revisión territorial y de capacidad antes de un piloto con protocolo previo. Los rangos de la ficha son errores retrospectivos por método, no intervalos prospectivos calibrados. La cartografía conserva límites históricos sin armonizar e incorpora un complemento insular oficial. La demo abre localmente con sus datos y librerías.

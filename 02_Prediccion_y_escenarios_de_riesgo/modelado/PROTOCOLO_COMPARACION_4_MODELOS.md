# Protocolo de comparación de cuatro modelos

Definido antes de ejecutar la comparación, 16 de octubre de 2026.

## Objetivo común

Estimar la abstención municipal en puntos porcentuales. Comparar Ridge, HistGradientBoostingRegressor, LGBMRegressor y CatBoostRegressor. Incluir la persistencia de la elección homóloga como referencia adicional, sin contarla entre los cuatro modelos aprendidos.

Todos aprenden el residual respecto a la misma referencia, usan las mismas 15 variables históricas de `core.make_features`, las mismas filas y reglas de calidad (NS≤10% en los antecedentes y el objetivo evaluado). No se añaden identificadores categóricos a un único competidor ni datos demográficos del año objetivo. No se utilizan proyecciones CONAPO solo para el futuro, porque no están disponibles de forma comparable en los cortes históricos. La proyección 2027 de este experimento utiliza esas mismas 15 variables.

## Cortes y ajuste

- Comprobación 2021: entrenamiento con etiquetas 2015/2018. Los parámetros se seleccionan usando únicamente validación 2018 con entrenamiento 2015.
- Comprobación 2024: entrenamiento con etiquetas 2015/2018/2021. Selección interna por validaciones 2018 y 2021, siempre con entrenamiento anterior al año validado.
- Cuatro configuraciones por familia, registradas en el código antes de la ejecución. Semilla 42 y un hilo de CPU para los cuatro competidores. Sin parada temprana sobre el corte externo ni división aleatoria entre años.
- Final 2027: entrenamiento hasta 2024; selección interna de parámetros con validaciones 2018, 2021 y 2024. La familia se elige a partir de las dos comprobaciones externas anteriores.

Se comprueba que cada fila usa antecedentes de años estrictamente menores que su objetivo. El corte 2024 ya fue examinado en versiones anteriores del proyecto: es un backtest temporal reproducible, no una prueba nueva y completamente ciega del proceso de investigación.

## Regla de selección

1. Elegir la familia con menor promedio del MAE de 2021 y 2024, dando el mismo peso a cada elección.
2. Si la diferencia frente al mínimo es ≤0.05 pp, desempatar por menor promedio del MAE ponderado por SV+NV del objetivo.
3. Si también difieren ≤0.05 pp en MAE ponderado, preferir mayor promedio de precisión top50.
4. Si la diferencia en precisión top50 es ≤0.01, preferir menor mediana de tiempo de entrenamiento medida en esta máquina.

Se publican ambos cortes por separado, sesgo con signo, error P90 y aciertos top50. El tiempo no se combina con puntos porcentuales en una puntuación arbitraria. Se compara además el ganador con la persistencia; si esta resulta mejor en la métrica principal se identifica expresamente, sin ocultarla. La regla anterior sustituye la comparación defectuosa del cambio de sesgo con signo solo para este experimento; no se reescriben los resultados históricos de versiones anteriores.

## Velocidad y reproducibilidad

Tiempo de entrenamiento con parámetros fijados: mediana de tres ajustes en CPU, sin incluir carga de CSV ni búsqueda de parámetros. Predicción: mediana de diez ejecuciones después de un calentamiento, sobre toda la cohorte evaluada. Se registran Python, paquetes, plataforma, parámetros, semilla, hashes de insumos y predicciones por fila.

Los tiempos son locales y descriptivos. Demo6 seguirá mostrando predicciones precalculadas, por lo que no se interpretan como tiempos de interacción del navegador.

## Alcance de la conclusión

La selección final utiliza estos backtests y no dispone de una elección futura independiente para validar al ganador después de seleccionarlo. Dos cortes, uno intermedio y otro presidencial, no garantizan superioridad en 2027. Los rangos basados en errores históricos no son intervalos probabilísticos prospectivos. Las claves municipales no acreditan fronteras históricas armonizadas.

## Documentación técnica primaria

- [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html).
- [LGBMRegressor](https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMRegressor.html).
- [CatBoostRegressor](https://catboost.ai/docs/en/concepts/python-reference_catboostregressor).

No se usa el modelo ni se modifica el proyecto Voto Vigía.

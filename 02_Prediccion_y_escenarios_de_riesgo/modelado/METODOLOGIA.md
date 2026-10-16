# Metodología vigente: comparación de cuatro modelos

16 de octubre de 2026. Esta etapa sí incluye una nueva ejecución real de entrenamiento y evaluación. Los resultados anteriores se conservan en sus artefactos y no se atribuyen a esta ejecución.

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

## Datos, variables y cortes

CCPC INE de 2009 a 2024. Objetivo: abstención observable municipal = 100 × NV / (SV+NV). Cohorte con NS≤10% en ambos antecedentes y, para evaluar, también en el objetivo. Las 15 variables de core.make_features son idénticas para todos los modelos y se construyen solo con años anteriores al objetivo. No se añaden identificadores categóricos a un solo competidor ni proyecciones CONAPO exclusivas de 2027.

Todos estiman el residual respecto a la última elección del mismo tipo; la salida suma referencia más residual y se acota a [0,100]. La referencia homóloga se conserva como control adicional. Para 2027 la referencia es 2021.

| Corte externo | Etiquetas de entrenamiento | Validaciones internas | Municipios evaluados |
|---|---|---|---:|
| 2021 | 2015, 2018 | 2018, entrenando solo con 2015 | 1,490 |
| 2024 | 2015, 2018, 2021 | 2018 y 2021, cada una con años anteriores | 1,476 |
| Proyección 2027 | 2015, 2018, 2021, 2024 | 2018, 2021 y 2024 | 1,783 proyecciones |

Cuatro configuraciones por familia, semilla 42, un hilo de CPU y ninguna parada temprana con el corte externo. La estandarización de Ridge se ajusta solo con entrenamiento. Parámetros completos y búsquedas internas en salidas/comparacion_modelos/resultados.json.

## Regla de selección fijada antes de ejecutar

Menor MAE medio dando igual peso a 2021 y 2024. Dentro de 0.05 pp del mínimo, menor MAE ponderado; si este difiere ≤0.05 pp, mayor precisión top50; dentro de 0.01 de precisión, menor tiempo de ajuste. No se mezcla tiempo y error en una puntuación arbitraria.

Esta regla sustituye en el nuevo experimento la comparación defectuosa del cambio de sesgo con signo. No se reescriben core.choose_model ni los resultados de las demos anteriores. El sesgo con signo se informa para cada modelo sin rechazar mejoras de sesgo absoluto por un cambio de signo.

## Resultados

| Modelo | MAE medio (pp) | MAE ponderado medio (pp) | Aciertos top50 medios | Ajuste medio (s) |
|---|---:|---:|---:|---:|
| LightGBM | 6.8304 | 4.8385 | 21.0/50 | 0.1266 |
| HistGradientBoosting | 6.8360 | 4.6684 | 20.0/50 | 0.1996 |
| CatBoost | 6.9089 | 4.6692 | 20.5/50 | 1.0452 |
| Ridge | 9.0094 | 5.2188 | 20.0/50 | 0.0128 |


La referencia obtiene MAE medio 8.8774 pp. En 2024 logra 27/50 aciertos top50 frente a 19/50 de HistGradientBoosting: menor MAE no implica mejor ranking en todos los casos. LightGBM recupera más municipios top50 en promedio que el ganador, pero el protocolo prioriza MAE y su desempate ponderado.

## Velocidad

Mediana de tres ajustes por corte, excluyendo carga y búsqueda. Mediana de diez predicciones tras calentamiento, sobre la cohorte completa. El informe registra CPU, plataforma y versiones. Ridge conserva el menor tiempo de entrenamiento; no se afirma que el ganador sea más rápido. Demo6 sigue leyendo proyecciones precalculadas, sin ejecutar modelos en cada clic.

## Proyección y sensibilidad

Demo6 carga data/comparacion_modelos.js después de los datos originales. El complemento incorpora los cuatro métodos y selecciona HistGradientBoosting. No reemplaza datos_embebidos.js ni las demos previas. Se guardan también el modelo seleccionado serializado, predicciones por municipio y corte y sus hashes.

La sensibilidad NS5/10/20 usa los parámetros finales NS10 congelados y reentrena con la cohorte correspondiente. La frecuencia compara referencia y método activo; cuando se consulta referencia, el comparador es Ridge. Los nombres internos ridge_* de decision.js son compatibilidad de implementación, no atribución del método activo a Ridge. No se usan estas sensibilidades para decidir el ganador.

## Incertidumbre y límites

El rango ilustrativo de la ficha usa el P90 del error absoluto de 2021 de cada método. Para el ganador: ±18.04 pp, acotado a [0,100]. Es error retrospectivo, no un intervalo prospectivo calibrado.

Los dos cortes participan en la selección final. 2024 ya fue examinado en etapas previas: no se presenta como una nueva prueba ciega de todo el proceso de investigación. Falta una elección futura independiente después de seleccionar. Hay pocos ciclos electorales, cohortes condicionadas por calidad y límites históricos sin armonizar. No se garantizan resultados de 2027 ni se infieren comportamientos individuales.

## Reproducción

1. Crear un entorno Python 3.12 e instalar modelado/requirements_comparacion.lock.txt.
2. Ejecutar modelado/comparar_modelos.py con ese entorno.
3. Ejecutar modelado/publicar_comparacion_demo6.py para generar el complemento local y la sensibilidad.
4. Ejecutar modelado/verificar_comparacion.py y demo/verificar_demo6.py.

[Protocolo previo](PROTOCOLO_COMPARACION_4_MODELOS.md), [resultados completos](COMPARACION_4_MODELOS.md), salidas/comparacion_modelos/resultados.json y verificacion.json. No se modifica Voto Vigía.

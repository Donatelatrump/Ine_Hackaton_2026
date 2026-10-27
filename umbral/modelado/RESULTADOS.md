# Resultados vigentes de Umbral

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

| Modelo | MAE medio (pp) | MAE ponderado medio (pp) | Aciertos top50 medios | Ajuste medio (s) |
|---|---:|---:|---:|---:|
| LightGBM | 6.8304 | 4.8385 | 21.0/50 | 0.1266 |
| HistGradientBoosting | 6.8360 | 4.6684 | 20.0/50 | 0.1996 |
| CatBoost | 6.9089 | 4.6692 | 20.5/50 | 1.0452 |
| Ridge | 9.0094 | 5.2188 | 20.0/50 | 0.0128 |

[Comparación completa y tiempos por corte](COMPARACION_4_MODELOS.md). [Protocolo](PROTOCOLO_COMPARACION_4_MODELOS.md). [Metodología](METODOLOGIA.md).

La referencia de 2021 sigue disponible. Los resultados anteriores se conservan en los artefactos originales y no se mezclan con este benchmark de 15 variables. En 2024 la referencia recupera más municipios del top50 que el modelo seleccionado.

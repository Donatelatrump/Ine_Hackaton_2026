# Resultados de la comparación de cuatro modelos

Ejecución real: 2026-10-16T20:15:53.598853+00:00. Python 3.12.0.

Se reentrenaron los cuatro regresores sobre la misma cohorte y las mismas 15 variables históricas. Las cifras no son las del experimento anterior con 18 variables declaradas en sus metadatos.

| Corte | Modelo | Municipios | MAE pp | Ponderado pp | Sesgo pp | Top50 | Entrenar s | Predecir ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2021 | Referencia homóloga | 1490 | 12.1159 | 8.0524 | 7.8660 | 16/50 | No aplica | No medido |
| 2021 | Ridge | 1490 | 9.3209 | 5.5710 | 3.5199 | 19/50 | 0.0092 | 2.0635 |
| 2021 | HistGradientBoosting | 1490 | 8.5486 | 5.9990 | 2.7010 | 21/50 | 0.1827 | 11.7457 |
| 2021 | LightGBM | 1490 | 8.5419 | 6.2303 | 2.7330 | 22/50 | 0.1103 | 15.7488 |
| 2021 | CatBoost | 1490 | 8.6986 | 5.8547 | 2.5768 | 20/50 | 0.9924 | 3.7899 |
| 2024 | Referencia homóloga | 1476 | 5.6389 | 3.5411 | -4.3061 | 27/50 | No aplica | No medido |
| 2024 | Ridge | 1476 | 8.6980 | 4.8666 | -8.4080 | 21/50 | 0.0163 | 1.9721 |
| 2024 | HistGradientBoosting | 1476 | 5.1235 | 3.3377 | -2.6485 | 19/50 | 0.2165 | 11.0444 |
| 2024 | LightGBM | 1476 | 5.1190 | 3.4468 | -2.5190 | 20/50 | 0.1430 | 11.9355 |
| 2024 | CatBoost | 1476 | 5.1192 | 3.4837 | -2.7906 | 21/50 | 1.0980 | 3.4061 |

## Selección

Modelo seleccionado entre los cuatro: **HistGradientBoosting**.

| Modelo | MAE medio entre elecciones | MAE ponderado medio | Aciertos top50 medios | Entrenar s medios |
|---|---:|---:|---:|---:|
| LightGBM | 6.8304 | 4.8385 | 21.0/50 | 0.1266 |
| HistGradientBoosting | 6.8360 | 4.6684 | 20.0/50 | 0.1996 |
| CatBoost | 6.9089 | 4.6692 | 20.5/50 | 1.0452 |
| Ridge | 9.0094 | 5.2188 | 20.0/50 | 0.0128 |

Referencia homóloga adicional: MAE medio 8.8774 pp. El modelo seleccionado mejora ese promedio.

Se prioriza MAE medio con igual peso para 2021 y 2024. Desempates: tolerancia 0.05 pp, MAE ponderado, precisión top50 (tolerancia 0.01) y tiempo de ajuste. Las diferencias de tiempo se midieron en esta CPU con un hilo, tres ajustes y diez predicciones por corte.

La selección utiliza estos dos cortes. No existe una prueba futura independiente después de seleccionar al ganador. 2024 ya fue observado en investigaciones anteriores y no se presenta como una prueba nueva ciega. La proyección 2027 continúa siendo exploratoria.

Los rangos de error se identifican como referencias retrospectivas, sin garantías probabilísticas. No se modifica Voto Vigía. Demo6 conserva predicciones precalculadas.

## Reproducción

Desde la raíz: `.venv_modelos/Scripts/python.exe umbral/modelado/comparar_modelos.py`. Dependencias exactas: `requirements_comparacion.lock.txt`. Protocolo: `PROTOCOLO_COMPARACION_4_MODELOS.md`.

Artefactos en `salidas/comparacion_modelos/`: informe JSON, predicciones por municipio y corte, proyecciones 2027 para los cuatro modelos, modelo seleccionado serializado, búsqueda de parámetros y hashes.

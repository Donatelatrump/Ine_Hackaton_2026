## Comparación de cuatro modelos ejecutada · 16 de octubre de 2026

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

La versión vigente de demo6 incluye los cuatro métodos y usa HistGradientBoosting por defecto. La documentación anterior que sigue corresponde a la etapa previa al benchmark. Fuente actual: modelado/COMPARACION_4_MODELOS.md del track.

---

# Umbral demo6

Versión actual: [abrir demo6](02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html). [Guía](02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md), [metodología](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md) y [resultados](02_Prediccion_y_escenarios_de_riesgo/modelado/RESULTADOS.md), actualizados el 16 de octubre de 2026. Voto Vigía se conserva como proyecto separado.

---

# Ine_Hackaton_2026

Proyecto **Umbral**, atlas de decisión municipal para el track 2 del Hackathon INE 2026: predicción y escenarios de riesgo de abstención, con cobertura nacional por municipio.

## Documentación

- [Explicación del proyecto y análisis general](ANALISIS_GENERAL_DEL_PROYECTO.md).
- [Por qué, qué y cómo se desarrolló](EXPLICACION_DEL_PROYECTO.md).
- [Resultados reales y limitaciones](02_Prediccion_y_escenarios_de_riesgo/modelado/RESULTADOS.md).
- [Metodología y reproducción](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md).
- [Instrucciones de la demo](02_Prediccion_y_escenarios_de_riesgo/demo/README.md).

## Ejecutar la demo

Desde la raíz del repositorio:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765. La demo preparada funciona con recursos locales y no requiere reentrenar.

## Datos y archivos grandes

El trabajo activo se limita al track 2 en `02_Prediccion_y_escenarios_de_riesgo/`: bases procesadas, código, demo, pruebas y documentación. Se retiraron las carpetas de los tracks 1 y 3. Los insumos cartográficos originales se excluyen de Git por tamaño; la demo conserva la capa preparada en `demo/data/`. La fuente y el cruce de claves de CONABIO/INEGI AGEM 2024 están documentados en [fuentes.json](02_Prediccion_y_escenarios_de_riesgo/fuentes.json) y [la guía de la demo](02_Prediccion_y_escenarios_de_riesgo/demo/README.md). `git lfs pull` no recupera los insumos originales en el estado actual.

## Trabajo en equipo

Consultar [CONTRIBUTING.md](CONTRIBUTING.md) para las responsabilidades, archivos compartidos, pruebas y flujo de pull requests. `main` es la versión integrada; las ramas `algoritmo`, `web`, `datos` y `entrega` separan las áreas de trabajo.

`Ine_Hackaton_completo.zip` es un respaldo completo **anterior a las correcciones del track 2** (generado el 5 de octubre de 2026 a las 20:42): incluye las dependencias locales y el manifiesto de sus archivos, pero **no** contiene la demo corregida, la carpeta `entrega/` ni los análisis posteriores. La entrega técnica vigente es este repositorio. Las dependencias instaladas y cachés quedan fuera del historial Git; para reproducir el análisis se reinstalan según `modelado/requirements.txt` dentro del track 2. El script `empaquetar_proyecto.py` regenera el ZIP y el manifiesto desde el estado actual y excluye los metadatos internos `.git`.

## Estado

Modelo y demo exploratorios, pruebas e integridad verificadas. Ridge mejora en el corte 2021 y pierde frente a la referencia en 2024. La proyección 2027 no constituye predicción prospectiva validada ni demuestra efectos causales. Reporte PDF de 14 páginas, presentación de 10 diapositivas, demo y base están disponibles. Registro, firmas, envío y armonización territorial histórica siguen pendientes.

La documentación vigente del track 2 está en [ANALISIS_TRACK_2.md](02_Prediccion_y_escenarios_de_riesgo/ANALISIS_TRACK_2.md). Incluye [caso municipal](02_Prediccion_y_escenarios_de_riesgo/entrega/CASO_MUNICIPAL.md) y [guion de presentación](02_Prediccion_y_escenarios_de_riesgo/entrega/GUION_PRESENTACION.md).

Actualización de escenarios: municipio, estado o México con estimación incluida; cobertura total, distribución por prioridad o proporcional a SV+NV 2024 y acciones con citas originales. El efecto trasladado a México es hipotético. Caso, reporte y presentación distinguen la evidencia publicada de reglas de planeación y supuestos. La demo muestra exclusiones y conserva fuentes y distribución en CSV.

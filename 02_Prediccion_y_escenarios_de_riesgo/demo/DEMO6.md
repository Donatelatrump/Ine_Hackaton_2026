# Umbral demo6

Versión del 16 de octubre de 2026. Abrir [demo6.html](demo6.html) con la carpeta completa. Funciona desde archivo local; los datos, Leaflet y las gráficas son locales. Los enlaces a las fuentes requieren conexión.

## Recorrido

1. Elegir año, estado y municipio. El resumen muestra abstención, participación, municipios con datos y cobertura sobre la población observable del filtro.
2. Consultar la ficha y la gráfica histórica. La línea discontinua distingue la proyección de 2027. En un municipio se añade el promedio estatal y la brecha en puntos porcentuales.
3. Comparar los métodos de 2027 y su evaluación en 2021/2024. Los coeficientes del ajuste Ridge se muestran por separado de los perfiles observados.
4. Descargar la consulta completa en CSV, incluidos los registros sin datos, sin configurar una intervención. El ranking en pantalla muestra como máximo 25 filas; la descarga abarca todo el filtro.
5. Para 2027, configurar una acción y cobertura total. Los ejemplos de 1,000 SMS o 1,000 conversaciones completadas son configuraciones editables. El plan y la gráfica antes/después usan el motor `decision.js` y conservan sus citas y supuestos.

## Navegación y selección

Mapa, resumen, gráfica, ficha y exportación comparten una selección de año, estado, municipio, método y catálogo. Cambiar el año o el método conserva el territorio y el encuadre. Cambiar de municipio sustituye la selección. El clic derecho vuelve de municipio a estado y después a México, sin recorrer municipios anteriores. El cambio de vista utiliza desvanecido, con respeto a movimiento reducido. Los territorios circundantes se desenfocan.

Para 2009–2024 se muestran valores observados, perfil disponible y calidad del año elegido. El selector de método se deshabilita porque no modifica hechos observados; el selector de año sigue activo. La simulación y las recomendaciones se ocultan en históricos. Volver a 2027 restablece la consulta prospectiva sin activar una acción automáticamente.

## Métodos y evidencia

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

El selector ofrece HistGradientBoosting, LightGBM, CatBoost, Ridge y referencia de 2021. Los cuatro regresores fueron reentrenados sobre las mismas 15 variables y cohortes. La consulta histórica permanece observada e independiente del método. La tabla muestra ambos cortes, error, aciertos y tiempos de CPU.

[Protocolo](../modelado/PROTOCOLO_COMPARACION_4_MODELOS.md), [resultados completos](../modelado/COMPARACION_4_MODELOS.md) y [metodología](../modelado/METODOLOGIA.md). El rango de la ficha usa el error P90 retrospectivo de 2021 del método activo; no es un intervalo prospectivo.

Los factores Ridge son coeficientes del Ridge reentrenado en el benchmark y no explican las predicciones de los otros modelos. La estabilidad compara referencia y método activo en NS5/10/20, con parámetros congelados. Al elegir referencia se compara con Ridge. No es probabilidad de acierto.

## Denominadores y semáforo

La media territorial es la suma de tasa × SV+NV dividida entre SV+NV de municipios con tasa disponible. Para proyecciones y simulaciones se utiliza SV+NV 2024. Para históricos se reconstruye SV+NV desde LN y NS% del mismo año. El denominador y el número de registros disponibles acompañan a la gráfica y al CSV.

La cobertura de población es SV+NV con tasa disponible / SV+NV disponible del filtro, no cobertura del electorado futuro ni de todo el territorio nacional. Sin dato no equivale a cero. Las tasas con denominador desconocido no participan en la media ponderada.

Los colores municipales y estatales usan tercios nacionales por año y método. Los estados se agregan con el mismo ponderador del resumen; no se promedian porcentajes municipales por igual. Los umbrales permanecen fijos entre escenarios de una misma consulta.

## Archivos de demo6

- `demo6.html`: entrada; carga datos y los paquetes generados.
- `src/demo6/`: código organizado en app, dominio, mapa, interfaz, vistas y compatibilidad.
- `styles/demo6/`: estilos propios por responsabilidad.
- `build.config.json`: orden de construcción.
- `assets/demo6.js`, `assets/demo6.css`, `assets/build.json`: recursos generados y procedencia.
- `decision.js`, `data/*`: motor existente y datos locales compartidos.
- `verificar_demo6.py`, `build.test.cjs`: comprobaciones de comportamiento y construcción.

Guía de componentes, arranque y reconstrucción: [src/demo6/README.md](src/demo6/README.md). El estado interno está encapsulado; `Umbral6.inspect()` sustituye el acceso de las pruebas a variables globales.

La cartografía incluye el complemento insular INEGI 2025: 308 componentes vinculados con 34 municipios. Fuentes, generalización y hashes en `data/islas_metadatos.json`. Las claves y fronteras históricas no están armonizadas.

## Documentos y reproducción

[Resultados](../modelado/RESULTADOS.md), [Metodología](../modelado/METODOLOGIA.md) y [caso municipal](../entrega/CASO_MUNICIPAL.md). Los generadores del reporte y la presentación leen cifras actuales y el caso usa Ridge explícito, independiente del método inicial de la página.

Desde la raíz:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo6.py
node --test 02_Prediccion_y_escenarios_de_riesgo/demo/demo6.test.cjs
node 02_Prediccion_y_escenarios_de_riesgo/entrega/generar_caso.cjs
python 02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/generar_reporte.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/presentacion/generar_presentacion.py
```

La comprobación de navegador requiere Playwright y Edge. Los generadores documentales utilizan las dependencias locales existentes de ReportLab y PyMuPDF. El complemento data/comparacion_modelos.js conserva los datos de las demos anteriores. Esta publicación no modifica el proyecto Voto Vigía.
# Ficha informativa en la sección 03

La sección 03 muestra primero el contexto del estado seleccionado y conserva esa ficha al consultar sus municipios. La simulación se encuentra después, en un desplegable opcional. Fuentes, alcance y reproducción: [FICHAS_ESTATALES.md](FICHAS_ESTATALES.md).


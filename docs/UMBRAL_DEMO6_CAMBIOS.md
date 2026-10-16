# Entrega de Umbral demo6

16 de octubre de 2026.

## Actualización posterior: cuatro modelos entrenados

Se ejecutó la comparación de Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables, cohortes y cortes. Se seleccionó HistGradientBoosting por empate práctico de MAE y menor error ponderado. Demo6 ya incorpora los cuatro y abre con el seleccionado. [Resultados y tiempos](../02_Prediccion_y_escenarios_de_riesgo/modelado/COMPARACION_4_MODELOS.md), [protocolo previo](../02_Prediccion_y_escenarios_de_riesgo/modelado/PROTOCOLO_COMPARACION_4_MODELOS.md) y [metodología actual](../02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md).

Se conservaron el modelo seleccionado serializado, predicciones individuales y hashes. La verificación independiente recalcula 10 filas de métricas y reproduce 1,783 proyecciones desde el modelo guardado. La regla antigua de sesgo no se utiliza en este experimento. Los apartados de límites de la primera entrega que siguen corresponden a su versión anterior, cuando aún no se habían reentrenado los cuatro modelos.

## Página

[Abrir demo6](../02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html) · [Guía de uso](../02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md).

- Consulta común de año, entidad, municipio, método y catálogo, conservando encuadre y retroceso por nivel.
- Resumen de abstención, participación, cobertura municipal y cobertura de población observable.
- Mapa y promedios territoriales ponderados con el mismo denominador.
- Brecha del municipio respecto a su estado.
- Gráfica histórica con proyección 2027 diferenciada, tabla accesible y datos ausentes sin sustituir por cero.
- Evaluación 2021/2024 y coeficientes estandarizados tomados de los artefactos actuales.
- Descarga CSV de toda la consulta, independiente del plan de intervención.
- Ejemplos editables de 1,000 SMS y 1,000 conversaciones completadas; comparación visual antes/después con escala común.
- Conserva cartografía municipal, islas, desvanecido y desenfoque de los territorios no seleccionados.

Demo6 tiene archivos propios para mapa, geografía, buscadores y aplicación. Demo5 continúa disponible. Los estilos base, datos y motor de escenarios existentes se comparten. El proyecto Voto Vigía no se modifica.

## Documentación

Se actualizaron metodología, resultados, caso municipal, README, estado del proyecto, guías de entrega y referencias a la versión vigente. Se regeneraron el reporte PDF de 14 páginas, su fuente Markdown y la presentación editable de 10 diapositivas con su PDF. La tabla editable de métricas lee los resultados actuales al regenerarse.

El caso municipal ahora aplica Ridge explícitamente: puesto 5 en la cohorte de catálogo constante, referencia puesto 3, proyección 62.071193% y posterior 62.070018% para el ejemplo de SMS. La reducción sigue siendo 0.001175 pp y los votos adicionales hipotéticos, 3. El universo nacional top50 se distingue del plan municipal.

## Validación

- 25 pruebas Node de cálculos, agregación, datos ausentes, CSV y escenarios.
- Navegador Edge sin interfaz: selección, histórico que conserva encuadre, regreso por nivel, métodos, exportación de 2,477 filas, efecto SMS y pantalla de 390 px, sin errores JavaScript.
- Reporte: 14 páginas renderizadas, revisión de límites y revisión visual.
- Presentación: 10 diapositivas y tabla nativa editable; comprobaciones estructurales y de geometría sin hallazgos ni advertencias. Se revisó el PDF de composición; no se afirma ejecución en PowerPoint.
- Inventario de Voto Vigía antes/después: comprobación de nombres, tamaños y fechas de modificación, sin alteraciones.

## Límites

Esta actualización no reentrena modelos. El método inicial sigue la selección persistencia del artefacto. La regla implementada de sesgo con signo queda descrita como una limitación y requiere una revisión experimental independiente, sin reinterpretar las métricas guardadas. CatBoost y la ampliación a secciones no se incorporan sin una evaluación comparable ni cartografía real.

Los escenarios siguen siendo hipótesis; no se validan sus efectos en México. Los rangos retrospectivos no son intervalos prospectivos calibrados. Las claves y fronteras históricas no se armonizan por esta actualización.

# Reproducción

Actualización de la demo: el catálogo de acciones y las reglas de distribución están en `demo/decision.js` y [EVIDENCIA_INTERVENCIONES.md](EVIDENCIA_INTERVENCIONES.md). La cobertura es total; se reparte por prioridad o proporcional a SV+NV 2024. Estas funciones no reentrenan el predictor ni alteran métricas históricas. Pruebas adicionales: `node --test 02_Prediccion_y_escenarios_de_riesgo/demo/intervenciones.test.cjs` y `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py`. Este último verifica el flujo vigente y regenera capturas con configuración explícita, sin servidor.

Actualización: `ampliar_analisis.py` reproduce el experimento y añade análisis posteriores y variantes, sin retuning. Escenario con SV+NV 2024, NS fuera. MAE ponderado también usa SV+NV del objetivo, corrigiendo menciones previas a LN. Comando de cifras: `python 02_Prediccion_y_escenarios_de_riesgo/modelado/imprimir_cifras.py`. Ver `../CORRECCIONES_Y_ESTADO.md`.

Desde la raíz `Ine_Hackaton`, ejecutar:

```powershell
python -m pip install --target .task_packages -r 02_Prediccion_y_escenarios_de_riesgo/modelado/requirements.txt
python -m unittest discover -s 02_Prediccion_y_escenarios_de_riesgo/modelado/tests
python 02_Prediccion_y_escenarios_de_riesgo/modelado/ejecutar.py
python 02_Prediccion_y_escenarios_de_riesgo/modelado/ampliar_analisis.py
python 02_Prediccion_y_escenarios_de_riesgo/demo/preparar_datos.py
node --test 02_Prediccion_y_escenarios_de_riesgo/demo/decision.test.cjs
```

El insumo es `datos_preparados/municipios_historico_con_calidad.csv`; su SHA256 se registra en resultados. Los originales no se modifican. La construcción de la demo descarga Leaflet 1.9.4 y simplifica una copia de la cartografía a tolerancia 0.006 grados exclusivamente para visualización. Una vez preparada, la demo funciona sin recursos externos mientras el servidor local esté activo.

Características: tasas del último proceso y último del mismo tipo, diferencia de ambas, logaritmo de LN, proporciones etarias/urbanas, NS de ambos antecedentes y tipo de elección. Todos los datos son anteriores al objetivo. Edades superiores a 120 se excluyen de proporciones etarias; no se altera la tasa agregada de votación. No se utilizan identidades individuales ni afinidad política.

Se ajusta StandardScaler y Ridge únicamente con entrenamiento previo al corte. Ridge estima un ajuste residual a la referencia del mismo tipo, alpha fijo 10; salida truncada a [0,100]. Etiquetas de entrenamiento 2015/2018 para 2021 y 2015/2018/2021 para 2024. El ajuste final para 2027 incorpora etiquetas hasta 2024. MAE ponderado utiliza SV+NV del objetivo histórico; el top50 se compara dentro de la misma cohorte elegible para ambos métodos.

El bootstrap agrupa por entidad (500 réplicas, semilla 123) como sensibilidad espacial. No incluye incertidumbre temporal ni establece estabilidad para próximas elecciones. Sensibilidades NS y catálogos son análisis adicionales, sin reajustar alpha ni la regla elegida.

API de referencia: [Ridge](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html), [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html). Versiones fijadas en requirements; código y archivos auditables disponibles localmente. Interpretación y límites en `RESULTADOS.md`.

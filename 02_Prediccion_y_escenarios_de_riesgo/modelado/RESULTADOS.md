# Resultado de la comparación temporal

Actualización: [correcciones y nuevas métricas](../CORRECCIONES_Y_ESTADO.md). Reporte y presentación ya generados, escenario SV+NV 2024 y mapa Base/Intervención/Δ. Registro, firmas y envío siguen sin acreditar; requisitos humanos no se completaron automáticamente.

La propuesta ahora responde una decisión concreta: con capacidad para atender N municipios, cuáles revisar primero, con qué calidad y bajo qué supuestos. La complejidad del modelo queda subordinada a evidencia observable.

| Corte | Método | Municipios evaluados | MAE (pp) | MAE ponderado (pp) | Aciertos top 50 |
|---|---|---:|---:|---:|---:|
| 2021 | Última elección del mismo tipo | 1,490 | 12.12 | 8.05 | 16/50 |
| 2021 | Ridge, alpha=10 | 1,490 | 9.21 | 5.49 | 19/50 |
| 2024 | Última elección del mismo tipo | 1,476 | 5.64 | 3.54 | 27/50 |
| 2024 | Ridge, alpha=10 | 1,476 | 8.58 | 4.49 | 27/50 |

Ridge satisface la regla fijada para 2021: MAE al menos 1% menor y métricas ponderada/top50 no peores. Reduce el MAE 23.9% en ese corte, pero solo recupera 19 de los 50 municipios con mayor abstención observada. En 2024 pierde frente a la referencia. No se ajustaron parámetros para ocultar ese resultado: la mejora no es consistentemente transferible.

2021 se usa para seleccionar, no constituye evaluación independiente posterior a selección. 2024 es presidencial; no valida una futura elección intermedia. Hay seis ocasiones electorales nacionales y solo tres intermedias, aunque las fuentes sumen millones de filas. La proyección 2027 es exploratoria, útil para revisión, sin afirmar precisión futura.

## Calidad y sensibilidad

La cobertura cartográfica incluye 2,477 claves INE. Se proyectan 1,783; 694 quedan sin estimación, nunca con riesgo cero. Se exige NS ≤10% y antecedentes observables en el último proceso y el último del mismo tipo. La evaluación exige además objetivo observable y NS ≤10%; por tanto es condicional a calidad, no representativa de todos los municipios.

En 2021, al exigir NS ≤5%, se evalúan 1,007 municipios: MAE referencia 12.69/Ridge 9.86 pp, top50 20/23 aciertos. Con NS ≤20%, se evalúan 1,960: MAE 12.20/9.16 pp, top50 13/15. Las cohortes cambian: estas cifras son sensibilidad, no resultados sobre el mismo universo.

En entidades con catálogos de claves constantes, el corte 2021 comprende 1,050 municipios y 2024 comprende 948. Se mantiene la ventaja de MAE en 2021 y la pérdida en 2024. El filtro por catálogo deja 1,144 estimaciones actuales; es un proxy conservador y no prueba que los límites municipales sean idénticos. Falta armonizar límites históricos para sustentar comparabilidad territorial más fuerte.

El rango mostrado en 2027 es estimación ±21.05 pp, percentil 90 del error absoluto de Ridge en 2021, truncado a [0,100]. Es ilustrativo y amplio; no es intervalo probabilístico calibrado ni garantiza cobertura del 90% en 2027. El semáforo divide estimaciones válidas en tercios nacionales, no representa probabilidades de un evento.

## Escenario operativo

Selección por criterio editable (tasa, volumen sobre observados o variación), empate por clave. Capacidad N, alcance y respuesta son editables. Participación adicional hipotética = alcance limitado × tasa estimada /100 × respuesta /100. Alcance limitado y reducción sobre SV+NV 2024, con NS fuera, sin proyectar electorado 2027. Se supone que las personas alcanzadas presentan la tasa observada; no existe evidencia causal ni costos monetarios inventados. La exportación registra supuestos y ficha preventiva.

## Para competir

El diferencial defendible es una decisión revisable, con calidad, referencia simple, resultados adversos visibles y restricciones de capacidad. Reporte de 12 páginas y presentación de 10 diapositivas disponibles en `entrega/`. Faltan revisión territorial/institucional, armonización o justificación de límites, confirmación de registro y firmas/envío oficiales. No se garantiza ganar ni se presenta como sistema validado para asignación definitiva de recursos.

Evidencia íntegra: `salidas/metricas.json`, `salidas/backtest_predicciones.csv`, `salidas/metricas_entidad.csv`, `salidas/proyeccion_exploratoria_2027.csv`. Fuentes: [CCPC INE](https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/) y [cartografía INE](https://pautas.ine.mx/transparencia/mapas/index_2025.html).

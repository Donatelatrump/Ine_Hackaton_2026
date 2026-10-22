# Caso municipal vigente: SOLIDARIDAD, clave histórica 23008

Revisado el 22 de octubre de 2026 con los resultados del experimento del 16 de octubre. Modelo seleccionado: HistGradientBoosting. Nombre y límites del catálogo histórico, sin certificar denominación o fronteras actuales.

Abrir demo/demo7.html, Quintana Roo, clave 23008, año 2027, HistGradientBoosting y catálogo constante. Elegir SMS Suecia, cobertura total de 1,000 personas. Los puestos nacionales usan la cohorte de catálogo constante; no son el ranking local de un único municipio. Este ejemplo es independiente del plan estatal de cobertura inicial del 10% y efecto supuesto de 1.5 pp.

| Indicador | Valor |
|---|---:|
| Puesto del modelo seleccionado | 9 |
| Puesto Ridge (benchmark) | 4 |
| Puesto de referencia | 3 |
| Proyección del modelo seleccionado | 61.636222% |
| Referencia 2021 | 66.300075% |
| Base SV+NV 2024 | 255,362 |
| Frecuencia nacional top50 | 4/6 |
| Cobertura total SMS | 1,000 personas asignadas |
| Votos adicionales hipotéticos | 3 |
| Rango externo trasladado | 1.3–4.8 |
| Proyección posterior | 61.635048% |
| Reducción municipal | 0.001175 pp |

H = 1,000 × 0.30 / 100 = 3. Posterior = antes - 100 × H / 255,362. El efecto ITT cuenta asignación a SMS, no lectores efectivos. Fuente: Lindgren, Nyman y Oskarsson (2025), DOI 10.1017/S0007123424000504. El traslado a México es hipotético, no validado. El rango externo no incluye incertidumbre del predictor ni de transferencia.

Los puestos y la frecuencia son del ranking nacional top50 con catálogo constante. Las sensibilidades comparan referencia y método activo con parámetros congelados en NS5/10/20. La cobertura no es capacidad institucional confirmada. Validar población, canal, atribuciones, capacidad y protocolo antes de un piloto.

Reproducción: entrega/generar_caso.cjs, que lee demo/data/comparacion_modelos.json. El JSON del caso y esta documentación sustituyen la etapa anterior que usaba Ridge explícito.

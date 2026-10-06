# Correcciones aplicadas — Tecnocalidos

5 de octubre de 2026. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum.

| Recomendación | Implementación y límites |
|---|---|
| Mínimos técnicos | Reporte PDF 12 páginas; PPTX/PDF 10 diapositivas; mapa y CSV. Cartas oficiales sin firmas; registro/envío no acreditados |
| Núcleo robusto | Dos métodos × NS 5/10/20, topN por filtro/lente. 6/6 indica estabilidad entre variantes, no probabilidad; elegibilidad aparte |
| Error por tamaño | MAE y P90 por SV+NV previo: <10 mil, 10–100 mil, ≥100 mil; retrospectivos, no intervalos futuros |
| Semáforo | Spearman, precisión/recobrado rojo con umbral del entrenamiento congelado; tercio alto real del test como comparación separada |
| Calidad | NS, catálogo y acuerdo en ficha/lista, capa opcional de estabilidad, gris con motivo específico |
| Escenario | Base/Intervención/Δ, umbrales base fijos; inversión de alcance/respuesta y factibilidad |
| Denominador | SV+NV 2024 para alcance máximo, reducción y ponderación; NS fuera, LN aparte |
| Prevención | Perfil observable, acción, responsable propuesto, cobertura, condiciones, personas como recurso, medición y mecanismo hipotético |
| Piloto | Aleatorización propuesta en ventana elegible alrededor del corte N con balance y evaluación; cercanía del score no acredita equivalencia ni causalidad |
| Lentes | Tasa, volumen observable, variación frente al mismo tipo y solapamiento |
| Operación | Resumen por entidad; no se inventa correspondencia distrital |
| Verificabilidad | index.html abre con file://; comando `python 02_Prediccion_y_escenarios_de_riesgo/modelado/imprimir_cifras.py` |

## Resultados adicionales, posteriores al experimento original

Alpha=10, cortes y selección originales conservados. Métricas definidas antes de calcularlas, **después** de conocer resultados originales: análisis posteriores, no evaluación independiente ni preespecificación original.

| Corte | Método | Spearman | Precisión roja | Recobrado rojo | Rojos predichos |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia | 0.485 | 46.76% | 81.52% | 849 |
| 2021 | Ridge | 0.599 | 54.89% | 73.72% | 654 |
| 2024 | Referencia | 0.827 | 88.50% | 37.88% | 113 |
| 2024 | Ridge | 0.811 | 98.18% | 20.45% | 55 |

Estas cifras usan umbral del entrenamiento, no tercio de la prueba. La comparación contra tercio alto real aparece por separado en demo/JSON. Precisión alta con bajo recobrado no demuestra buena cobertura. La demo 2027 usa tercios de tasas base nacionales, fijos entre escenarios; evaluación histórica no calibra ese futuro. Ridge sigue perdiendo MAE en 2024.

**Corrección documental:** MAE ponderado original ya usaba SV+NV del objetivo; menciones previas a LN eran incorrectas. Se corrige narración sin alterar cifras. El escenario original sí usaba LN y se alinea ahora con SV+NV.

## Pendientes humanos

Confirmar registro, elegibilidad y composición paritaria según convocatoria, sin inferir por nombres. Completar/firmar cartas por todos los integrantes. Revisar documentos: PPTX verificado estructuralmente, PDF gemelo revisado visualmente; no motor PowerPoint disponible. Enviar por medio/plazo oficiales: no se envió correo ni se hizo público GitHub. El paquete técnico se conserva como respaldo previo a estas correcciones; la entrega vigente es el repositorio, que incluye el código y la demo corregida. Para reconstruir el ZIP actualizado: `python empaquetar_proyecto.py`. Validar responsables, recursos, límites históricos y piloto antes de aplicación institucional.

Los documentos anteriores conservan el diagnóstico inicial. Esta actualización y el reporte prevalecen para funcionalidad y escenario actuales.

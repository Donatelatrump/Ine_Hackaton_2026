## Comparación de cuatro modelos ejecutada · 16 de octubre de 2026

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

La versión vigente de demo6 incluye los cuatro métodos y usa HistGradientBoosting por defecto. La documentación anterior que sigue corresponde a la etapa previa al benchmark. Fuente actual: modelado/COMPARACION_4_MODELOS.md del track.

---

# Estado de demo6 · 16 de octubre de 2026

Demo6 incorpora consulta unificada, mapa y resúmenes ponderados, serie temporal con proyección diferenciada, brecha municipal-estatal, métricas reales, coeficientes Ridge y descarga CSV independiente de la simulación. Presets SMS/llamada con supuestos explícitos. Consulta histórica sin recomendaciones ni proyecciones del pasado.

Ridge mejora el error medio en 2021 (8.90 frente a 12.12 pp) y empeora en 2024 (8.96 frente a 5.64 pp). La referencia recupera 27 de los 50 municipios prioritarios en 2024 y Ridge 21. No hay evidencia de superioridad consistente.

El artefacto actual identifica persistencia como método seleccionado y alpha final 500 para el ajuste Ridge. Demo6 inicia con la referencia de 2021 y permite comparar Ridge. La condición de sesgo implementada compara el cambio con signo: (sesgo candidato - sesgo referencia) >= -3 pp. Con 3.72 - 7.87 = -4.14 pp en 2021, rechaza Ridge aunque disminuya el sesgo absoluto. Esta selección describe el código vigente; no demuestra que la referencia sea universalmente superior. Corregir esa regla y regenerar modelos requiere un experimento separado, sin alterar retrospectivamente esta evaluación.

Las cifras y rangos actuales sustituyen las menciones fijas de versiones previas. Evidencia técnica: [guía demo6](demo/DEMO6.md) y [metodología](modelado/METODOLOGIA.md). Voto Vigía no se modifica.

---

# Correcciones aplicadas — aguas.exe

5 de octubre de 2026. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum.

| Recomendación | Implementación y límites |
|---|---|
| Mínimos técnicos | Reporte PDF 14 páginas (8 secciones); PPTX/PDF 10 diapositivas; mapa y CSV. Cartas oficiales sin firmas; registro/envío no acreditados |
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

## Mejoras de decisión aplicadas (5 de octubre de 2026)

El modelo permanece congelado (alpha=10, cortes y selección originales). Se añadieron capas de explicación y decisión, sin reentrenar:

| Mejora | Implementación y límites |
|---|---|
| Ficha «¿Por qué este municipio?» | Posición de prioridad, riesgo, estabilidad, estimación, razones (comparable, último proceso, jóvenes, urbano, NS, acuerdo de métodos), robustez 6/6, acción, hipótesis y forma de evaluarla |
| Estabilidad de prioridad | Frecuencia con que el municipio entra en la selección entre las seis variantes (2 métodos × NS 5/10/20). No es probabilidad. El rango ±21.05 pp se mueve a una nota técnica |
| Perfil CCPC separado | Abstención observada por edad, sexo y tipo de sección (2021 y 2024), calculada directo de los ZIP. Capa explicativa posterior: no alimenta a Ridge, referencia ni prioridad; no implica causalidad |
| Modo Director | Capacidad territorial (municipios) o humana (personas alcanzables), estabilidad mínima, plan sugerido y descarga |
| Frontera de decisión | Núcleo robusto 6/6, zona de revisión 1/6–5/6 y fuera. El piloto aleatorio se propone dentro de la frontera |

Verificación vigente: 15 pruebas Python, 12 Node y 24 comprobaciones de navegador (incluida apertura `file://`), más integridad de artefactos. Detalle en `docs/superpowers/plans/2026-10-05-ficha-perfil-y-frontera.md`.

## Pendientes humanos

Confirmar registro, elegibilidad y composición paritaria según convocatoria, sin inferir por nombres. Completar/firmar cartas por todos los integrantes. Revisar documentos: PPTX verificado estructuralmente, PDF gemelo revisado visualmente; no motor PowerPoint disponible. Enviar por medio/plazo oficiales: no se envió correo ni se hizo público GitHub. El paquete técnico se conserva como respaldo previo a estas correcciones; la entrega vigente es el repositorio, que incluye el código y la demo corregida. Para reconstruir el ZIP actualizado: `python empaquetar_proyecto.py`. Validar responsables, recursos, límites históricos y piloto antes de aplicación institucional.

El reporte se reestructuró a 14 páginas y 8 secciones (portada, problema, datos, modelo, evidencia, semáforo, escenarios, prevención, viabilidad) con la incertidumbre de prioridad, la capacidad territorial o humana y las nuevas capas. La presentación se actualizó el 6 de octubre: ficha de decisión, perfil descriptivo, estabilidad, frontera y caso 23008. Reporte, presentación y documentación comparten denominadores y límites.

## Unificación de entrega (6 de octubre de 2026)

Actualización posterior de la página: recorrido capacidad → prioridades → intervención; controles y evidencia técnica desplegables; ficha con datos observados, estimación exploratoria y escenario separados; reducción en puntos porcentuales; contador y consulta de municipios sin estimación. Sin estimación deja de mostrar puesto cero o zona de revisión y no participa en ranking ni simulación. Ver `demo/README.md` para el flujo actual y `demo/verificacion/resultado.json` para la verificación vigente. Las métricas y el modelo permanecen congelados.

Se reemplazó el diagnóstico desactualizado por el análisis vigente, se corrigieron referencias residuales a LN en el escenario y se actualizó la presentación a diez diapositivas con ficha, frontera y caso municipal. «Estabilidad de selección» reemplaza «confianza» en textos visibles: no acredita probabilidad de acierto y las variantes pueden equivocarse juntas. Identificadores internos y columna CSV `confianza_prioridad` permanecen compatibles.

Caso y cifras reproducibles: [CASO_MUNICIPAL.md](entrega/CASO_MUNICIPAL.md). Discurso y recorrido: [GUION_PRESENTACION.md](entrega/GUION_PRESENTACION.md). Modelo, alpha, cortes y métricas originales sin cambios. Planes históricos conservados como registros, no como estado vigente. Verificación de esta actualización: `entrega/verificacion_unificacion.json`.

Actualización de escenarios: municipio, estado o México con estimación incluida; cobertura total, distribución por prioridad o proporcional a SV+NV 2024 y acciones con citas originales. El efecto trasladado a México es hipotético. Caso, reporte y presentación distinguen la evidencia publicada de reglas de planeación y supuestos. La demo muestra exclusiones y conserva fuentes y distribución en CSV.

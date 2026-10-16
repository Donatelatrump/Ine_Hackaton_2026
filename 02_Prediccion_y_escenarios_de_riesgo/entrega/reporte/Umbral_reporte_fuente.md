# Umbral: reporte metodológico y preventivo
Versión técnica para revisión | 16 de octubre de 2026
Estructura de 14 páginas (8 secciones)

## Página 1: Resumen ejecutivo

### Reporte metodológico y preventivo · Reto 2
aguas.exe. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Versión técnica para revisión, 16 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios 2009-2024. Presupuesto de 15 páginas; este documento usa 14.

### Resumen ejecutivo
Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027. Demo6 muestra la consulta histórica y proyecciones precalculadas, comparación estatal, exportación de consultas y escenarios hipotéticos con cobertura total y fuentes.

### Qué es y qué no es
Es una herramienta de priorización auditable y un registro explícito de supuestos. No es un predictor validado de 2027, no es un asignador automático de recursos y no demuestra efectos causales de una intervención.

## Página 2: Para qué sirve y para quién

### Pregunta operativa
Con una cobertura total de personas, ¿cómo distribuir una acción en un municipio, un estado o el país y qué cambio hipotético permite suponer la evidencia externa? La cobertura es un único presupuesto territorial, no una cantidad repetida por municipio.

### Criterio de prioridad y selector
La prioridad principal es la tasa de abstención estimada, no el número absoluto ni el deterioro. El prototipo permite elegir entre tres lentes que responden preguntas distintas: tasa (proporción estimada), volumen sobre la población observable (cuántas abstenciones) y deterioro frente a la última elección del mismo tipo. Cambiar el lente cambia la lista; la elección responde al objetivo institucional declarado, no a un valor universal.

### Persona usuaria y flujo de uso
Un área de educación cívica elige municipio, estado o país, catálogo, método y criterio; define cobertura total, distribución y acción; revisa estimaciones, exclusiones y evidencia; compara el territorio completo y descarga el plan.

## Página 3: De conteos a una base comparable

### Fuente y volumen auditado
Conteos Censales de Participación Ciudadana del INE, seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y 2024, agregados y disociados, sin datos personales. Se auditaron 54,872,712 filas de 192 CSV con integridad CRC, duplicados y reconciliación de conteos, y se generaron 14,779 registros municipio-año y 2,477 claves. Prisión preventiva y voto anticipado se conservan como fuentes separadas. Fuente: auditoria/ y datos_preparados/.

### Definiciones
SV: participación registrada. NV: no participación. NS: participación no especificada. LN = SV + NV + NS. Abstención observable (%) = 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. La suma de conteos precede al cálculo de porcentajes: una tasa vacía es denominador cero, no abstención de cero.

### Reglas de calidad y cobertura
Se exige NS ≤10% en el antecedente más reciente y en el del mismo tipo; la evaluación exige además objetivo observable con NS ≤10%. En 2027 hay 1,783 municipios con estimación y 694 sin estimación sobre 2,477 claves. La exclusión por calidad puede apartar zonas con necesidad alta: es un sesgo de cohorte que debe declararse. Fuente: modelado/salidas/metricas.json.

### Límite territorial
Se conservan 2,477 claves, con proyección NS10 para 1,783. La cartografía incorpora 308 componentes insulares oficiales. Los límites históricos no están armonizados y la coincidencia de claves no prueba continuidad territorial.

## Página 4: Variables usadas, omitidas y trazabilidad

Variables del predictor en modelado/core.py: Abstención del mismo tipo, Abstención del último proceso, Diferencia último − mismo tipo, log(LN), Proporción 18-29, Proporción 60+ (sin >120), Proporción urbana, NS de ambos antecedentes, Tipo de elección (intermedia), Interacciones electorales, Indicadores complementarios.

### Variables omitidas y por qué
Sexo, escolaridad y variables externas no verificadas no forman parte del predictor. Sexo existe en la fuente y se usa solo en la capa explicativa posterior (sección de prevención); el modelo conserva variables agregadas verificables para reducir sobreajuste y fuga. La representación etaria es agregada; no se infieren características individuales.

### Trazabilidad
Cada cifra proviene de archivos citados en el pie de tabla o en el texto: datos_preparados/municipios_historico_con_calidad.csv, modelado/salidas/metricas.json, evaluacion_adicional.json y perfil_demografico.json. El diccionario de datos y las tablas largas viven en la base CSV y el repositorio, no en este PDF.

## Página 5: Referencia homóloga y cuatro regresores

### Referencia
Predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye por otro tipo electoral. Es interpretable y constituye la exigencia mínima que la complejidad debe superar.

### Cuatro regresores
Se comparan cuatro regresores del residual respecto a la misma referencia: Ridge, HistGradientBoosting, LightGBM y CatBoost. Todos usan las mismas 15 variables históricas y cohortes. Cuatro configuraciones por familia, semilla 42 y un hilo de CPU. No se añaden variables futuras ni categóricas a un único competidor.

### Flujo simple
Antecedentes observados con calidad verificada → Referencia del mismo tipo → Ajuste del residual con el modelo seleccionado → Estimación 2027 → Semáforo relativo, estabilidad y decisión con capacidad.

## Página 6: Construcción, cortes y regla de selección

### Cortes temporales
Evaluación 2021: entrenamiento 2015/2018 y validación interna 2018 con entrenamiento 2015. Evaluación 2024: entrenamiento 2015/2018/2021 y validaciones internas 2018/2021 con años anteriores. Para 2027 se entrena hasta 2024. No se ajusta ni detiene el aprendizaje con el corte externo.

### Regla de selección
Menor MAE medio, igual peso para 2021 y 2024. Diferencias ≤0.05 pp se desempatan por MAE ponderado; después top50 y tiempo. HistGradientBoosting y LightGBM empatan dentro de la tolerancia; gana el primero por su menor MAE ponderado. La regla previa de sesgo con signo no se usa en este experimento.

### Selección retrospectiva
Los dos backtests participan en la selección final. 2024 ya fue examinado en etapas anteriores del proyecto. No hay una elección futura independiente después de elegir al ganador; la proyección 2027 sigue siendo exploratoria.

## Página 7: Comparación temporal de cuatro modelos

| Corte / método | n | MAE pp | Pond. pp | Top50 |
|---|---|---|---|---|
| 2021 / Referencia | 1490 | 12.116 | 8.052 | 16/50 |
| 2021 / Ridge | 1490 | 9.321 | 5.571 | 19/50 |
| 2021 / HistGradientBoosting | 1490 | 8.549 | 5.999 | 21/50 |
| 2021 / LightGBM | 1490 | 8.542 | 6.230 | 22/50 |
| 2021 / CatBoost | 1490 | 8.699 | 5.855 | 20/50 |
| 2024 / Referencia | 1476 | 5.639 | 3.541 | 27/50 |
| 2024 / Ridge | 1476 | 8.698 | 4.867 | 21/50 |
| 2024 / HistGradientBoosting | 1476 | 5.123 | 3.338 | 19/50 |
| 2024 / LightGBM | 1476 | 5.119 | 3.447 | 20/50 |
| 2024 / CatBoost | 1476 | 5.119 | 3.484 | 21/50 |

### Lectura honesta
Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

### Resultados y límites de priorización
Se publican MAE, error ponderado, sesgo con signo, P90 y aciertos top50 para cada método y corte. En 2024 la referencia recupera 27/50 frente a 19/50 de HistGradientBoosting: mejorar error no garantiza mejor priorización. Fuente: modelado/salidas/comparacion_modelos/resultados.json.

## Página 8: Estabilidad, incertidumbre y límites

### Estabilidad del top N
Seis variantes: referencia y método activo, con calidad NS5/10/20. Al consultar referencia, el comparador es Ridge. Se fijan los parámetros elegidos en NS10 y se reentrena sobre cada cohorte. La frecuencia describe el ranking topN; no es probabilidad ni se utiliza para elegir al ganador.

### Incertidumbre de prioridad, no de intervalo
Cada método muestra su P90 retrospectivo de 2021. Para HistGradientBoosting, ±18.04 pp, acotado a [0,100]. No es intervalo prospectivo calibrado. La estabilidad compara referencia y método activo en NS5/10/20 con parámetros finales congelados; no interviene en la selección del ganador.

### Error por tamaño y límites
El P90 del error por denominador observable previo (<10 mil, 10-100 mil, ≥100 mil) describe heterogeneidad por escala, no un intervalo para 2027. Límites: seis ocasiones electorales y tres intermedias; 2024 es presidencial y no valida 2027; sin causalidad; selección por calidad que puede excluir zonas con necesidad alta.

## Página 9: Clasificación territorial y estabilidad

### Tercios relativos
Bajo, medio y alto son tercios de las estimaciones nacionales válidas. Alto es el tercio superior de tasas estimadas; no es probabilidad calibrada de deterioro. Gris significa información insuficiente para estimar, se muestra con motivo de exclusión y nunca recibe riesgo cero.

### Eje de estabilidad
La calidad (NS), la estabilidad entre seis variantes y el acuerdo entre métodos se informan como dimensión separada del color, en la lista y en la ficha. Los umbrales base permanecen fijos al comparar escenarios para que el color no se redefina entre ellos.

### Sensibilidad de umbrales
Mover el corte cambia el número de municipios por nivel; el informe incluye variación por tamaño municipal y por umbral NS. Ejemplo: alternar el filtro de catálogo constante pasa de 1,144 a 1,783 estimaciones. Fuente: modelado/salidas/metricas.json.

(FIGURE_MAP_STATES)

## Página 10: Sin intervención y con intervención hipotética

### Fórmulas del escenario
O = SV2024 + NV2024. E es cobertura asignada, limitada por O. Acción con evidencia: H = mínimo(E × efecto_pp/100, E × tasa/100). Personalizada: H = E × tasa/100 × respuesta/100, sin evidencia causal. Tasa posterior = tasa - 100 × H/O. La comparación pondera por O TODOS los municipios estimables filtrados, incluidos los no atendidos (H=0).

### Supuestos explícitos
O es referencia observable 2024, no electorado 2027. Transferencia del efecto extranjero a México hipotética y no validada. ITT usa personas asignadas a SMS; ATT exige contactos efectivos para llamada. No sumar acciones ni efectos. País: «México: municipios con estimación incluidos»; catálogo y exclusiones explícitos.

(FIGURE_TRIPLE)

### Escenario invertido y ejemplo
Para un objetivo, H requerido = O × (tasa - umbral)/100. Con coeficiente externo, cobertura requerida = H/(efecto_pp/100); personalizada usa H/((tasa/100) × (respuesta/100)). Debe respetar O y presupuesto. Caso 23008: SMS Suecia a 1,000 personas supone 3 votos adicionales y reducción 0.001175 pp; sigue alto.

## Página 11: Tipologías observables y línea de acción

### Tipologías por perfil observable
Se derivan tipologías de información agregada, no de personas: territorio con menor proporción urbana; proporción joven 18-29 ≥25%; proporción 60+ ≥25%; y calidad insuficiente (NS alto o antecedentes incompletos). Cada tipología lleva una línea de acción: información electoral accesible, talleres en espacios educativos y comunitarios, material legible, o revisión de datos antes de priorizar.

### El perfil no decide, explica
La prioridad la fija el modelo; la tipología orienta a quién podría dirigirse una intervención. El perfil CCPC por edad, sexo y tipo de sección es una capa explicativa posterior que nunca alimenta al modelo y no implica causalidad; los grupos con muestra insuficiente se marcan como tales. Fuente: modelado/salidas/perfil_demografico.json.

### Mecanismo como hipótesis
SMS Suecia: ITT 0.30 pp [0.13,0.48], Lindgren, Nyman y Oskarsson (2025), resultados, figura 1; DOI 10.1017/S0007123424000504. SMS EEUU: ITT 0.25 pp, IC95% [0.17,0.34], Haenschen, Mann y DeMora (2026), introducción; DOI 10.1007/s11109-026-10121-2. Plan de voto por llamada: ATT 4.1 pp, EE 1.7, ITT publicado 0.9 pp; Nickerson y Rogers (2010), pp.194-199, tabla 1; DOI 10.1177/0956797609359326. ATT exige contacto efectivo: no intentos ni talleres. No sumar acciones. México requiere validación propia.

## Página 12: Ficha tipo y ejemplo completo

### Ficha tipo
Cada recomendación registra: condición observable, acción, responsable propuesto, cobertura, condiciones de aplicación, recurso (personas y horas), medición y mecanismo hipotético.

### Caso 23008: SOLIDARIDAD (catálogo histórico)
HistGradientBoosting, catálogo constante: puesto 9; referencia 3. Proyección 61.636222%. Frecuencia nacional top50 4/6. SMS Suecia a 1,000 personas asignadas: 3 votos hipotéticos [1.3,4.8], posterior 61.635048%, reducción 0.001175 pp. Base 255,362. La transferencia del efecto a México requiere evaluación. Fuente: entrega/caso_municipal.json.

### El resto, en el CSV
La ficha completa de cada municipio seleccionado se exporta en el plan CSV; este PDF incluye un ejemplo representativo.

## Página 13: Priorización de recursos y diseño de evaluación

### Priorización de recursos
Cobertura total limitada a población observable elegible. Prioridad concentra cupo siguiendo ranking hasta agotarlo. Proporcional distribuye según SV+NV2024 entre todos los elegibles, redondeo por mayor resto y desempate determinista. Son decisiones del proyecto, no reglas de la literatura. Con coeficiente homogéneo y sin activar el límite de abstenciones, igual cobertura produce igual H total: cambia dónde se asigna, no necesariamente el impacto agregado. Estabilidad de referencia separada del reparto actual.

### Diseño de evaluación propuesto
Aleatorizar atención inmediata o diferida entre municipios cercanos al corte de capacidad, con balance por entidad, tamaño, calidad y contexto; indicadores de cobertura y comprensión; y regla de análisis fijada antes de observar resultados. La cercanía del score no acredita equivalencia ni causalidad.

### Vista operativa
Demo6 conserva año y territorio al cambiar de método, muestra históricos sin proyecciones del pasado, agrega resumen ponderado y brecha estatal, gráfica temporal y exportación de toda la consulta. La simulación compara antes/después con presets editables. Cartografía municipal e islas INEGI, con límites históricos sin armonizar.

## Página 14: Qué se puede defender hoy y qué falta

| Se puede defender hoy | Falta evidencia o validación |
|---|---|
| Marco de decisión con capacidad y criterio explícitos | Aceptación institucional del flujo y de los responsables. |
| Auditoría de datos y calidad visible | Armonización histórica de límites municipales. |
| Comparación honesta con la referencia (2021 y 2024) | Validación prospectiva; 2024 adverso no se oculta. |
| Análisis posteriores congelados (rango, tamaño, estabilidad) | Semáforo calibrado como probabilidad; hoy es relativo. |
| Escenarios y fichas preventivas revisables | Costos monetarios y efecto causal. |
| Reproducibilidad local (mapa, cifras, código) | Piloto ejecutado y evaluado. |

### Riesgos de uso
Uso automático de la lista como asignación definitiva; lectura causal del escenario; y falacia ecológica al pasar del municipio a la persona. Se mitigan con revisión humana, etiquetando el escenario como hipótesis y sin inferir comportamiento individual del agregado.

### Reproducibilidad y cierre
Abrir demo/demo6.html. Se ejecutaron comparar_modelos.py, publicar_comparacion_demo6.py y verificar_comparacion.py en Python 3.12 con dependencias fijadas. Se conservan predicciones por fila, modelo serializado y hashes. La interacción usa proyecciones precalculadas. Fuentes: protocolo y comparación de cuatro modelos en modelado/. Voto Vigía no se modifica.

# Umbral: reporte metodológico y preventivo
Versión técnica para revisión | 5 de octubre de 2026
Estructura de 14 páginas (8 secciones)

## Página 1: Resumen ejecutivo

### Reporte metodológico y preventivo · Reto 2
Tecnocalidos. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Versión técnica para revisión, 5 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios 2009-2024. Presupuesto de 15 páginas; este documento usa 14.

### Resumen ejecutivo
Umbral apoya una decisión acotada: con capacidad para atender N municipios, ¿cuáles revisar primero, con qué respaldo y qué puede hacerse después? El método compara una referencia sencilla (última elección del mismo tipo) con un ajuste Ridge regularizado, con calidad de datos visible y análisis posteriores congelados. Hallazgo principal: Ridge mejora el error en 2021 y empeora frente a la referencia en 2024; no se declara ganador. La propuesta preventiva son fichas revisables con acción, responsable, cobertura y medición, más un piloto aleatorio propuesto alrededor del corte de capacidad. El alcance de uso es la deliberación institucional; no es asignación automática de recursos.

### Qué es y qué no es
Es una herramienta de priorización auditable y un registro explícito de supuestos. No es un predictor validado de 2027, no es un asignador automático de recursos y no demuestra efectos causales de una intervención.

## Página 2: Para qué sirve y para quién

### Pregunta operativa
Si un área de educación cívica dispone de capacidad para atender N municipios, ¿cuáles conviene revisar primero, qué antecedentes respaldan su prioridad y cómo cambia un escenario al variar alcance y respuesta supuesta?

### Criterio de prioridad y selector
La prioridad principal es la tasa de abstención estimada, no el número absoluto ni el deterioro. El prototipo permite elegir entre tres lentes que responden preguntas distintas: tasa (proporción estimada), volumen sobre la población observable (cuántas abstenciones) y deterioro frente a la última elección del mismo tipo. Cambiar el lente cambia la lista; la elección responde al objetivo institucional declarado, no a un valor universal.

### Persona usuaria y flujo de uso
La persona usuaria es un área de educación cívica o planeación territorial que define territorio y capacidad. Flujo en cuatro pasos: 1) definir territorio, capacidad y criterio; 2) revisar mapa y lista priorizada; 3) inspeccionar calidad, confianza y antecedentes; 4) descargar el plan con supuestos y escenario.

## Página 3: De conteos a una base comparable

### Fuente y volumen auditado
Conteos Censales de Participación Ciudadana del INE [2], seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y 2024, agregados y disociados, sin datos personales. Se auditaron 54,872,712 filas de 192 CSV con integridad CRC, duplicados y reconciliación de conteos, y se generaron 14,779 registros municipio-año y 2,477 claves. Prisión preventiva y voto anticipado se conservan como fuentes separadas. Fuente: auditoria/ y datos_preparados/.

### Definiciones
SV: participación registrada. NV: no participación. NS: participación no especificada. LN = SV + NV + NS. Abstención observable (%) = 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. La suma de conteos precede al cálculo de porcentajes: una tasa vacía es denominador cero, no abstención de cero.

### Reglas de calidad y cobertura
Se exige NS ≤10% en el antecedente más reciente y en el del mismo tipo; la evaluación exige además objetivo observable con NS ≤10%. En 2027 hay 1,783 municipios con estimación y 694 sin estimación sobre 2,477 claves. La exclusión por calidad puede apartar zonas con necesidad alta: es un sesgo de cohorte que debe declararse. Fuente: modelado/salidas/metricas.json.

### Límite territorial
Una clave municipal constante no prueba límites ni población constantes. No hay armonización histórica de fronteras y los conteos no se redistribuyeron a los límites de 2024. Se excluyen edades mayores de 120 al construir proporciones etarias, conservando los conteos originales.

## Página 4: Variables usadas, omitidas y trazabilidad

Variables del predictor en modelado/core.py: Abstención del mismo tipo, Abstención del último proceso, Diferencia último − mismo tipo, log(LN), Proporción 18-29, Proporción 60+ (sin >120), Proporción urbana, NS de ambos antecedentes, Tipo de elección (intermedia).

### Variables omitidas y por qué
Sexo, escolaridad y variables externas no verificadas no forman parte del predictor. Sexo existe en la fuente y se usa solo en la capa explicativa posterior (sección de prevención); el modelo conserva variables agregadas verificables para reducir sobreajuste y fuga. La representación etaria es agregada; no se infieren características individuales.

### Trazabilidad
Cada cifra proviene de archivos citados en el pie de tabla o en el texto: datos_preparados/municipios_historico_con_calidad.csv, modelado/salidas/metricas.json, evaluacion_adicional.json y perfil_demografico.json. El diccionario de datos y las tablas largas viven en el CSV/XLSX y el repositorio, no en este PDF.

## Página 5: Referencia simple y ajuste regularizado

### Referencia
Predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye por otro tipo electoral. Es interpretable y constituye la exigencia mínima que la complejidad debe superar.

### Ajuste Ridge
Ridge estima el residual respecto de la referencia con diez características agregadas: abstención del mismo tipo, abstención del último proceso, su diferencia, logaritmo de LN, proporción 18-29, proporción 60+ sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo de elección. StandardScaler y Ridge se ajustan solo con entrenamiento anterior a cada corte; alpha=10 se fijó antes de ver métricas; la predicción se trunca a [0,100].

### Flujo simple
Antecedentes observados con calidad verificada → Referencia del mismo tipo → Ajuste Ridge del residual → Estimación 2027 → Semáforo relativo, confianza y decisión con capacidad.

## Página 6: Construcción, cortes y regla de selección

### Cortes temporales
Para evaluar 2021 se entrena con etiquetas 2015 y 2018; para 2024, con 2015, 2018 y 2021. La proyección 2027 incorpora 2015, 2018, 2021 y 2024. Cada ejemplo usa características anteriores a su año objetivo. Hay seis procesos y solo tres intermedias: el volumen de registros no crea más ocasiones electorales.

### Regla de selección
Fijada para 2021: adoptar Ridge solo si mejora el MAE al menos 1% y no empeora el MAE ponderado ni la precisión top50. Ridge cumple esa regla en 2021. El corte 2024 se conserva como comprobación y no se usó para reajustar alpha ni para ocultar el deterioro.

### 2021 es selección, no prueba
2021 se usó para elegir; no es una prueba independiente posterior a la selección. Los análisis posteriores (rango, tamaño, estabilidad) tampoco reajustan el modelo: describen su comportamiento con parámetros congelados.

## Página 7: La mejora no se transfiere de forma consistente

### Tabla de resultados
TABLE_METRICS

### Lectura honesta
En 2021 el MAE baja aproximadamente 23.9% y top50 pasa de 16 a 19 coincidencias; eso deja 31 municipios del top observado fuera de la lista Ridge. En 2024 el MAE sube aproximadamente 52.2%, el ponderado empeora y ambos métodos recuperan 27/50. No hay ganador universal: Ridge se conserva como alternativa exploratoria con la referencia visible.

### Métricas posteriores congeladas
Se definieron después del experimento original y antes de calcularlas: Spearman; precisión y recobrado del tercio alto con umbral aprendido en entrenamiento y congelado por corte; error P90 por tamaño municipal. En 2024 la precisión roja alta de Ridge convive con recobrado bajo: identifica pocos altos y no corrige su deterioro en MAE. Fuente: modelado/salidas/evaluacion_adicional.json.

## Página 8: Estabilidad, incertidumbre y límites

### Estabilidad del top N
Se combinan dos métodos × umbrales NS 5/10/20 para seis variantes. En seis de seis, un municipio forma parte del núcleo robusto; entre una y cinco, de la zona de revisión; cero, queda fuera. La frecuencia es descriptiva, no probabilidad calibrada. Fuente: modelado/salidas/metricas.json.

### Incertidumbre de prioridad, no de intervalo
La interfaz responde «si solo puedo intervenir N municipios, ¿puedo confiar en que este esté entre ellos?» comunicando esa frecuencia y el acuerdo de puesto entre referencia y Ridge. El rango ±21.05 pp (P90 retrospectivo de Ridge 2021, truncado a [0,100]) se conserva solo como error histórico, no como intervalo prospectivo.

### Error por tamaño y límites
El P90 del error por denominador observable previo (<10 mil, 10-100 mil, ≥100 mil) describe heterogeneidad por escala, no un intervalo para 2027. Límites: seis ocasiones electorales y tres intermedias; 2024 es presidencial y no valida 2027; sin causalidad; selección por calidad que puede excluir zonas con necesidad alta.

## Página 9: Clasificación territorial y confianza

### Tercios relativos
Bajo, medio y alto son tercios de las estimaciones nacionales válidas. Alto es el tercio superior de tasas estimadas; no es probabilidad calibrada de deterioro. Gris significa información insuficiente para estimar, se muestra con motivo de exclusión y nunca recibe riesgo cero.

### Eje de confianza
La calidad (NS), la estabilidad entre seis variantes y el acuerdo entre métodos se informan como dimensión separada del color, en la lista y en la ficha. Los umbrales base permanecen fijos al comparar escenarios para que el color no se redefina entre ellos.

### Sensibilidad de umbrales
Mover el corte cambia el número de municipios por nivel; el informe incluye variación por tamaño municipal y por umbral NS. Ejemplo: alternar el filtro de catálogo constante pasa de 1,144 a 1,783 estimaciones. Fuente: modelado/salidas/metricas.json.

(FIGURE_MAP_STATES)

## Página 10: Sin intervención y con intervención hipotética

### Fórmulas del escenario
O = SV2024 + NV2024 por municipio. Alcance efectivo E = mínimo(alcance supuesto, O). Participación adicional hipotética H = E × tasa/100 × respuesta/100. Tasa del escenario = tasa − 100 × H / O. La agregación se pondera por O sobre los mismos municipios seleccionados.

### Supuestos explícitos
Las personas alcanzadas presentan la tasa estimada; la respuesta es hipótesis del usuario; O es referencia histórica observable, no electorado de 2027. NS queda fuera del escenario. Respuesta cero conserva la base; entradas inválidas bloquean la exportación.

(FIGURE_TRIPLE)

### Escenario invertido y ejemplo
Para bajar de nivel, H = O × (tasa − umbral)/100 con tasa > umbral, y el alcance requerido = H / (tasa × respuesta). Si excede O o el alcance, el objetivo es inviable. Ejemplo trabajado con capacidad de 50 municipios: el efecto local por municipio es visible, mientras el efecto agregado es pequeño.

## Página 11: Tipologías observables y línea de acción

### Tipologías por perfil observable
Se derivan tipologías de información agregada, no de personas: territorio con menor proporción urbana; proporción joven 18-29 ≥25%; proporción 60+ ≥25%; y calidad insuficiente (NS alto o antecedentes incompletos). Cada tipología lleva una línea de acción: información electoral accesible, talleres en espacios educativos y comunitarios, material legible, o revisión de datos antes de priorizar.

### El perfil no decide, explica
La prioridad la fija el modelo; la tipología orienta a quién podría dirigirse una intervención. El perfil CCPC por edad, sexo y tipo de sección es una capa explicativa posterior que nunca alimenta al modelo y no implica causalidad; los grupos con muestra insuficiente se marcan como tales. Fuente: modelado/salidas/perfil_demografico.json.

### Mecanismo como hipótesis
La reducción de barreras informativas podría favorecer la participación; es una hipótesis a evaluar, no un hallazgo del modelo.

## Página 12: Ficha tipo y ejemplo completo

### Ficha tipo
Cada recomendación registra: condición observable, acción, responsable propuesto, cobertura, condiciones de aplicación, recurso (personas y horas), medición y mecanismo hipotético.

### Ejemplo completo
Municipio con proporción joven ≥25% y tasa en el tercio alto con calidad suficiente. Acción: talleres sobre requisitos y procedimiento electoral en espacios educativos y comunitarios. Responsable propuesto: área de educación cívica y enlace local, por validar. Cobertura: población alcanzada registrada; atención voluntaria y abierta. Condiciones: verificar espacios y acceso; no asumir desinterés por edad ni seleccionar por afinidad. Recurso: personas alcanzadas y horas de facilitación, sin costos inventados. Medición: alcance y cambio de conocimiento agregado. Hipótesis: brecha informativa; el modelo no demuestra el mecanismo.

### El resto, en el CSV
La ficha completa de cada municipio seleccionado se exporta en el plan CSV; este PDF incluye un ejemplo representativo.

## Página 13: Priorización de recursos y diseño de evaluación

### Priorización de recursos
El plan ordena por capacidad, con el criterio elegido y la confianza mínima declarada. Comunica núcleo robusto y zona de revisión para no tratar la frontera como certeza. En modo de capacidad humana, el presupuesto se expresa en personas alcanzables y se agota por prioridad.

### Diseño de evaluación propuesto
Aleatorizar atención inmediata o diferida entre municipios cercanos al corte de capacidad, con balance por entidad, tamaño, calidad y contexto; indicadores de cobertura y comprensión; y regla de análisis fijada antes de observar resultados. La cercanía del score no acredita equivalencia ni causalidad.

### Vista operativa
El resumen por entidad apoya la distribución regional con la cobertura de municipios estimables y excluidos. No se inventa correspondencia distrital: la base no la contiene y no se certifica.

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
Abrir el mapa con doble clic en demo/index.html (o servidor local); regenerar cifras con modelado/imprimir_cifras.py; el código, la demo y los insumos están en el repositorio y el paquete. La revisión visual comprueba estas 14 páginas. Umbral convierte la incertidumbre del modelo en diseño institucional: prioriza, muestra por qué y qué tan robusta es cada decisión, y propone cómo evaluar una acción. Se invita a pilotear alrededor del corte de capacidad antes de ampliar.

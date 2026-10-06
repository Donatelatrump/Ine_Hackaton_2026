# Umbral: reporte metodológico y preventivo
Versión técnica para revisión | 6 de octubre de 2026
Estructura de 14 páginas (8 secciones)

## Página 1: Resumen ejecutivo

### Reporte metodológico y preventivo · Reto 2
Tecnocalidos. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Versión técnica para revisión, 6 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios 2009-2024. Presupuesto de 15 páginas; este documento usa 14.

### Resumen ejecutivo
Umbral permite distribuir una cobertura total de personas en municipio, estado o país mediante prioridad o reparto proporcional. Compara una referencia sencilla (última elección del mismo tipo) con Ridge regularizado, con calidad visible y análisis congelados. Ridge mejora en 2021 y empeora en 2024: no se declara ganador. Los escenarios usan efectos publicados de SMS o llamada, como transferencia hipotética no validada a México, o respuesta personalizada sin respaldo causal. La comparación incluye todos los estimables filtrados. Propone fichas revisables y un piloto con protocolo previo; el uso es deliberación institucional.

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
Una clave municipal constante no prueba límites ni población constantes. No hay armonización histórica de fronteras y los conteos no se redistribuyeron a los límites de 2024. Se excluyen edades mayores de 120 al construir proporciones etarias, conservando los conteos originales.

## Página 4: Variables usadas, omitidas y trazabilidad

Variables del predictor en modelado/core.py: Abstención del mismo tipo, Abstención del último proceso, Diferencia último − mismo tipo, log(LN), Proporción 18-29, Proporción 60+ (sin >120), Proporción urbana, NS de ambos antecedentes, Tipo de elección (intermedia).

### Variables omitidas y por qué
Sexo, escolaridad y variables externas no verificadas no forman parte del predictor. Sexo existe en la fuente y se usa solo en la capa explicativa posterior (sección de prevención); el modelo conserva variables agregadas verificables para reducir sobreajuste y fuga. La representación etaria es agregada; no se infieren características individuales.

### Trazabilidad
Cada cifra proviene de archivos citados en el pie de tabla o en el texto: datos_preparados/municipios_historico_con_calidad.csv, modelado/salidas/metricas.json, evaluacion_adicional.json y perfil_demografico.json. El diccionario de datos y las tablas largas viven en la base CSV y el repositorio, no en este PDF.

## Página 5: Referencia simple y ajuste regularizado

### Referencia
Predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye por otro tipo electoral. Es interpretable y constituye la exigencia mínima que la complejidad debe superar.

### Ajuste Ridge
Ridge estima el residual respecto de la referencia con diez características agregadas: abstención del mismo tipo, abstención del último proceso, su diferencia, logaritmo de LN, proporción 18-29, proporción 60+ sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo de elección. StandardScaler y Ridge se ajustan solo con entrenamiento anterior a cada corte; alpha=10 se fijó antes de ver métricas; la predicción se trunca a [0,100].

### Flujo simple
Antecedentes observados con calidad verificada → Referencia del mismo tipo → Ajuste Ridge del residual → Estimación 2027 → Semáforo relativo, estabilidad y decisión con capacidad.

## Página 6: Construcción, cortes y regla de selección

### Cortes temporales
Para evaluar 2021 se entrena con etiquetas 2015 y 2018; para 2024, con 2015, 2018 y 2021. La proyección 2027 incorpora 2015, 2018, 2021 y 2024. Cada ejemplo usa características anteriores a su año objetivo. Hay seis procesos y solo tres intermedias: el volumen de registros no crea más ocasiones electorales.

### Regla de selección
Fijada para 2021: adoptar Ridge solo si mejora el MAE al menos 1% y no empeora el MAE ponderado ni la precisión top50. Ridge cumple esa regla en 2021. El corte 2024 se conserva como comprobación y no se usó para reajustar alpha ni para ocultar el deterioro.

### 2021 es selección, no prueba
2021 se usó para elegir; no es una prueba independiente posterior a la selección. Los análisis posteriores (rango, tamaño, estabilidad) tampoco reajustan el modelo: describen su comportamiento con parámetros congelados.

## Página 7: La mejora no se transfiere de forma consistente

| Corte / método | n | MAE pp | Pond. pp | Top50 |
|---|---|---|---|---|
| 2021 / Referencia | 1490 | 12.116 | 8.052 | 16/50 |
| 2021 / Ridge | 1490 | 9.215 | 5.489 | 19/50 |
| 2024 / Referencia | 1476 | 5.639 | 3.541 | 27/50 |
| 2024 / Ridge | 1476 | 8.585 | 4.491 | 27/50 |

### Lectura honesta
En 2021 el MAE baja aproximadamente 23.9% y top50 pasa de 16 a 19 coincidencias; eso deja 31 municipios del top observado fuera de la lista Ridge. En 2024 el MAE sube aproximadamente 52.2%, el ponderado empeora y ambos métodos recuperan 27/50. No hay ganador universal: Ridge se conserva como alternativa exploratoria con la referencia visible.

### Métricas posteriores congeladas
Se definieron después del experimento original y antes de calcularlas: Spearman; precisión y recobrado del tercio alto con umbral aprendido en entrenamiento y congelado por corte; error P90 por tamaño municipal. En 2024 la precisión roja alta de Ridge convive con recobrado bajo: identifica pocos altos y no corrige su deterioro en MAE. Fuente: modelado/salidas/evaluacion_adicional.json.

## Página 8: Estabilidad, incertidumbre y límites

### Estabilidad del top N
Dos métodos por umbrales NS 5/10/20 generan seis variantes. Seis inclusiones forman núcleo robusto; una a cinco, zona de revisión. La frecuencia describe el ranking de REFERENCIA top50, no una probabilidad ni la asignación municipal actual o proporcional. Las variantes comparten datos y pueden equivocarse juntas. Fuente: demo/decision.js y entrega/caso_municipal.json.

### Incertidumbre de prioridad, no de intervalo
La frecuencia informa acuerdo del ranking de referencia, separado del reparto de personas. El rango ±21.05 pp (P90 retrospectivo de Ridge 2021, truncado a [0,100]) es error histórico, no intervalo prospectivo. Los intervalos SMS pertenecen a estudios externos y no cubren incertidumbre de transferencia a México.

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
En ranking nacional de referencia top50, catálogo constante y tasa, Ridge ocupa puesto 1 y referencia 3. Estimación 62.106806%; antecedente 2021: 66.30%; NS 2021/2024: 9.60%/2.28%. Estabilidad 4/6, elegible 4/6, zona de revisión: no es la asignación municipal actual. Ámbito municipio, cobertura TOTAL 1,000, SMS Suecia ITT 0.30 pp [0.13,0.48], O=255,362: H=3 votos hipotéticos [1.3,4.8]; posterior 62.105631%, reducción 0.001175 pp. Responsable propuesto: educación cívica y junta local, por validar; verificar contactos y capacidad. Registrar asignación, entrega y resultados conforme al protocolo. Transferencia a México no validada. Fuente: entrega/caso_municipal.json.

### El resto, en el CSV
La ficha completa de cada municipio seleccionado se exporta en el plan CSV; este PDF incluye un ejemplo representativo.

## Página 13: Priorización de recursos y diseño de evaluación

### Priorización de recursos
Cobertura total limitada a población observable elegible. Prioridad concentra cupo siguiendo ranking hasta agotarlo. Proporcional distribuye según SV+NV2024 entre todos los elegibles, redondeo por mayor resto y desempate determinista. Son decisiones del proyecto, no reglas de la literatura. Con coeficiente homogéneo y sin activar el límite de abstenciones, igual cobertura produce igual H total: cambia dónde se asigna, no necesariamente el impacto agregado. Estabilidad de referencia separada del reparto actual.

### Diseño de evaluación propuesto
Aleatorizar atención inmediata o diferida entre municipios cercanos al corte de capacidad, con balance por entidad, tamaño, calidad y contexto; indicadores de cobertura y comprensión; y regla de análisis fijada antes de observar resultados. La cercanía del score no acredita equivalencia ni causalidad.

### Vista operativa
Comparación municipal, estatal o nacional sobre TODOS los estimables filtrados, atendidos y no atendidos; exclusiones y motivos visibles. No representa todo el electorado nacional ni armoniza límites. Sin correspondencia distrital certificada.

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

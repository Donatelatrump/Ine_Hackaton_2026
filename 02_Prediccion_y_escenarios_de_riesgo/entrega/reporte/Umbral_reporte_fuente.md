# Umbral: reporte metodológico y preventivo
Versión técnica para revisión | 5 de octubre de 2026

## Página 1: Una decisión municipal revisable

### Reporte metodológico y preventivo | Track 2
Versión técnica para revisión, 5 de octubre de 2026. Horizonte exploratorio: elección intermedia de 2027. Cobertura: México por municipio, claves INE. Datos históricos ordinarios: 2009-2024. La propuesta combina una referencia sencilla, un modelo regularizado, calidad de datos visible y escenarios sujetos a capacidad.

### La decisión que organiza el atlas
Si un área de educación cívica dispone de capacidad para atender N municipios, Umbral permite revisar cuáles aparecen primero, qué antecedentes sustentan su posición y qué alcance y respuesta serían necesarios bajo una hipótesis de intervención. La lista es un insumo para deliberación institucional; la prioridad automática no sustituye diagnóstico local.

### Hallazgo central
Ridge reduce el error en el corte 2021, utilizado para selección, y empeora frente a persistencia en 2024. El resultado adverso forma parte de la evidencia. La utilidad defendible está en hacer revisable la decisión territorial, mostrar su sensibilidad y registrar supuestos, sin prometer superioridad predictiva consistente ni impacto causal.

### Ruta de lectura
Páginas 2-3: fuentes, calidad y unidad de análisis. Páginas 4-6: modelo, resultados y análisis posteriores. Páginas 7-8: semáforo, estabilidad y escenario. Páginas 9-10: acciones preventivas y piloto. Páginas 11-12: operación, límites y reproducibilidad.

### Equipo y estado de la propuesta
Tecnocalidos. Integrantes: Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum. Este documento desarrolla el reporte de 10-15 cuartillas solicitado para el reto 2. Los formatos de cartas no equivalen a firmas; registro y envío oficial no están acreditados en este trabajo. El paquete técnico requiere revisión humana antes de su presentación formal.

## Página 2: Priorizar exige definir el objetivo

### Alineación con el reto
La convocatoria pide un modelo simple de riesgo con antecedentes y variables sociodemográficas, escenarios sin intervención y con intervención hipotética, clasificación territorial comprensible y recomendaciones preventivas. El reporte y el mapa ejecutable con base anonimizada son entregables específicos. Estas exigencias se verificaron en las páginas 3-5 del PDF oficial [1].

### Tres preguntas distintas
La tasa estimada identifica territorios con mayor proporción de abstención. El volumen estimado aproxima cuántas abstenciones corresponderían a esa tasa sobre la población observable de referencia. El deterioro compara la estimación con la última elección del mismo tipo. Una localidad pequeña con tasa alta puede no encabezar el volumen; ninguna lista es neutral respecto al objetivo.

### Unidad y horizonte
La unidad es municipio-año identificado por clave INE, preservada como texto. Para 2027 se toma 2021 como último antecedente del mismo tipo y 2024 como último proceso disponible. La proyección es exploratoria y municipal: no permite afirmar comportamientos individuales ni producir una asignación distrital que la base no contiene.

### Capacidad como restricción explícita
N expresa municipios revisables o atendibles, no presupuesto monetario. El ejemplo inicial de 50 municipios es una decisión del prototipo y puede cambiar. Cada ejecución debe registrar método, umbral NS, filtro territorial, objetivo de prioridad, capacidad, alcance y respuesta; cambiar esos valores altera la decisión y exige volver a revisarla.

### Resultado institucional esperado
El producto propone una mesa de revisión: evidencia histórica, calidad, posiciones bajo alternativas, acción propuesta y factibilidad. La institución debe confirmar responsables, recursos y pertinencia territorial. No se atribuye respaldo institucional a las recomendaciones ni se asegura que su implementación aumente la participación.

## Página 3: De conteos a una base comparable

### Serie histórica y trazabilidad
La serie principal procede de los Conteos Censales de Participación Ciudadana del INE [2], para seis elecciones ordinarias: 2009, 2012, 2015, 2018, 2021 y 2024. Los insumos de prisión preventiva y voto anticipado se conservan separados y no se incorporan automáticamente al histórico municipal ordinario.

### Auditoría realizada
El procesamiento principal comprende 54,872,712 filas de 192 CSV y genera 14,779 registros municipio-año y 2,477 claves históricas. Se revisaron integridad CRC, duplicados y reconciliación de conteos. Estas comprobaciones sustentan consistencia de archivos y sumas; no resuelven cambios de límites ni equivalencia de población a lo largo del tiempo.

### Definiciones que evitan confundir desconocimiento con abstención
SV cuenta participación registrada; NV cuenta no participación; NS indica participación no especificada. LN = SV + NV + NS. La abstención observable es 100 × NV / (SV + NV), cuando el denominador es positivo. NS (%) = 100 × NS / LN. Se suman conteos antes de calcular tasas, evitando promediar porcentajes de grupos con tamaños distintos.

### Calidad y exclusión
La regla principal exige NS ≤10% y tasas observables en los antecedentes más reciente y del mismo tipo. La evaluación exige también calidad del objetivo histórico. En 2027 hay 1,783 estimaciones y 694 municipios sin estimación, sobre 2,477 claves. El estado sin datos se muestra gris y con motivo de exclusión; no recibe riesgo cero.

### Cartografía y sociodemografía
Los polígonos INE sirven de referencia visual de mayo de 2024 [3]. Catálogo de claves constante y límites constantes son propiedades distintas: falta armonización histórica. Se excluyen edades superiores a 120 al construir proporciones etarias, conservando conteos originales. Sexo, escolaridad y variables externas no verificadas no forman parte del predictor actual.

## Página 4: Referencia simple y ajuste regularizado

### Persistencia del mismo tipo
La referencia predice la abstención de la última elección del mismo tipo: 2015 para 2021, 2018 para 2024 y 2021 para 2027. Si no existe antecedente válido, no se sustituye silenciosamente por otro tipo electoral. Esta referencia es interpretable y constituye una exigencia mínima para valorar la complejidad adicional.

### Diez características agregadas
Se usan abstención del mismo tipo, abstención del último proceso, su diferencia, logaritmo de LN, proporción de 18-29 años, proporción de 60 años y más sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo electoral. LN conserva su papel de característica histórica; su uso como predictor no cambia el denominador observable de tasas, escenarios y ponderación del error.

### Construcción del candidato
StandardScaler y Ridge estiman el residual respecto de persistencia. La predicción suma referencia y residual y se trunca a [0,100]. Alpha=10 permanece congelado. Cada ejemplo utiliza características anteriores al objetivo y el escalador se ajusta con entrenamiento. Las contribuciones del modelo son algebraicas, no causas individuales o efectos de una política.

### Cortes temporales
Para evaluar 2021 se entrena con etiquetas 2015 y 2018; para 2024, con 2015, 2018 y 2021. La proyección 2027 incorpora etiquetas 2015, 2018, 2021 y 2024. El volumen de registros no crea más ocasiones electorales: hay seis procesos y solo tres intermedias, una limitación de transferencia temporal.

### Selección congelada
La regla fijada para 2021 exige al menos 1% de mejora en MAE y ausencia de empeoramiento del MAE ponderado y precisión top50. Ridge cumple esa regla. 2021 es selección, no prueba independiente posterior a selección. Los nuevos análisis no se utilizan para reajustar alpha, cambiar retrospectivamente la regla o ocultar 2024.

## Página 5: La mejora no se transfiere de forma consistente

### Comparación temporal
La tabla usa las mismas cohortes para ambos métodos dentro de cada corte. MAE es error absoluto medio en puntos porcentuales. MAE ponderado utiliza SV+NV del objetivo histórico, corrigiendo referencias narrativas previas a LN. Top50 cuenta coincidencias entre los 50 valores predichos más altos y los 50 observados más altos dentro de la cohorte evaluable.

| Corte / método | n | MAE pp | Ponderado pp | Top50 |
|---|---:|---:|---:|---:|
| 2021 / Referencia | 1490 | 12.116 | 8.052 | 16/50 |
| 2021 / Ridge | 1490 | 9.215 | 5.489 | 19/50 |
| 2024 / Referencia | 1476 | 5.639 | 3.541 | 27/50 |
| 2024 / Ridge | 1476 | 8.585 | 4.491 | 27/50 |

### Lectura del resultado
En 2021 el MAE baja aproximadamente 23.9% y top50 pasa de 16 a 19 coincidencias. Eso deja 31 municipios del top observado fuera de la lista Ridge. En 2024 el MAE sube aproximadamente 52.2%, el ponderado empeora y ambos métodos recuperan 27/50. La coincidencia del ranking no compensa automáticamente el deterioro en tasas.

### Qué sostiene esta evidencia
Ridge puede conservarse como alternativa exploratoria conforme a la selección original, con persistencia visible. No hay evidencia de ganador universal. 2024 es presidencial y no valida directamente una elección intermedia de 2027. El desempeño es condicional a municipios con antecedentes y objetivos de calidad suficiente, no al universo nacional.

### Comparar sin cambiar la pregunta
Las métricas responden preguntas complementarias: precisión de tasas, error sobre población observable y recuperación de prioridades. Una mejora en una no acredita mejora en todas. No se transforma el error retrospectivo en probabilidad de abstención futura; tampoco se usan los resultados para inferir eficacia de una intervención.

## Página 6: Orden, tercio alto y tamaño municipal

### Un análisis posterior identificado
Las ampliaciones se definen después del experimento original y antes de calcularlas. Describen utilidad operativa y heterogeneidad del error, con modelo, alpha y selección congelados. No son una prueba independiente del diseño inicial.

### Ordenamiento: Spearman
Correlación entre rangos observados y predichos, con rangos promedio en empates. Resume concordancia global de orden. Puede coexistir con fallos en los primeros N; se conserva top50 y revisión de listas específicas.

### Tercio alto con umbral aprendido
El percentil 2/3 se aprende con etiquetas de entrenamiento y se congela para evaluar ambos métodos. Precisión: fracción de clasificados altos realmente altos. Recobrado: fracción de altos observados recuperada. Umbrales: 47.814% en 2021 y 47.726% en 2024; no se redefine el umbral con el objetivo de prueba.

### Error por tamaño
Percentil 90 del error absoluto por denominador observable previo: <10 mil, 10 mil a <100 mil y ≥100 mil. Cada banda informa n. Describe heterogeneidad por escala; no es intervalo calibrado para 2027.

### Resultados complementarios
2021 persistencia: Spearman 0.485; precisión alta 46.8%; recobrado 81.5%.
2021 ridge: Spearman 0.599; precisión alta 54.9%; recobrado 73.7%.
2024 persistencia: Spearman 0.827; precisión alta 88.5%; recobrado 37.9%.
2024 ridge: Spearman 0.811; precisión alta 98.2%; recobrado 20.5%.
P90 de error Ridge por tamaño (<10 mil / 10-100 mil / ≥100 mil):
2021: 23.68 pp (n=766) / 18.53 pp (n=608) / 8.12 pp (n=116).
2024: 18.08 pp (n=732) / 14.05 pp (n=622) / 6.74 pp (n=122).
En 2024 la alta precisión de Ridge se acompaña de bajo recobrado: identifica pocos altos. No corrige su deterioro en MAE.

### Lectura conjunta
NS 5, 10 y 20 alteran las cohortes: no comparan idénticas muestras. La exclusión por calidad exige diagnóstico de datos. Estas métricas no autorizan asignación definitiva de recursos.

## Página 7: Nivel relativo y estabilidad de la selección

### Clasificación interpretable
Bajo, medio y alto corresponden a tercios relativos de estimaciones nacionales válidas. Alto identifica el tercio superior de tasas estimadas; no significa una probabilidad calibrada de deterioro. Gris significa que la información no permite estimación. Los umbrales base se mantienen fijos al comparar Base, Con intervención y cambio, para que el color no se redefina entre escenarios.

### Seis variantes, una frecuencia descriptiva
Se combinan persistencia y Ridge con límites NS de 5, 10 y 20%. Los entrenamientos siguen el procedimiento original. Para el N, filtro y criterio activos se cuenta cuántas veces cada municipio entra en la selección entre las seis variantes. Una variante no elegible cuenta como no seleccionada; la elegibilidad se informa por separado.

### Cómo usar la estabilidad
Entrar en seis de seis variantes define un núcleo robusto respecto a esas alternativas, no a todos los modelos posibles. Tres de seis indica dependencia de decisiones metodológicas. Cero de seis puede reflejar calidad insuficiente y no necesariamente baja tasa. La frecuencia no es probabilidad, confianza calibrada ni garantía de permanecer prioritario en 2027.

### Incertidumbre de prioridad, no de intervalo
La interfaz responde a la pregunta operativa «si solo puedo intervenir N municipios, ¿puedo confiar en que este esté entre ellos?». Para ello comunica la frecuencia con que un municipio entra en la selección entre las seis variantes (dos métodos × NS 5/10/20) y el acuerdo de puesto entre referencia y Ridge. No es probabilidad calibrada. El rango histórico ±21.05 pp (p90 retrospectivo de Ridge 2021, truncado a [0,100]) se conserva solo en una nota técnica colapsada: es error histórico, no intervalo prospectivo. El catálogo territorial es un indicador separado: no acredita límites históricos equivalentes.

### Revisión de lentes
Tasa, volumen estimado sobre observados y deterioro respecto del último proceso del mismo tipo responden objetivos distintos. La concordancia entre listas ayuda a detectar municipios sensibles al criterio. La revisión debe registrar qué objetivo se eligió y por qué: una lista estable bajo tasa puede cambiar al priorizar volumen o deterioro.

## Página 8: Población observable y supuestos explícitos

### Base corregida
Para cada municipio O = SV2024 + NV2024. O limita cobertura, es el denominador de la reducción de tasa y pondera la agregación. NS se informa aparte y no se incluye como población alcanzable dentro de esta simulación. O es una referencia histórica observable; no es población proyectada de 2027. Nuevos datos deben aportar O, sin reemplazo silencioso por LN.

### Fórmula operativa
Sea a la tasa estimada (%), A el alcance supuesto y r la respuesta supuesta (%). Alcance efectivo E = mínimo(A,O). Participación adicional hipotética H = E × a/100 × r/100. Tasa con intervención = a - 100 × H/O. La tasa agregada se pondera por O sobre los mismos municipios seleccionados. Respuesta cero conserva la base.

### Ejemplo hipotético, no resultado medido
Si O=20,000, a=60%, A=1,000 y r=10%, E=1,000 y H=60 personas hipotéticas. La tasa sería 59.7%, una reducción de 0.3 pp. El ejemplo solo explica unidades y fórmula; no es un municipio real ni una estimación causal. El mecanismo supone que las personas alcanzadas presentan la tasa base y que la respuesta convierte una fracción de abstenciones.

### Inversión para evaluar factibilidad
Para bajar a un umbral t, se requiere H = O × (a-t)/100 cuando a>t. Con r positivo y a positivo, E requerido = O × (a-t)/(a × r/100). Si excede O o el alcance disponible, el objetivo es inviable bajo esos límites. Respuesta cero, denominador ausente o capacidad nula se tratan explícitamente, evitando divisiones inválidas.

### Comparación y recursos
Base, Con intervención y cambio permiten inspeccionar el mismo conjunto y umbrales. Personas alcanzadas son una unidad de recurso, no costo monetario ni electores adicionales garantizados. El plan exportado debe registrar supuestos y factibilidad. El escenario no estima efectos causales, movilización individual ni cambios en el tamaño del electorado.

### Capacidad territorial o humana
El Modo Director admite dos restricciones equivalentes: municipios o personas alcanzables. En modo humano, la selección añade municipios por prioridad hasta agotar el presupuesto, con alcance limitado por la base observable. La ficha «¿Por qué este municipio?» explica posición, confianza, razones y robustez; el perfil CCPC es capa explicativa posterior; y la frontera de decisión separa núcleo robusto, zona de revisión y fuera.

## Página 9: Fichas ligadas a condiciones observables

### Ficha A | Persistencia alta
Condición: tasa histórica y prioridad actual altas con datos válidos. Acción: sesiones neutrales de información sobre el proceso y rutas institucionales de consulta. Responsable propuesto: área de educación cívica y enlace local, sujetos a confirmación. Cobertura: municipios seleccionados y alcance aprobado. Recurso: personas alcanzadas, sesiones y horas de facilitación. Medición: comprensión antes/después y asistencia agregada. Hipótesis: reducir barreras informativas podría favorecer participación; el modelo no demuestra ese mecanismo.

### Ficha B | Deterioro respecto al mismo tipo
Condición: estimación mayor que el antecedente comparable y señal persistente al variar método. Acción: diagnóstico local previo y revisión de información accesible sobre fechas, ubicación y procedimientos. Responsable propuesto: coordinación territorial y educación cívica. Cobertura: conjunto elegible por deterioro, con alcance limitado por O. Recurso: consultas atendidas y personas informadas. Medición: consultas resueltas, comprensión y participación agregada futura. Hipótesis: una brecha informativa explica parte del deterioro; debe comprobarse antes de ampliar.

### Ficha C | Barreras de acceso por verificar
Condición: composición agregada rural o etaria relevante, sin inferir características de cada habitante. Acción: probar formatos accesibles y puntos presenciales de información tras consulta local. Responsable propuesto: enlace local y equipo de accesibilidad. Cobertura: puntos confirmados y alcance medible. Recurso: personas atendidas, materiales y horas. Medición: acceso, comprensión y satisfacción agregada. Hipótesis: adecuar el formato mejora alcance; no atribuir abstención a edad o ruralidad como causas.

### Ficha D | Información insuficiente
Condición: NS alto, historial incompleto o duda territorial. Acción: revisar fuente, clave y agregación antes de priorizar una intervención. Responsable propuesto: equipo de datos con enlace territorial. Cobertura: municipios excluidos y discrepancias detectadas. Recurso: registros revisados y horas de validación. Medición: casos resueltos, cobertura recuperada y motivos documentados. Hipótesis: mejor información reduce decisiones erróneas; no se interpreta gris como baja necesidad.

### Asignación y registro
Las fichas son propuestas de trabajo, no programas aprobados. Cada responsable debe validar pertinencia, lenguaje neutral, cobertura real y recursos disponibles. El registro operativo une condición, acción, encargado confirmado, calendario, alcance y medición. La respuesta del simulador se etiqueta como hipótesis, sin convertirla en compromiso de resultados.

## Página 10: Aprender antes de ampliar una intervención

### Población y acuerdo previo
Se propone un piloto entre municipios elegibles alrededor del corte de capacidad, definido antes de asignar acciones. La cercanía del score no acredita equivalencia entre territorios ni causalidad. Se requiere acuerdo institucional previo y, cuando corresponda, consentimiento de participantes antes de aleatorizar. Ninguna actividad individual se desprende automáticamente de los datos agregados.

### Asignación aleatoria y balance
Dentro del conjunto acordado, asignar intervención y comparación mediante sorteo reproducible. Usar bloques o estratos definidos previamente por entidad, tamaño observable, tasa histórica y calidad; comprobar balance y reportar desequilibrios. Establecer criterios de inclusión, tamaño factible, calendario y regla de análisis antes de observar resultados. No seleccionar comparadores porque produzcan un efecto favorable.

### Resultado primario y proceso
Definir una medida primaria de comprensión o alcance efectivo para un piloto corto; la participación agregada futura exige un proceso electoral y comparabilidad territorial. Registrar implementación, personas alcanzadas, intensidad y eventos externos. Mantener costos de operación como medición futura, sin inventar cifras. Si la asignación es municipal, las unidades de inferencia deben respetar esa agrupación.

### Interpretación causal limitada
Una diferencia entre escenarios calculados no es impacto. Un piloto aleatorio bien ejecutado permitiría estimar el efecto de ofrecer la acción en su conjunto elegible, con incertidumbre y posibles problemas de contaminación o incumplimiento. Analizar por asignación original y describir desvíos. El resultado no se generaliza automáticamente a municipios excluidos, otros años o acciones distintas.

### Condiciones de pausa y ampliación
Pausar ante barreras de acceso, implementación insuficiente, reclamos o datos no comparables. Ampliar solo tras revisar ejecución, balance, efecto e incertidumbre y capacidad institucional. La medición puede concluir que la intervención no funciona. El piloto busca aprender y ajustar operación; no garantiza una reducción de abstención ni transforma el score en diagnóstico causal.

## Página 11: Una revisión territorial con evidencia visible

### Flujo propuesto
Primero definir objetivo, capacidad y territorio. Después revisar calidad y catálogo, comparar persistencia y Ridge, inspeccionar estabilidad bajo seis variantes y confirmar los municipios con conocimiento local. Finalmente seleccionar fichas, registrar responsables y recursos, formular escenario y exportar el plan. La decisión institucional debe conservar una justificación para aceptar o desplazar prioridades.

### Vista por entidad
La revisión por entidad permite distribuir atención y leer cobertura de municipios estimables y excluidos. No se inventa correspondencia distrital ausente. Las claves constituyen la unión territorial; nombres sirven para lectura y requieren revisión cuando cambian. Un catálogo constante es una señal conservadora y no una certificación de comparabilidad de límites.

### Límites que afectan uso
La proyección tiene escasa profundidad temporal, resultado adverso en 2024 y selección por calidad que puede excluir zonas con necesidades altas. El agregado municipal oculta heterogeneidad interna. La intervención usa una respuesta no estimada y población observable histórica. Estas limitaciones deben acompañar el plan, incluso si una lista es estable bajo las seis variantes.

### Qué verifican las pruebas
Los controles de software pueden verificar fórmulas, filtros, respuesta cero, estado gris, denominador obligatorio, frecuencia y exportación consistente. No prueban precisión futura, límites históricos armonizados o eficacia preventiva. El mapa local debe abrirse sin depender de servicios remotos y conservar datos incrustados para la revisión del jurado.

### Responsabilidad y seguimiento
El área usuaria confirma responsables y alcance; el equipo técnico conserva versión de insumos, parámetros y plan exportado. Se recomienda revisar incidencias, cambios territoriales y fuentes antes de cada uso. No se utiliza información personal ni se prescribe persuasión partidista. La finalidad es educación cívica neutral y planeación revisable con información agregada.

### Modo Director y frontera de decisión
El Modo Director fija capacidad (territorial o humana), criterio y confianza mínima, y resume el plan. La frontera de decisión separa el núcleo robusto (6/6 variantes), la zona de revisión (1/6–5/6) y los que quedan fuera; sobre la frontera se propone un piloto aleatorio.

## Página 12: Fuentes, archivos y cierre administrativo

### Evidencia local para revisar cifras
modelado/salidas/metricas.json conserva métricas y metadatos; backtest_predicciones.csv permite reconstruir errores y rankings; evaluacion_adicional.json documenta análisis posteriores cuando está disponible. La base municipios_historico_con_calidad.csv sustenta conteos. ejecutar.py fija cortes, referencia y Ridge; el código de ampliación conserva la separación entre experimento original y análisis posteriores.

### Regeneración del documento
Ejecutar python entrega/reporte/generar_reporte.py desde el directorio del track o mediante ruta completa. Requiere reportlab, pymupdf y pypdf; instalar en entrega/reporte/.packages con pip --target si faltan. El script lee métricas, produce este PDF, fuente Markdown y renders, y verifica 12 páginas, texto extraíble y límites geométricos. La revisión visual sigue siendo necesaria.

### Referencias oficiales
[1] INE, Convocatoria Hackea la participación, 2026. Página 3: reto 2; página 4: reporte de 10-15 cuartillas, mapa y entregables generales; página 5: envío y evaluación. https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf
[2] INE, Conteos Censales de Participación Ciudadana 2009-2024. https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/
[3] INE, mapas y cartografía consultados como referencia visual. https://pautas.ine.mx/transparencia/mapas/index_2025.html

### Entrega técnica y requisitos humanos
La convocatoria requiere presentación de máximo 10 diapositivas, código o repositorio cuando corresponda y cartas firmadas por todas las personas integrantes. El ZIP debe identificarse por equipo y eje. Este reporte no acredita registro, firmas, elegibilidad de integrantes o envío. Esos actos requieren a las personas participantes; la versión técnica no se presenta como entrega final certificada.

### Criterio de uso responsable
La evidencia disponible permite explorar prioridades y documentar decisiones. Una adopción institucional exige revisión territorial, contraste de calidad y un piloto evaluable. Mantener la referencia sencilla, el deterioro de 2024 y las hipótesis visibles es parte del método, no una nota secundaria. El resultado puede cambiar con nuevas fuentes y futuras elecciones.

# Track 2: revisión vigente de Umbral

Actualización: 6 de octubre de 2026. Equipo: Tecnocalidos.

## Decisión y alcance

Umbral permite priorizar una revisión territorial con antecedentes observables, restricciones de capacidad y supuestos visibles. La persona usuaria define territorio, cobertura total de personas, distribución por prioridad o proporcional a SV+NV 2024, criterio de tasa/volumen/deterioro y estabilidad mínima. Inspecciona cada ficha y exporta un plan para revisión humana.

El horizonte 2027 es exploratorio. La herramienta no está validada para asignar recursos automáticamente ni demuestra la efectividad de las intervenciones. El recorrido de presentación es: definir capacidad, revisar un municipio y comparar un escenario.

## Datos y denominadores

Seis elecciones ordinarias 2009–2024; 54,872,712 filas auditadas de 192 CSV; 14,779 registros municipio-año. Fuentes agregadas CCPC, sin identidades personales. Voto anticipado y prisión preventiva se conservan aparte.

```text
LN = SV + NV + NS
Abstención observada (%) = 100 × NV / (SV + NV)
NS (%) = 100 × NS / LN
```

La regla principal exige NS ≤10% en el último antecedente y el del mismo tipo. Para evaluar, también exige objetivo observable con NS ≤10%. Hay 1,783 estimaciones y 694 municipios sin estimación sobre 2,477 claves. El filtro opcional de entidades con catálogo constante deja 1,144 estimaciones; no acredita límites constantes. La cartografía 2024 es referencia visual, sin armonización histórica.

LN sigue siendo una variable de tamaño del predictor y denominador de NS y composición. **SV+NV del objetivo histórico pondera el MAE. SV+NV 2024 limita alcance, calcula la reducción y pondera el escenario.** NS queda fuera de ese escenario; no se proyecta el electorado de 2027.

## Modelo y evidencia

Referencia: última elección del mismo tipo. Ridge ajusta un residual con diez variables históricas agregadas; StandardScaler y Ridge aprenden solo del entrenamiento previo a cada corte. Alpha=10 y la selección original permanecen congelados.

| Corte | Método | Municipios | MAE (pp) | MAE ponderado (pp) | Aciertos top50 |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia | 1,490 | 12.12 | 8.05 | 16/50 |
| 2021 | Ridge | 1,490 | 9.21 | 5.49 | 19/50 |
| 2024 | Referencia | 1,476 | 5.64 | 3.54 | 27/50 |
| 2024 | Ridge | 1,476 | 8.58 | 4.49 | 27/50 |

Ridge mejora aproximadamente 23.9% en 2021 y empeora 52.2% en 2024. No muestra superioridad consistente. 2021 fue selección, no prueba independiente posterior; 2024 es presidencial y no valida directamente 2027. Millones de filas no compensan seis ocasiones electorales y tres intermedias. Las métricas adicionales son análisis posteriores, no nueva validación independiente.

El top50 se compara dentro de cada cohorte evaluable. La exclusión por calidad puede apartar territorios con necesidad alta; falta validar representatividad y comparabilidad territorial. El rango ±21.05 pp es error histórico ilustrativo, no intervalo probabilístico prospectivo.

## Semáforo y estabilidad

El color divide tasas estimadas nacionales en tercios; no expresa probabilidad. Los umbrales base quedan fijos al cambiar Base/Intervención/Δ. Gris significa falta de estimación con motivo visible.

**Estabilidad de selección** es la frecuencia de entrada entre seis variantes: dos métodos × NS 5/10/20, con los mismos filtros, criterio y capacidad. 6/6 forma el núcleo robusto; 1/6–5/6, zona de revisión. Elegibilidad se informa aparte: una variante no elegible cuenta como no seleccionada. Alta ≥5/6, media ≥3/6 y baja <3/6 son categorías descriptivas. Los métodos comparten datos y supuestos: pueden coincidir y equivocarse juntos. Los identificadores internos `confidence` y la columna CSV `confianza_prioridad` se conservan por compatibilidad; su significado es estabilidad, no probabilidad de acierto.

El perfil CCPC por edad, sexo y tipo de sección es una capa descriptiva posterior. No alimenta Ridge ni la prioridad. Las variables etarias y urbanas originales del predictor se documentan por separado; diferencias de grupos no son efectos causales.

En modo personas, la estabilidad usa el número de municipios que caben en el plan actual como N equivalente: cada variante calcula top N, sin repetir la asignación del mismo presupuesto humano. El filtro mínimo usa N antes de filtrar; la ficha y la frontera muestran N del plan final. Es una sensibilidad del ranking municipal, no del presupuesto humano entre variantes.

## Escenario y prevención

La demo incorpora un selector: sin intervención (inicial), SMS con referencia sueca o estadounidense, llamada para elaborar un plan de votación y modo personalizado. El catálogo muestra citas originales, población, elección, estimador e incertidumbre; las descargas preservan esa información. Véanse [fuentes y reglas del catálogo](modelado/EVIDENCIA_INTERVENCIONES.md).

La simulación permite municipio, estado y país. La cobertura es un total de personas para ese territorio y se asigna por prioridad o proporcionalmente a SV+NV 2024, sin repetir el total por municipio. El promedio territorial usa toda la base estimable del filtro, incluidos municipios no atendidos; el resumen de atendidos se presenta aparte. Municipios sin estimación y excluidos por catálogo no se tratan como abstención cero. En SMS el usuario proporciona la capacidad prevista de envío a personas distintas; CCPC no proporciona ese dato operativo.

Las acciones con evidencia usan `H = min(E × efecto_pp / 100, E × tasa estimada / 100)`, seguido de `tasa posterior = tasa estimada − 100 × H / O`. ITT se aplica a asignados; ATT a contactos efectivos. La cobertura comparable y la transferencia a México son supuestos explícitos, no hallazgos CCPC. Los extremos publicados de SMS se trasladan sin incluir incertidumbre del modelo ni de transferencia. El catálogo de la demo no modifica las salidas históricas de Python.

La fórmula siguiente corresponde al modo personalizado, que conserva una respuesta supuesta sin fuente causal:

```text
O = SV2024 + NV2024
E = mínimo(alcance supuesto, O)
H = E × tasa estimada / 100 × respuesta supuesta / 100
Tasa del escenario = tasa estimada − 100 × H / O
```

E es la asignación municipal de la cobertura total. La comparación agrega todos los municipios estimables del territorio filtrado, incluidos los no atendidos, ponderados por O. Se supone que los alcanzados presentan la tasa estimada y que la respuesta es aplicable; ambas son hipótesis. H es un número esperado hipotético, no personas observadas ni efecto probado.

Las fichas registran acción, responsable propuesto, condiciones, alcance, recurso y medición. El [caso municipal completo](entrega/CASO_MUNICIPAL.md) distingue cifras verificadas y propuesta operativa. El piloto propone asignación aleatoria entre territorios elegibles con balance y protocolo previo; cercanía del score no acredita equivalencia. Medir alcance y conocimiento es distinto de demostrar efecto sobre participación, que requiere comparación causal y potencia suficiente.

## Entrega y pendientes

| Elemento | Estado vigente |
|---|---|
| Reporte | PDF de 14 páginas y fuente regenerable |
| Presentación | PPTX/PDF de 10 diapositivas; ficha, perfil y frontera incluidos |
| Mapa comparativo | Demo local Base/Intervención/Δ, abre con doble clic |
| Base y código | CSV municipal, GeoJSON visual y fuentes disponibles |
| Caso y exposición | Caso 23008 y guion con recorrido de tres pasos |
| Registro, elegibilidad y cartas | Confirmación humana y firmas pendientes |
| Envío | No acreditado; preparar paquete final y acceso del jurado |
| Validación institucional | Responsables, capacidad, límites y protocolo del piloto por acordar |

Los requisitos se transcriben de la convocatoria local; esta actualización no verifica cambios en las reglas o plazos oficiales. El ZIP completo previo es respaldo histórico y no sustituye los archivos vigentes. Los planes de `docs/superpowers/` son registros de desarrollo, no el estado actual.

## Fuentes de verdad y reproducción

- [Métricas congeladas](modelado/salidas/metricas.json), [resultados municipales](modelado/salidas/resultados.json) y [metodología](modelado/METODOLOGIA.md).
- [Estado y correcciones](CORRECCIONES_Y_ESTADO.md), [demo](demo/README.md) y [reporte](entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf).
- [Presentación](entrega/presentacion/Umbral_presentacion.pptx) y [guion](entrega/GUION_PRESENTACION.md).

La verificación del software comprueba comportamiento e integridad; no valida precisión futura ni eficacia preventiva.

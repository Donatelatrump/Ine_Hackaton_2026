# Track 2 — requisitos, trabajo realizado y análisis de la propuesta

**Actualización:** diagnóstico inicial conservado. Capas, apertura directa, fichas, reporte y presentación se implementaron: [CORRECCIONES_Y_ESTADO.md](CORRECCIONES_Y_ESTADO.md). Escenario ahora con SV+NV 2024; nuevas métricas posteriores. Después se añadieron la ficha «¿Por qué este municipio?», la confianza de prioridad (frecuencia entre seis variantes), el perfil CCPC como capa explicativa separada, el Modo Director (capacidad territorial o humana) y la frontera de decisión: [plan de mejoras](../docs/superpowers/plans/2026-10-05-ficha-perfil-y-frontera.md). Registro, firmas, envío y validación institucional pendientes. La actualización prevalece sobre las tablas siguientes.

**Proyecto:** Umbral, atlas de decisión municipal.
**Corte de este documento:** 5 de octubre de 2026.
**Cobertura elegida:** México por municipio, claves INE.
**Estado:** prototipo funcional y evaluación retrospectiva; entrega formal pendiente.
**Repositorio privado:** https://github.com/Donatelatrump/Ine_Hackaton_2026.

Este documento reúne contexto suficiente para que otra persona o modelo evalúe el proyecto sin conocer la conversación. Distingue requisitos oficiales, decisiones nuestras, resultados medidos y propuestas aún sin implementar. No sustituye el reporte final exigido por el concurso.

## 1. Qué pide el track 2

El reto busca anticipar territorios con abstención elevada para planear recursos. Exige un modelo simple con historia electoral y variables sociodemográficas, escenarios sin intervención y con intervención hipotética, clasificación territorial comprensible y recomendaciones preventivas. Se trabaja con datos CCPC agregados y disociados, sin datos personales. [Convocatoria, página 3](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

Entregables específicos:

- Reporte metodológico y preventivo PDF de 10–15 cuartillas: variables, semáforo, prevención y priorización de recursos.
- Mapa ejecutable que compare ambos escenarios, junto con la base empleada en CSV/XLSX; se mencionan tableros y formatos geográficos como ejemplos.

Entregables generales: presentación de máximo 10 diapositivas, código/repositorio cuando corresponda y cartas de cesión y declaración de verdad firmadas. [Convocatoria, páginas 4–5](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

Se valoran alineación temática, solidez y claridad, originalidad, viabilidad y aplicación institucional. Registro hasta el 15 de octubre; entrega hasta el 31 de octubre de 2026, 23:59, en ZIP identificado por equipo y eje, por correo a grecia.castro@ine.mx y cirse.rodriguez@ine.mx. Omitir mínimos descalifica. [Convocatoria, páginas 4–5](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

Las decisiones de cubrir todo México, trabajar por municipio, usar Ridge, mirar hacia 2027 y adoptar capacidad inicial de 50 municipios son nuestras; no son mandatos de la convocatoria.

## 2. Qué problema intentamos resolver

La pregunta operativa es:

> Si un área de educación cívica puede atender N municipios, ¿cuáles conviene revisar primero, qué antecedentes respaldan su prioridad y cómo cambia un escenario al variar alcance y respuesta supuesta?

La persona usuaria define territorio y capacidad, revisa mapa y lista, inspecciona antecedentes y calidad, ajusta supuestos y descarga un plan. El producto busca apoyar una revisión institucional; todavía no está validado para asignar recursos de forma automática.

Se prioriza por **tasa de abstención estimada**, no por número absoluto de abstenciones ni por aumento respecto de una elección anterior. Estas decisiones producen listas diferentes: la elección de tasa debe justificarse según el objetivo institucional.

## 3. Qué hicimos y por qué

| Trabajo realizado | Por qué se hizo | Evidencia local |
|---|---|---|
| Organización de fuentes y originales | Mantener trazabilidad y separar los tres retos | README, fuentes y documentos oficiales |
| Auditoría de ZIP y CSV históricos | Evitar construir el modelo sobre conteos inconsistentes | `auditoria/RESULTADOS.md` y scripts |
| Agregación municipio-año | Convertir millones de registros agregados en una unidad territorial operativa | `datos_preparados/` |
| Abstención observada y NS separados | No tratar participación desconocida como abstención | Base con calidad y metodología |
| Referencia del mismo tipo electoral | Tener un punto de comparación sencillo y evitar equiparar intermedias con presidenciales | `modelado/core.py` |
| Ridge sobre ajuste a la referencia | Explorar señales adicionales con regularización y complejidad moderada | `modelado/ejecutar.py` |
| Cortes 2021 y 2024 | Medir resultados posteriores al entrenamiento y detectar falta de transferencia | `modelado/salidas/` |
| Cartografía y revisión de claves | Dibujar territorios reales sin unir por nombre | `cartografia/`, correspondencia auditada |
| Filtros de calidad y catálogo | Hacer visible dónde la evidencia es insuficiente | Demo y sensibilidades |
| Capacidad, alcance y respuesta editables | Convertir el mapa en una decisión operativa con supuestos explícitos | `demo/decision.js` |
| CSV, pruebas y documentación | Permitir inspección, reproducción y revisión de resultados | Tests, verificación de navegador y README |

El enfoque se reforzó tras una revisión externa: mayor claridad de decisión, comparación honesta con persistencia, calidad visible y escenarios operativos. Se sustituyó la idea inicial de sumar arbitrariamente 1/3/5 puntos de participación por una fórmula ligada a alcance y respuesta supuesta.

## 4. Datos y procesamiento

El usuario aportó ocho ZIP y cuatro PDF. La serie principal utiliza las seis elecciones ordinarias 2009, 2012, 2015, 2018, 2021 y 2024. Prisión preventiva y voto anticipado se conservan como fuentes independientes; no se incorporaron automáticamente al histórico ordinario municipal.

La auditoría principal procesó **54,872,712 filas de 192 CSV**, generando **14,779 registros municipio-año** y **2,477 claves** en el conjunto histórico. Se verificaron CRC, duplicados y reconciliación de conteos. El informe de auditoría contiene el detalle; no se afirma que esas comprobaciones resuelvan comparabilidad histórica territorial.

Definiciones:

```text
SV = registros de quienes sí votaron
NV = registros de quienes no votaron
NS = registros sin participación especificada
LN = SV + NV + NS
abstención observada (%) = 100 × NV / (SV + NV)
NS (%) = 100 × NS / LN
```

Si SV+NV es cero, la tasa no se calcula. Las claves se conservan como texto, con ceros iniciales. No se asume que una clave INE equivalga a INEGI. La suma de conteos precede al cálculo de porcentajes.

La regla principal exige antecedentes válidos con NS ≤10% tanto en el último proceso como en el último del mismo tipo. Para evaluar se exige además objetivo histórico observable con NS ≤10%. Esto selecciona cohortes de mejor calidad y limita la representatividad de las métricas.

Se excluyeron edades superiores a 120 de la construcción de proporciones etarias, conservando los conteos originales. La representación etaria usada es agregada. Sexo no se incorporó como predictor al modelo actual; no se incorporaron escolaridad ni variables externas no verificadas.

## 5. Cómo se construyó y evaluó el modelo

### Referencia

Predice la tasa de la última elección del mismo tipo: para 2021 usa 2015; para 2024 usa 2018; para 2027 usa 2021. Si no existe antecedente válido, no se reemplaza silenciosamente por una elección de otro tipo.

### Candidato Ridge

Usa diez características: abstención del mismo tipo, abstención del último proceso, diferencia de ambas, logaritmo de LN, proporción 18–29, proporción 60+ sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo de elección.

Se ajusta StandardScaler y Ridge para estimar el residual respecto a la referencia. Alpha=10 se fijó antes de ver las métricas. Cada ejemplo usa características anteriores a su año objetivo. No se usaron resultados futuros para construir predictores.

| Objetivo | Etiquetas de entrenamiento |
|---|---|
| Evaluación 2021 | 2015 y 2018 |
| Evaluación 2024 | 2015, 2018 y 2021 |
| Proyección exploratoria 2027 | 2015, 2018, 2021 y 2024 |

Regla fijada para elegir en 2021: Ridge debe mejorar MAE al menos 1%, sin empeorar MAE ponderado ni precisión top50. El resultado de 2024 no se utilizó para reajustar alpha y ocultar el deterioro.

### Resultados medidos

| Corte | Método | n | MAE, pp | MAE ponderado, pp | Coincidencias top50 |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia | 1,490 | 12.12 | 8.05 | 16/50 |
| 2021 | Ridge | 1,490 | 9.21 | 5.49 | 19/50 |
| 2024 | Referencia | 1,476 | 5.64 | 3.54 | 27/50 |
| 2024 | Ridge | 1,476 | 8.58 | 4.49 | 27/50 |

MAE expresa error absoluto promedio en puntos porcentuales. MAE ponderado utiliza LN del objetivo histórico. Top50 compara listas dentro de la misma cohorte evaluable; no equivale a recuperar los 50 municipios de mayor abstención de todo México.

**Interpretación:** Ridge mejora aproximadamente 23.9% el MAE en 2021, pero recupera solo 19/50 y empeora en 2024. No demuestra superioridad consistente. Se conserva como método exploratorio por la regla de 2021, no como ganador universal.

2021 es selección, no prueba independiente posterior a selección. 2024 es presidencial y no valida directamente 2027. Hay seis ocasiones electorales, solo tres intermedias; el tamaño de los CSV no compensa la escasez temporal.

## 6. Qué significa el mapa y la incertidumbre

La cartografía de referencia visual mayo 2024 contiene 2,477 claves. La demo utiliza una copia simplificada a 0.006 grados exclusivamente para dibujar.

Se estiman **1,783 municipios** y **694 quedan sin estimación**. El filtro inicial por entidades con catálogo constante deja **1,144 estimaciones**. Un catálogo constante no prueba que sus límites sean constantes: falta armonización histórica.

El semáforo usa tercios relativos de estimaciones nacionales. Alto significa pertenecer al tercio de tasas estimadas más altas; no significa probabilidad calibrada de deterioro ni garantía de que un municipio empeore.

El rango ilustrativo de 2027 aplica ±21.05 pp, percentil 90 del error absoluto de Ridge en 2021, truncado a [0,100]. Es amplio y no es intervalo de confianza prospectivo. La incertidumbre de NS 2024 se explica aparte, como límites históricos bajo extremos de participación desconocida.

## 7. Cómo funciona el escenario y qué puede concluirse

```text
alcance efectivo = mínimo(alcance supuesto por municipio, LN 2024)
adicional hipotética = alcance efectivo × abstención estimada/100 × respuesta supuesta/100
tasa del escenario = estimación − 100 × adicional hipotética / LN 2024
```

La agregación pondera por LN 2024 sobre los mismos municipios seleccionados. No se cambian los territorios al comparar escenarios. Respuesta cero conserva la base; filtros vacíos y capacidad cero generan selección vacía. Las entradas inválidas bloquean la exportación.

Supuestos: las personas alcanzadas presentan la tasa de abstención estimada, la respuesta es una hipótesis del usuario y LN 2024 limita cobertura sin proyectar el electorado de 2027. No se ha demostrado impacto causal ni calculado costos monetarios.

La demo **compara tasas y selección**, pero todavía colorea el mapa según el riesgo base: no ofrece dos capas cartográficas completas que cambien de color para ambos escenarios. Esa brecha visual debe revisarse para que la comparación geográfica exigida sea inequívoca.

Las acciones de información electoral accesible y educación cívica son líneas propuestas. Falta convertirlas en recomendaciones municipales verificables: acción, responsable, cobertura, condiciones de aplicación, recurso y evaluación. El simulador por sí solo no cumple esa parte preventiva.

## 8. Estado de cumplimiento

| Componente | Estado | Qué falta para sostener la entrega |
|---|---|---|
| Datos CCPC agregados | Implementado | Seleccionar y explicar base final y diccionario |
| Modelo simple con antecedentes | Implementado, evidencia mixta | Defender selección y límites sin exagerar resultados |
| Variables sociodemográficas | Implementado parcialmente | Justificar las disponibles y las omitidas |
| Sin/con intervención | Simulación implementada | Hacer inequívoca la comparación cartográfica |
| Semáforo | Implementado | Justificar umbrales y sensibilidad |
| Prevención y recursos | Parcial | Recomendaciones concretas y factibilidad institucional |
| Reporte PDF 10–15 cuartillas | Pendiente | Integrar método, evidencia y prevención |
| Mapa y base de entrega | Demo, GeoJSON y CSV disponibles | Preparar paquete final comprobable por el jurado |
| Presentación ≤10 diapositivas | Pendiente | Problema, decisión, resultados, límites y aplicación |
| Código/repositorio | Disponible, privado | Definir acceso del jurado o entregar código en ZIP |
| Cartas firmadas | Formatos disponibles | Confirmar firmas de todas las personas integrantes |
| Registro y envío oficial | No acreditados en este trabajo | Confirmar cumplimiento; no se hicieron automáticamente |

El ZIP completo actual es respaldo técnico: incluye dependencias y datos voluminosos. No equivale al ZIP final identificado por equipo y eje. El repositorio privado requiere acceso concedido a quien deba revisarlo; no se vuelve público por compartir el enlace.

## 9. Análisis frente a los criterios de evaluación

Esta tabla es valoración nuestra, no puntuación del comité.

| Criterio | Fortaleza actual | Debilidad actual | Evidencia que fortalecería la propuesta |
|---|---|---|---|
| Alineación | Datos CCPC, riesgo, escenarios y capacidad | Prevención aún poco desarrollada | Caso de uso completo y acciones ligadas al resultado |
| Claridad y solidez | Auditoría, referencia y resultados adversos visibles | Pocos cortes, 2024 adverso, incertidumbre amplia | Justificación metodológica y estabilidad de prioridades |
| Originalidad | Decisión revisable con calidad y restricciones | Un mapa y Ridge son herramientas comunes | Flujo institucional diferenciado y trazabilidad de acciones |
| Viabilidad | Demo local, CSV y código reproducible | Sin costos, responsables ni proceso institucional confirmado | Validación con área usuaria y plan operativo razonable |
| Aplicación institucional | Permite revisar territorios y registrar hipótesis | No acredita integración real ni efectividad | Piloto acotado con indicadores y límites de uso |

No contamos con análisis de las propuestas competidoras ni con pesos de evaluación publicados en el documento consultado. No podemos asignar una probabilidad de ganar.

## 10. Qué conviene cuestionar en el análisis

1. **Objetivo:** ¿atender tasas altas, deterioro o mayor número de abstenciones? La prioridad actual solo responde al primero.
2. **Selección:** ¿se justifica Ridge para intermedias pese a su deterioro presidencial, o conviene permitir referencia y comparación visible? Evaluar esto antes de modificar parámetros.
3. **Cohorte:** ¿qué territorios excluye NS y qué sesgo introduce? Comparar cobertura por entidad y tamaño municipal.
4. **Territorio:** ¿una clave constante conserva población y límites? Determinar una cohorte defendible o documentar excepciones.
5. **Ranking:** ¿cambian demasiado los primeros N bajo referencia, Ridge, umbrales NS y filtros? La incertidumbre del orden importa para decisiones de capacidad.
6. **Escenario:** ¿el alcance y respuesta son interpretables para un área usuaria? ¿Qué acción concreta permitiría evaluar esos supuestos?
7. **Mapa:** ¿el jurado puede observar geográficamente ambos escenarios y descargar datos consistentes?
8. **Prevención:** ¿cada recomendación identifica mecanismo plausible, responsable y medición sin inventar causalidad?
9. **Entrega:** ¿puede abrirse el paquete en otra computadora y comprobarse cada cifra?
10. **Narrativa:** ¿el pitch admite 2024 adverso y explica la utilidad que permanece aun cuando la referencia gana?

## 11. Prioridades propuestas, todavía pendientes

| Orden | Próximo trabajo | Motivo |
|---|---|---|
| 1 | Cerrar reporte, presentación, cartas y acceso/paquete | La entrega formal es obligatoria |
| 2 | Comparación cartográfica explícita sin/con intervención | Cubrir claramente el requisito de mapa |
| 3 | Recomendaciones preventivas y flujo institucional | Convertir exploración en propuesta aplicable |
| 4 | Sensibilidad del ranking y justificación territorial | Fortalecer la decisión antes de prometer precisión |
| 5 | Revisar diseño de selección/modelos con evidencia congelada | No perseguir mejoras aparentes por ajuste al resultado |

No se propone sumar algoritmos complejos como sustituto de estos pendientes. Cambios metodológicos nuevos deben distinguirse del experimento actual, para no reutilizar 2021 como prueba supuestamente independiente.

## 12. Archivos que permiten revisar lo afirmado

- [Auditoría](auditoria/RESULTADOS.md).
- [Base y calidad](datos_preparados/README.md).
- [Resultados del modelo](modelado/RESULTADOS.md).
- [Metodología reproducible](modelado/METODOLOGIA.md).
- [Métricas completas](modelado/salidas/metricas.json).
- [Predicciones retrospectivas](modelado/salidas/backtest_predicciones.csv).
- [Demo y ejecución](demo/README.md).
- [Especificación vigente](../docs/superpowers/specs/2026-10-05-atlas-decision-design.md).
- [Explicación general del proyecto](../EXPLICACION_DEL_PROYECTO.md).

Última verificación de implementación: 15 pruebas Python, 12 Node y 24 comprobaciones de navegador (incluida apertura file://), más integridad de artefactos. Estas pruebas verifican comportamiento y consistencia del software, no precisión prospectiva ni eficacia de una intervención.

## 13. Texto para solicitar una evaluación externa

> Analiza esta propuesta del track 2 del Hackathon INE. Contrasta requisitos, implementación y evidencia. Señala incumplimientos, riesgos metodológicos y oportunidades de originalidad/aplicación institucional. Considera el deterioro de Ridge en 2024, la selección en 2021, NS, límites municipales, incertidumbre y ausencia de causalidad. Separa hechos de hipótesis. Prioriza cambios por impacto y esfuerzo sin inventar datos, costos ni resultados. Indica qué decisiones se pueden defender hoy y qué evidencia falta; no asumas que más complejidad mejora la candidatura.

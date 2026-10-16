## Comparación de cuatro modelos ejecutada · 16 de octubre de 2026

Se entrenaron y evaluaron Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Se seleccionó HistGradientBoosting: MAE medio 6.8360 pp frente a 9.0094 de Ridge (24.12% menos error). LightGBM obtuvo MAE 6.8304 pp; la diferencia menor que 0.05 pp activó el desempate por MAE ponderado, favorable a HistGradientBoosting. Ridge fue el más rápido. La selección es retrospectiva, sin validación futura de 2027.

La versión vigente de demo6 incluye los cuatro métodos y usa HistGradientBoosting por defecto. La documentación anterior que sigue corresponde a la etapa previa al benchmark. Fuente actual: modelado/COMPARACION_4_MODELOS.md del track.

---

> Actualización de 16 de octubre de 2026: la versión vigente es demo6. Consultar `02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md` y `modelado/RESULTADOS.md` del track para parámetros y cifras actuales. El contenido fechado anteriormente conserva el contexto de su versión y no debe usarse como fuente de las métricas vigentes.

---

# Umbral: por qué, qué y cómo se desarrolló

**Versión corregida aguas.exe:** [cambios y estado](02_Prediccion_y_escenarios_de_riesgo/CORRECCIONES_Y_ESTADO.md). Reporte 14 páginas (8 secciones), presentación 10 diapositivas, capas y fichas ya generados. Registro/firmas/envío no acreditados. Escenario actual sobre SV+NV 2024; nuevas métricas posteriores, sin retuning.

Fecha de documentación: 5 de octubre de 2026. Proyecto para el track 2 del Hackathon INE 2026: predicción y escenarios de riesgo de abstención. Alcance elegido: todo México por municipio.

## Por qué se hizo

El objetivo es convertir datos oficiales de participación en una decisión que pueda revisarse: si existe capacidad para atender N municipios, ¿cuáles conviene examinar primero, qué datos respaldan su prioridad y cómo cambia un escenario bajo determinados supuestos de atención?

Se eligió el track más difícil por decisión del usuario. La dificultad por sí sola no garantiza ganar. Para fortalecer la propuesta se aplicaron las recomendaciones de evaluación: comparar contra una referencia simple, validar con elecciones posteriores, mostrar incertidumbre y calidad, y traducir el mapa a una decisión limitada por capacidad.

Este enfoque evita que la propuesta dependa únicamente de un mapa atractivo o de la complejidad de un algoritmo. Su valor es que permite inspeccionar antecedentes, reconocer datos insuficientes, contrastar métodos y descargar un plan con supuestos explícitos.

## Qué se hizo

1. Se organizaron los tres tracks en carpetas independientes y se revisaron requisitos y fuentes oficiales. El desarrollo principal se encuentra en `02_Prediccion_y_escenarios_de_riesgo`.
2. Se inventariaron y auditaron los archivos aportados por el usuario: ocho ZIP y cuatro PDF. El procesamiento histórico principal usa los seis procesos ordinarios 2009, 2012, 2015, 2018, 2021 y 2024. Los archivos especiales de prisión preventiva y voto anticipado se conservan como fuentes, sin mezclarlos automáticamente con la serie municipal ordinaria.
3. Se procesaron 54,872,712 filas de 192 CSV históricos y se generaron 14,779 registros municipio-año. Se verificaron integridad de ZIP, columnas, duplicados y reconciliación de conteos.
4. Se obtuvieron polígonos oficiales INE con cobertura de las 2,477 claves municipales. Se preservó la geometría original y se creó una copia simplificada para la visualización.
5. Se implementaron una referencia de persistencia y un modelo Ridge regularizado. Se compararon retrospectivamente en 2021 y 2024, sin usar datos del objetivo ni posteriores para construir características de cada corte.
6. Se generó una proyección exploratoria para la elección intermedia de 2027. Hay 1,783 municipios con estimación y 694 sin estimación. La ausencia permanece visible; nunca se convierte en riesgo cero.
7. Se construyó la demo local **Umbral**, con mapa, filtros, búsqueda, ficha histórica, semáforo relativo, selección por capacidad, escenario hipotético y exportación CSV. Se añadieron después la ficha «¿Por qué este municipio?», la estabilidad de prioridad, el perfil CCPC como capa explicativa separada, el Modo Director con capacidad territorial o humana y la frontera de decisión (núcleo robusto, zona de revisión y fuera).
8. Se incorporaron documentación reproducible, pruebas automatizadas, comprobaciones de navegador y revisión independiente.

## Cómo se hizo

### Preparación y calidad de datos

Se agregaron conteos por año y claves INE, conservadas como texto para mantener ceros iniciales. No se unieron municipios por nombre ni se supuso equivalencia entre claves INE e INEGI.

La tasa observada de abstención se calcula así:

```text
abstención (%) = 100 × NV / (SV + NV)
NS (%) = 100 × NS / LN
LN = SV + NV + NS
```

SV significa registros de quienes sí votaron; NV, quienes no votaron; NS, participación no especificada. NS se informa por separado: no se interpreta como abstención. Si no hay participación observable, la tasa queda ausente.

Para estimar se exige información válida y NS ≤10% en el último proceso y el último del mismo tipo. Para evaluar retrospectivamente se exige también objetivo observable con NS ≤10%. La evaluación es condicional a ese filtro y no representa todos los municipios. Se añadieron sensibilidades con umbrales de 5% y 20%.

Los valores de edad mayores a 120 se excluyen al construir proporciones etarias; no se altera por ello la tasa agregada de votación. Se mantienen archivos originales y registros de integridad y procedencia.

### Comparación de modelos

La referencia conserva la abstención de la última elección del mismo tipo: intermedia con intermedia y presidencial con presidencial. Es una alternativa sencilla y verificable que el modelo debe superar.

Ridge estima un ajuste a esa referencia usando tasas previas, diferencia entre el último proceso y el último del mismo tipo, tamaño de LN, composición etaria, proporción urbana, NS y tipo de elección. StandardScaler y Ridge se ajustan solo con entrenamiento anterior a cada corte. Alpha se fijó en 10 antes de observar resultados. Las salidas se limitan al rango [0,100].

| Objetivo histórico | Años de etiquetas de entrenamiento |
|---|---|
| 2021 | 2015 y 2018 |
| 2024 | 2015, 2018 y 2021 |
| Proyección exploratoria 2027 | 2015, 2018, 2021 y 2024 |

Cada etiqueta utiliza características anteriores a su propio año. MAE ponderado usa SV+NV del objetivo histórico, corrigiendo la descripción previa de LN sin alterar las cifras. Top50 compara dentro de la misma cohorte elegible.

La regla de selección se fijó para 2021: adoptar Ridge si mejora MAE al menos 1% y no empeora MAE ponderado ni precisión top50. El corte 2024 se mantuvo como comprobación adicional, sin reajustar parámetros tras observarlo.

### Resultados reales y su interpretación

| Corte | Método | Municipios | MAE, pp | MAE ponderado, pp | Aciertos top50 |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia del mismo tipo | 1,490 | 12.12 | 8.05 | 16/50 |
| 2021 | Ridge | 1,490 | 9.21 | 5.49 | 19/50 |
| 2024 | Referencia del mismo tipo | 1,476 | 5.64 | 3.54 | 27/50 |
| 2024 | Ridge | 1,476 | 8.58 | 4.49 | 27/50 |

Ridge cumple la regla de 2021 y reduce su MAE aproximadamente 23.9%, pero pierde frente a la referencia en 2024. Se conserva ese resultado adverso en la demo y documentación. No hay evidencia de una mejora consistentemente transferible.

2021 fue usado para seleccionar; no es evaluación independiente posterior a selección. 2024 es presidencial y no valida 2027. Existen seis ocasiones electorales nacionales, solo tres intermedias; millones de filas no equivalen a millones de muestras temporales independientes.

El rango ilustrativo de 2027 usa ±21.05 puntos porcentuales, tomado del percentil 90 del error absoluto retrospectivo de Ridge en 2021. No es un intervalo probabilístico calibrado ni garantiza cobertura futura de 90%. El semáforo clasifica en tercios relativos de las estimaciones nacionales, sin representar probabilidades de un evento.

### Cartografía y comparabilidad

Se utilizan polígonos INE de referencia visual de mayo de 2024, localizados desde el portal cartográfico 2025. La versión original contiene las 2,477 claves requeridas. La copia para la demo usa simplificación de 0.006 grados exclusivamente para dibujar; no se usa para cálculo territorial.

Un filtro inicial conserva entidades con catálogo de claves constante y deja 1,144 estimaciones. Es una precaución por claves: no certifica estabilidad de límites. Los cambios históricos de fronteras municipales siguen sin armonizar, incluso cuando una clave permanece igual.

### Decisión y escenario

La persona usuaria elige municipio, estado o México con municipios estimables incluidos, una acción y cobertura total. Para SMS se cuentan personas distintas previstas para envío, no mensajes ni lectores; para la llamada, contactos efectivos. La capacidad es un supuesto operativo del usuario, no un dato CCPC.

Dos reglas propias de planeación distribuyen la cobertura: focalización por ranking (tasa, volumen o deterioro), o reparto proporcional a SV+NV 2024. La proporcional usa mayor resto para conservar personas enteras y desempata por clave. Ambas limitan la cobertura a la base disponible, sin asignar acciones a municipios sin estimación. No son recomendaciones de efectividad derivadas de los estudios.

Las acciones con evidencia usan `H = min(E × efecto_pp / 100, E × tasa / 100)`. El modo personalizado usa `H = E × tasa / 100 × respuesta / 100`, con respuesta supuesta sin fuente causal. Tasa posterior municipal = tasa − 100 × H / (SV+NV 2024). La comparación territorial incluye municipios no atendidos, ponderados por SV+NV, y excluye los no estimables. El resumen distingue población incluida y excluida por filtros.

Cada acción incluye publicación original, país, población, elección, estimador y límites en la página y CSV. Véase [evidencia de intervenciones](02_Prediccion_y_escenarios_de_riesgo/modelado/EVIDENCIA_INTERVENCIONES.md). El traslado a México es hipotético: los intervalos externos no incorporan incertidumbre local ni del predictor. NS queda fuera; SV+NV 2024 no es electorado proyectado. Entradas inválidas bloquean resultados y exportación.

### Implementación técnica y validación

Python procesa y evalúa los datos; el núcleo puro separa características, métricas y escenarios. La demo utiliza HTML, CSS, JavaScript y Leaflet 1.9.4 local. Datos, geometría y librerías se sirven desde la computadora, sin teselas ni llamadas remotas necesarias para su funcionamiento. Los enlaces a fuentes oficiales requieren internet cuando se abren.

La verificación vigente ejecuta 30 pruebas Python y 21 pruebas Node, además de `demo/verificar_intervenciones.py`: escalas, asignación total y proporcional, ITT/ATT, incertidumbre, CSV con fuentes, invalidación y vista móvil/file://. Las capturas se regeneran con `demo/capturar_demo.py` y registran su configuración. Las comprobaciones antiguas del navegador correspondían al flujo anterior; no acreditan por sí solas los controles actuales.

La revisión independiente detectó y corrigió redondeo de efectos pequeños y uso del presupuesto territorial en la inversión municipal. La inversión personalizada usa la cobertura realmente asignada al municipio. Verificar el software no demuestra efectividad causal ni valida la proyección 2027.

## Cómo abrir y reproducir

Descomprimir el paquete y abrir una terminal en la carpeta `Ine_Hackaton`. Ejecutar:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener terminal activa, detener con Ctrl+C. Alternativamente abrir `demo/index.html` con doble clic: versión corregida incrusta datos y geometría en JavaScript y no requiere servidor.

Los comandos para regenerar el modelo y recursos están en `02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md`. El paquete incluye las dependencias locales de esta computadora; para otro sistema operativo o versión de Python se deben reinstalar según requirements. La demo preparada requiere únicamente un servidor HTTP, sin volver a entrenar.

## Dónde está cada cosa

| Ruta | Contenido |
|---|---|
| `01_Perfiles_ciudadanos_de_participacion/` | Información organizada del track 1 |
| `02_Prediccion_y_escenarios_de_riesgo/` | Desarrollo elegido y ZIP originales |
| `02_…/documentos_oficiales/` | Documentos oficiales descargados |
| `02_…/auditoria/` | Scripts, inventarios y resultados de auditoría |
| `02_…/datos_preparados/` | Bases municipales agregadas y calidad |
| `02_…/cartografia/` | Fuentes y geometría oficial de referencia |
| `02_…/modelado/` | Código, pruebas, metodología, resultados y salidas |
| `02_…/demo/` | Aplicación, datos locales, librería y evidencias de navegador |
| `03_Comunicacion_y_visualizacion/` | Información organizada del track 3 |
| `docs/superpowers/` | Especificación, plan y registro de decisiones |
| `.task_packages/` | Dependencias locales de Python |
| `MANIFIESTO_PAQUETE.json` | Inventario y SHA256 de archivos empaquetados |

En la tabla, `02_…` abrevia `02_Prediccion_y_escenarios_de_riesgo`.

## Qué falta y qué no se afirma

El prototipo y documentos técnicos están implementados. Faltan armonización o justificación territorial histórica, revisión institucional, confirmar registro, firmar cartas y enviar oficialmente. El reporte y presentación están en `entrega/`. No se garantiza ganar ni se valida asignación definitiva de recursos.

La oportunidad competitiva es presentar una herramienta que haga explícitos su capacidad, evidencia, incertidumbre y supuestos. La mejora del algoritmo en una elección debe explicarse junto con su deterioro en otra.

## Fuentes y documentación complementaria

- [Hackathon INE 2026](https://ine.mx/hackathon-2026/).
- [Convocatoria oficial](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).
- [Conteos Censales de Participación Ciudadana](https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/).
- [Portal cartográfico INE](https://pautas.ine.mx/transparencia/mapas/index_2025.html).
- Documentación local: `modelado/RESULTADOS.md`, `modelado/METODOLOGIA.md`, `demo/README.md`, auditoría y registro del plan, dentro del track 2.

## Alcance del ZIP

El ZIP contiene todos los archivos existentes del proyecto al empaquetar, incluidas las tres carpetas de tracks, originales, dependencias, evidencias y este documento. Se excluye únicamente el propio ZIP de salida y su archivo temporal de construcción para evitar incluirlo dentro de sí mismo. El manifiesto describe los restantes archivos y se incluye también en el paquete; no se calcula un hash del manifiesto dentro de sí mismo.

**Estado del paquete:** el `Ine_Hackaton_completo.zip` conservado es un respaldo generado el 5 de octubre de 2026 a las 20:42, anterior a las correcciones del track 2. No incluye la demo corregida (capas Base/Intervención/Δ, fichas, vista por entidad, apertura `file://`), la carpeta `entrega/` ni los análisis posteriores. La entrega técnica vigente es este repositorio; para reconstruir un ZIP actualizado se ejecuta `empaquetar_proyecto.py`.

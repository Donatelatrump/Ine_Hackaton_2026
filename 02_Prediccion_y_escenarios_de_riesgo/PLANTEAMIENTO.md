# Propuesta de proyecto: Atlas de riesgo de abstención

Fecha: 2026-10-05. Estado: modelo comparado temporalmente y demo local implementada. Auditoría completa: 54,872,712 filas originales y 14,779 registros municipales; cartografía de 2,477 claves, límites históricos sin armonizar. Véanse [resultados actuales](modelado/RESULTADOS.md) y [demo](demo/README.md).

Este documento conserva el planteamiento inicial. La especificación vigente está en `../docs/superpowers/specs/2026-10-05-atlas-decision-design.md`: capacidad, alcance y respuesta supuesta sustituyen escenarios de incremento arbitrario. Se elige Ridge por 2021, pero pierde en 2024, por lo que 2027 sigue siendo exploratorio.

## Resultado que buscamos

Una herramienta que permita al INE localizar territorios con riesgo de abstención, revisar las señales que sustentan esa clasificación y comparar un escenario base con una intervención hipotética. El resultado debe ser reproducible, interpretable y respaldado por datos oficiales agregados.

El usuario confirmó cobertura nacional por municipio. Se conservará este alcance; las series y geometrías deben pasar una auditoría de comparabilidad. Los municipios sin datos suficientes permanecerán identificados en el mapa con esa condición. No se presupone que la descarga contenga todas las variables que muestra el tablero.

## Tres alternativas

| Enfoque | Ventaja | Limitación |
|---|---|---|
| Índice de riesgo con reglas documentadas | Rápido y explicable | Puede reflejar decisiones arbitrarias; requiere validación |
| Modelo explicable con historia electoral y variables agregadas | Equilibrio entre rigor, claridad y esfuerzo; recomendado | Exige datos comparables y evaluación temporal |
| Modelo complejo con análisis espacial y muchos predictores | Mayor capacidad potencial | Mayor esfuerzo y riesgo de sobreajuste con pocos años |

Recomendación: una referencia simple y un modelo regularizado. Adoptar el segundo solamente si supera a la referencia en pruebas temporales y mantiene una interpretación útil.

## Qué necesitamos conseguir

1. Bases CCPC de 2009, 2012, 2015, 2018, 2021 y 2024, diccionarios y metodología.
2. Conteos de quienes votaron, no votaron y registros no especificados; lista nominal, año y claves territoriales. Confirmar que estos campos estén realmente en la exportación.
3. Composición agregada por edad, sexo y tipo de sección, cuando exista una desagregación compatible. No inferir escolaridad si no está disponible.
4. Geometrías oficiales y catálogo de claves: obtenidos polígonos INE de referencia visual mayo 2024, completos para 2,477 claves. Comparabilidad de límites históricos pendiente.
5. Bases de la convocatoria, cartas oficiales y manual de la plataforma.

Fuentes: [CCPC](https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/), [manual](https://ine.mx/wp-content/uploads/2025/06/Manual-Conteos-Censales-2009-2024.pdf), [convocatoria](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

## Auditoría antes de modelar

- Registrar URL, fecha de descarga, tamaño y SHA-256; mantener los originales intactos.
- Inspeccionar columnas, codificación, unidades, granularidad, duplicados y valores faltantes.
- Verificar si existen identificadores personales y excluirlos del proyecto; usar exclusivamente información agregada y disociada.
- Conservar claves territoriales como texto para mantener ceros iniciales.
- Distinguir cero, falta de información y registros no especificados.
- Revisar cambios de municipios, secciones y distritos. No unir por nombre ni suponer estabilidad de claves.
- Utilizar el denominador oficial: abstención = no_votaron / (si_votaron + no_votaron). Reportar aparte la proporción de no especificados respecto de la lista nominal. Fuente: manual, páginas 17–18.
- Obtener tasas agregadas sumando conteos; no promediar porcentajes municipales sin ponderación.

## Diseño del análisis

### Pregunta operativa

¿Qué municipios podrían presentar una abstención elevada en una próxima elección federal intermedia, dadas las series disponibles? El horizonte inicial propuesto es 2027; es una decisión del proyecto, no una fecha exigida por las bases. Los datos hasta 2024 no permiten incorporar cambios posteriores sin fuentes adicionales.

### Variables candidatas

Abstención previa de una elección del mismo tipo, variación respecto a comicios comparables, tamaño del electorado y composición agregada. Cada predictor debe existir antes de la elección objetivo: no usar resultados o composición de la elección futura para predecirla retrospectivamente.

Analizar por separado intermedias (2009, 2015, 2021) y presidenciales (2012, 2018, 2024), o incluir explícitamente el tipo de elección en un modelo combinado. El manual también distingue estas series en su sección de comparaciones.

### Entrenamiento y validación

1. Referencia: persistencia de la abstención del último proceso comparable.
2. Candidato: regresión regularizada con pocos predictores. Evaluar otro algoritmo únicamente si los datos justifican la complejidad.
3. Pruebas por tiempo: entrenar con elecciones anteriores y reservar una posterior. Para intermedias, 2021 es la última prueba retrospectiva disponible; 2024 no es una prueba intermedia.
4. Ajustar imputación, escalado y parámetros solamente con entrenamiento. Mantener la separación temporal también en la selección de variables.
5. Medir error absoluto en puntos porcentuales, error ponderado por electorado, errores por región y estabilidad de territorios prioritarios. Documentar la limitada evidencia temporal.
6. Si no supera a la referencia, presentar la referencia como modelo final y explicar el resultado.

No interpretar asociaciones territoriales como causas ni como conductas de personas concretas. La incertidumbre y la cobertura de datos deben ser visibles.

### Semáforo

Proponer umbrales documentados sobre abstención estimada y comprobar su estabilidad. Diferenciar "abstención alta" de "deterioro respecto de la referencia". Un municipio sin cobertura suficiente debe aparecer como "información insuficiente", no como riesgo bajo.

## Escenarios

Escenario base: estimación sin intervención adicional.

Escenario con intervención: simular aumentos de participación de 1, 3 y 5 puntos porcentuales en territorios seleccionados. Son supuestos para un análisis de sensibilidad, no efectos demostrados de una campaña. Mantener las tasas entre 0 y 100 y explicitar población cubierta, presupuesto supuesto y regla de selección.

Intervenciones propuestas: información accesible sobre cómo votar y actividades de educación cívica. El mapa debe mostrar qué territorios se seleccionaron, cuánto cambia la estimación y qué supuestos explican la diferencia.

Las recomendaciones de recursos se basarán en necesidad estimada, cobertura y factibilidad. No inventar costos por persona ni prometer impacto causal sin evidencia.

## Herramientas propuestas

- Python para limpieza y modelos; pandas y scikit-learn como opciones.
- GeoPandas para cruces geográficos si el tamaño y formato lo permiten.
- Dashboard con mapa, filtros, explicaciones y comparación de escenarios; elegir entre Streamlit o una web según capacidades del equipo y forma de entrega.
- CSV y GeoJSON como salidas portables; README y scripts reproducibles.

Son opciones de diseño. Aún no se han instalado dependencias ni elegido versiones.

## Entregables y organización

Según la convocatoria, el track exige reporte metodológico de 10–15 cuartillas, mapa de escenarios y base anonimizada CSV/XLSX. Los entregables generales incluyen presentación ejecutiva de hasta 10 diapositivas, código/repositorio cuando corresponda y las dos cartas firmadas. Entrega: 31 de octubre de 2026, 23:59. Ver las páginas 4–5 del PDF para especificaciones y envío íntegros.

Distribución propuesta de responsabilidades: datos y calidad; modelo y validación; cartografía/dashboard; reporte y presentación. Una persona puede asumir más de una responsabilidad según el equipo.

## Secuencia de trabajo propuesta

| Periodo | Trabajo | Condición de cierre |
|---|---|---|
| 5–8 octubre | Fuentes y auditoría | Bases reales, diccionario y cobertura documentados |
| 9–12 octubre | Integración territorial y referencia | Tabla histórica verificable y uniones auditadas |
| 13–17 octubre | Modelo y validación | Comparación reproducible contra referencia |
| 18–22 octubre | Escenarios y mapa | Supuestos visibles y datos exportables |
| 23–27 octubre | Reporte y presentación | Correspondencia entre cifras, mapa y documentos |
| 28–30 octubre | Revisión final | Enlaces, formatos, cartas y paquete comprobados |
| 31 octubre | Entrega | Margen previo al cierre oficial |

Reservar además el registro del equipo dentro del plazo oficial; no esperar a terminar el modelo.

## Criterios de aceptación del proyecto

El tablero abre, todos sus valores se rastrean a datos y transformaciones, el modelo tiene evaluación temporal, los escenarios están rotulados como hipotéticos, no hay datos personales, la geometría y las claves concuerdan, las tasas y denominadores son consistentes y los entregables cumplen la convocatoria.

## Estado real de las descargas

**Actualización:** los archivos fueron aportados manualmente y ya están disponibles. El inventario actual está en `auditoria/inventario_local.json`; las bases aún requieren auditoría completa y agregación municipal. La cartografía continúa pendiente. Los párrafos siguientes describen el intento de descarga previo, no la disponibilidad actual.

La lectura de páginas mediante búsqueda web funciona. La descarga binaria desde PowerShell/curl falló tanto en ine.mx como en portal.ine.mx. El descargador Python confirmó WinError 10013: acceso a un socket no permitido por los permisos del entorno. La herramienta de navegador no tiene superficies conectadas. Por ello, no hay PDF ni bases locales descargadas; `estado_descargas.json` registra los cuatro fallos.

El archivo `fuentes.json` registra los cuatro PDF con URL identificada. `descargar_documentos.py` permite intentar obtenerlos desde una terminal con conexión y deja un registro de éxitos/fallos. Este descargador no obtiene las bases ni la cartografía: los enlaces de los años no pudieron resolverse con la herramienta web; se requiere acceder a la plataforma o exportar sus tablas. No tratar los documentos como sustitutos de las bases.

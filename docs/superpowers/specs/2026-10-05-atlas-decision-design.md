# Atlas de decisión municipal: diseño aprobado

El usuario pidió aplicar las recomendaciones de la revisión y continuar. La finalidad es competir en el track 2 con evidencia retrospectiva y una demo de decisión institucional para todo México por municipio.

## Alcance de esta ejecución

1. Comparar persistencia del último proceso del mismo tipo con Ridge sobre cambios de abstención, utilizando solamente información anterior al año objetivo. Coeficientes y escalado se ajustan dentro de cada corte temporal. Alpha=10, fijado antes de ver métricas.
2. Prueba de selección 2021 y comprobación adicional 2024 sin modificar características o parámetros a partir de esa comprobación. La selección en 2021 significa que sus métricas no son una estimación independiente posterior a la selección. El último corte intermedio disponible sigue siendo 2021.
3. Seleccionar Ridge solo si reduce MAE al menos 1%, no empeora el MAE ponderado y no empeora precisión de los 50 municipios de mayor abstención. De lo contrario publicar persistencia.
4. Calidad: NS máximo 10% en los antecedentes utilizados; denominador observado positivo. Evaluación exige además objetivo observable y NS máximo 10%. Estas son decisiones exploratorias; informar sensibilidad a 5% y 20% y tamaño de cohortes.
5. Comparabilidad territorial aproximada por clave: comparar también entidades cuyo catálogo de claves permanece constante entre antecedentes y objetivo. No afirmar armonización de límites. Los municipios sin un antecedente del mismo tipo no reciben una proyección numérica.
6. Proyección exploratoria 2027 utilizando datos disponibles hasta 2024. No considerarla validada para 2027. Intervalo mostrado: amplitud empírica del error retrospectivo; no intervalo probabilístico calibrado. Mostrar por separado límites históricos derivados de NS.
7. Demo local estática sin servicio remoto: mapa municipal, búsqueda, filtros por entidad, capacidad operativa, listado priorizado, ficha de municipio e historia, métricas y exportación CSV. Ranking por abstención estimada; mostrar calidad y cobertura. No personalizar mensajes por grupos demográficos.
8. Escenario: seleccionar hasta N municipios; alcance por municipio limitado al electorado observado del último año. Participación adicional hipotética = alcance × abstención estimada/100 × respuesta supuesta/100. Mostrar cambio sobre población cubierta y respetar tasas 0–100. No atribuir efectos causales ni costos monetarios sin evidencia.
9. Sin modificar ZIP, CSV originales o GeoJSON oficiales. Geometría simplificada solamente para la demo, con CRS WGS84. Datos y librerías web locales para poder abrir la demo sin conexión externa.

## Arquitectura

`modelado/core.py`: funciones de características, cohortes, métricas, selección y escenario; pruebas unitarias con fixtures independientes.
`modelado/ejecutar.py`: lee la base auditada, ajusta por corte, produce CSV/JSON, resultados por entidad, sensibilidad y reporte metodológico.
`demo/`: HTML/CSS/JS, controles de escenario, mapa Leaflet, datos de la ejecución y geometría simplificada. Funciones de escenario JS verificadas con node:test.

## Éxito

Métricas reproducibles, datos sin fuga temporal, referencia visible, ausencia de datos distinguible de riesgo bajo, escenario con supuestos explícitos, interfaz usable en escritorio y móvil, exportación consistente con filtros, demo ejecutable localmente y pruebas de comportamiento completas.

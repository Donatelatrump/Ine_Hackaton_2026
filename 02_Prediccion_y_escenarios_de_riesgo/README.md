# Track 2: Predicción y escenarios de riesgo de abstención

**aguas.exe, versión corregida:** [estado](CORRECCIONES_Y_ESTADO.md), [reporte 14 páginas](entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf), [presentación 10 diapositivas](entrega/presentacion/Umbral_presentacion.pptx). Demo abre con doble clic y compara Base/Intervención/Δ. Registro, firmas y envío no acreditados.

[Documento para analizar requisitos, decisiones, resultados y pendientes](ANALISIS_TRACK_2.md).

**Prototipo ejecutable:** [Umbral](demo/README.md), con mapa nacional, filtros de calidad, priorización por capacidad y exportación de escenarios. [Resultados reales del modelo](modelado/RESULTADOS.md) y [reproducción](modelado/METODOLOGIA.md). Ridge mejora en 2021 y pierde frente a la referencia en 2024: la proyección 2027 se conserva explícitamente como exploratoria.

Analítica predictiva para anticipar abstención territorial y priorizar recursos: modelar riesgo con tendencias y variables agregadas, comparar escenarios con/sin intervención, comunicar riesgo y recomendar prevención. Sin datos personales.

Entregables: reporte metodológico y preventivo PDF de 10–15 cuartillas, semáforo territorial; mapa comparativo ejecutable (Power BI/Tableau, SHP/GeoJSON/GPKG) y base anonimizada CSV/XLSX.

Consulta el desarrollo completo del reto en la página 3 y sus entregables en la página 4 de la [convocatoria oficial](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

Los requisitos y recursos compartidos están en [RECURSOS.md](RECURSOS.md).

Proyecto seleccionado: **todo México por municipio**. Consultar [PLANTEAMIENTO.md](PLANTEAMIENTO.md), [fuentes.json](fuentes.json), [DESCARGAS.md](DESCARGAS.md) y [estado_descargas.json](estado_descargas.json).

Los archivos ya fueron aportados manualmente. Ver [revisión inicial](auditoria/REVISION_INICIAL.md) e [inventario local](auditoria/inventario_local.json). `estado_descargas.json` conserva los fallos históricos del descargador y no representa la disponibilidad actual.

La base municipal y su documentación están en [datos_preparados](datos_preparados/README.md). El resultado de la auditoría completa está en [RESULTADOS.md](auditoria/RESULTADOS.md). La demo dibuja la capa CONABIO/INEGI AGEM 2024: parte de 2,478 polígonos, los cruza por nombre normalizado y alias explícitos con las 2,477 claves de la base, y agrega Villa de Pozos a San Luis Potosí (24028), clave histórica que conserva la base. Los dos pares homónimos de Oaxaca se emparejan por orden de clave. El cruce de identificadores no armoniza límites históricos; la cita y el método están en [fuentes.json](fuentes.json) y [la guía de la demo](demo/README.md).

Entrega unificada el 6 de octubre de 2026: [caso municipal](entrega/CASO_MUNICIPAL.md) y [guion de presentación](entrega/GUION_PRESENTACION.md). Estabilidad de selección es frecuencia descriptiva; las variantes comparten datos y pueden equivocarse juntas.

Actualización de escenarios: municipio, estado o México con estimación incluida; cobertura total, distribución por prioridad o proporcional a SV+NV 2024 y acciones con citas originales. El efecto trasladado a México es hipotético. Caso, reporte y presentación distinguen la evidencia publicada de reglas de planeación y supuestos. La demo muestra exclusiones y conserva fuentes y distribución en CSV.

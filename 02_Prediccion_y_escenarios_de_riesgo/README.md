# Track 2: Predicción y escenarios de riesgo de abstención

**Prototipo ejecutable:** [Umbral](demo/README.md), con mapa nacional, filtros de calidad, priorización por capacidad y exportación de escenarios. [Resultados reales del modelo](modelado/RESULTADOS.md) y [reproducción](modelado/METODOLOGIA.md). Ridge mejora en 2021 y pierde frente a la referencia en 2024: la proyección 2027 se conserva explícitamente como exploratoria.

Analítica predictiva para anticipar abstención territorial y priorizar recursos: modelar riesgo con tendencias y variables agregadas, comparar escenarios con/sin intervención, comunicar riesgo y recomendar prevención. Sin datos personales.

Entregables: reporte metodológico y preventivo PDF de 10–15 cuartillas, semáforo territorial; mapa comparativo ejecutable (Power BI/Tableau, SHP/GeoJSON/GPKG) y base anonimizada CSV/XLSX.

Consulta el desarrollo completo del reto en la página 3 y sus entregables en la página 4 de la [convocatoria oficial](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).

Los requisitos y recursos compartidos están en [RECURSOS.md](RECURSOS.md).

Proyecto seleccionado: **todo México por municipio**. Consultar [PLANTEAMIENTO.md](PLANTEAMIENTO.md), [fuentes.json](fuentes.json), [DESCARGAS.md](DESCARGAS.md) y [estado_descargas.json](estado_descargas.json).

Los archivos ya fueron aportados manualmente. Ver [revisión inicial](auditoria/REVISION_INICIAL.md) e [inventario local](auditoria/inventario_local.json). `estado_descargas.json` conserva los fallos históricos del descargador y no representa la disponibilidad actual.

La base municipal y su documentación están en [datos_preparados](datos_preparados/README.md). El resultado de la auditoría completa está en [RESULTADOS.md](auditoria/RESULTADOS.md); los polígonos de referencia visual están en `cartografia/municipios_ine_2024.geojson`.

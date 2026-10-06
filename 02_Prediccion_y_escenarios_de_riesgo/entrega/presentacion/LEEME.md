# Presentación Umbral

`Umbral_presentacion.pptx`: diez diapositivas con textos y tabla editables.

Actualización: 6 de octubre de 2026. Incluye ficha de decisión, estabilidad de selección, frontera y caso 23008. SOLIDARIDAD es el nombre del catálogo histórico. El resultado adverso de 2024 y los supuestos del escenario permanecen explícitos. Ver [guion](../GUION_PRESENTACION.md) y [caso completo](../CASO_MUNICIPAL.md).

`Umbral_presentacion.pdf`: exportación de la misma composición con ReportLab. No es una conversión del PPTX mediante PowerPoint.

`generar_presentacion.py`: fuente reproducible. Ejecutar con Python y python-pptx, reportlab y pymupdf instalados. Busca dependencias locales en `.packages` y en `../reporte/.packages`.

Paleta y tipografía tomadas de la demo Umbral: teal #10685F, sage #E5EEEA, fondo #F3F6F4, Segoe UI. Cifras retrospectivas del experimento original y Spearman de `modelado/salidas/evaluacion_adicional.json`, identificado como análisis posterior.

## Revisión

Se generaron diez páginas PNG `QA_01.png` a `QA_10.png` desde el PDF y se inspeccionó su composición. Se comprobó el número de diapositivas, los nombres del equipo y la presencia de textos y tabla editables en PPTX. LibreOffice no está disponible en este entorno. Falta abrir el PPTX en PowerPoint para comprobar la composición bajo su motor de renderizado.

La diapositiva 6 incorpora capturas reales de la demo corregida: intervención hipotética y diferencia. Las capturas se conservan como fuentes PNG junto al script.

Firmas, registro y envío formal quedan pendientes del equipo.


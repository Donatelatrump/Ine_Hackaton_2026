# Presentación Umbral

Actualización: 6 de octubre de 2026. Diez diapositivas. [PPTX editable](Umbral_presentacion.pptx) y [PDF](Umbral_presentacion.pdf). Ver [guion](../GUION_PRESENTACION.md).

Incluye territorio municipio/estado/país, cobertura total, acciones con evidencia externa, reglas propias de distribución y caso 23008 con 1,000 personas previstas para SMS Suecia. Los 3 votos adicionales y la reducción 0.001175 pp son un traslado hipotético a México. La estabilidad del plan usa N equivalente a municipios atendidos y no recalcula presupuesto ni reparto. El 4/6 del caso describe el ranking de referencia top50 documentado. Ridge mejora en 2021 y empeora en 2024. Modelo congelado.

La diapositiva 6 explica coeficientes y comparación territorial con texto editable. Las capturas mapa_intervencion.png y mapa_cambio.png son capturas actuales auxiliares copiadas de demo/verificacion. No se usan en el deck.

`generar_presentacion.py` reproduce el deck mediante edición OOXML estándar de `plantilla_base.pptx`, sin python-pptx, y genera PDF con ReportLab. Requiere reportlab, PyMuPDF y Pillow. Usa dependencias locales .packages y ../reporte/.packages de solo lectura. Conserva diseño, Segoe UI, dimensión y tabla nativa del original.

El PDF comparte composición y contenido con PPTX, pero no es conversión de PowerPoint. Los PNG QA_01 a QA_10 proceden del PDF. Se inspeccionaron diez renders y se verificaron cantidad de diapositivas, texto editable, notas y tabla nativa. El entorno no ofrece runtime Artifact Tool ni conversión nativa PowerPoint/LibreOffice. Queda pendiente comprobar el PPTX bajo ese motor antes de presentar.

Firmas, registro y envío formal pendientes del equipo.


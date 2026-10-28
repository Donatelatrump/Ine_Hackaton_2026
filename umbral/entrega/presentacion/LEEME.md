# Presentación ejecutiva — Umbral

Actualizada el 28 de octubre de 2026. [PPTX editable](Umbral_presentacion.pptx) y [PDF](Umbral_presentacion.pdf), diez diapositivas. [Guion de demostración](../GUION_PRESENTACION.md).

Secuencia: problema, funciones de Umbral, construcción de la predicción, evaluación, consulta territorial, simulación, planes estatales, ejemplo SMS y uso institucional. Incluye capturas reales de mapas e interfaz. La diapositiva 7 compara escenarios; la 8 presenta los planes estatales. El escenario estatal no es una evaluación causal del plan.

`generar_presentacion.py` ejecuta `generar_presentacion_clara.py`, que conserva textos editables e incorpora las capturas reales. `exportar_powerpoint.ps1` abre el PPTX en PowerPoint y exporta el PDF nativo. Requiere PowerPoint instalado, Segoe UI, PyMuPDF y Pillow. Primero ejecutar la prueba de la demo para actualizar las capturas.

`QA_01.png` a `QA_10.png` y `QA_montaje.png` proceden del PDF exportado por PowerPoint. El verificador comprueba diez diapositivas, cifras, texto y límites del PDF. La nueva composición fue revisada visualmente después de la exportación nativa.

[Revisión de requisitos del INE](../REVISION_REQUISITOS_INE.md).

La diapositiva 9 presenta un escenario de cobertura municipal completa: población CONAPO proyectada de 437,681 habitantes en 2027 y cobertura limitada a SV+NV 2024 (255,362 personas). Con 0.30 pp del estudio SMS, el resultado es 766.086 votos hipotéticos y 0.30 pp de reducción municipal. Es un escenario distinto del caso de 1,000 asignaciones documentado en el reporte y caso_municipal.json. La diapositiva 10 reúne las referencias.

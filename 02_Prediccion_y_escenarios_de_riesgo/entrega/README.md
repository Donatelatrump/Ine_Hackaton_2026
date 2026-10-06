# Entrega técnica vigente

Actualización: 6 de octubre de 2026. Umbral, equipo Tecnocalidos, track 2.

- [Reporte PDF](reporte/Umbral_reporte_metodologico_preventivo.pdf): 14 páginas; editar `reporte/generar_reporte.py` para regenerar PDF y fuente Markdown.
- [Presentación PPTX](presentacion/Umbral_presentacion.pptx) y [PDF](presentacion/Umbral_presentacion.pdf): diez diapositivas; editar `presentacion/generar_presentacion.py`.
- [Caso municipal](CASO_MUNICIPAL.md): evidencia, acción propuesta, responsables por validar, recursos, condiciones y evaluación.
- [Guion](GUION_PRESENTACION.md): discurso de cinco minutos, preguntas y demo en tres pasos.
- [Demo](../demo/index.html): mantener su carpeta completa para apertura local.
- [Base municipal](../datos_preparados/municipios_historico_con_calidad.csv) y [proyección exploratoria](../modelado/salidas/proyeccion_exploratoria_2027.csv).

La descripción vigente está en [ANALISIS_TRACK_2.md](../ANALISIS_TRACK_2.md). Modelo y métricas conservan el experimento original. Registro, elegibilidad, firmas, envío y validación institucional requieren actos humanos; no se acreditan aquí.

## Regeneración desde la raíz

```powershell
python -m pip install --index-url https://pypi.org/simple --target .task_packages python-pptx==1.0.2 reportlab==5.0.1 pymupdf==1.28.2 pillow==12.3.0
$env:PYTHONPATH = (Join-Path (Get-Location) '.task_packages')
node 02_Prediccion_y_escenarios_de_riesgo/entrega/generar_caso.cjs
python 02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/generar_reporte.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/presentacion/generar_presentacion.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/verificar_entrega.py
```

La presentación usa Segoe UI de Windows. El PDF se construye con la misma composición del generador; no es una conversión mediante PowerPoint. La revisión del motor PowerPoint sigue pendiente. El ZIP anterior conserva su identificación como respaldo histórico; estos archivos son la entrega técnica vigente.

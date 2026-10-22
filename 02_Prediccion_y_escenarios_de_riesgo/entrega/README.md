# Entrega técnica de Umbral · Demo7

Actualización: 21 de octubre de 2026. Equipo aguas.exe, Reto 2: Predicción y escenarios de riesgo de abstención.

La [revisión de requisitos del INE](REVISION_REQUISITOS_INE.md) identifica la evidencia de cada requisito y los pendientes administrativos. Esta carpeta no acredita registro, elegibilidad, firmas ni envío oficial.

## Archivos de revisión

- [Reporte metodológico y preventivo PDF](reporte/Umbral_reporte_metodologico_preventivo.pdf): 14 páginas, variables, evaluación, semáforo y prevención.
- [Presentación PDF](presentacion/Umbral_presentacion.pdf) y [PPTX editable](presentacion/Umbral_presentacion.pptx): diez diapositivas.
- [Demo7](../demo/demo7.html) y [guía de ejecución](../demo/DEMO7.md): mapas sin/con acción, diferencias y exportación de distribución CSV.
- [Base histórica agregada](../datos_preparados/municipios_historico_con_calidad.csv), [proyecciones de los cuatro modelos](../modelado/salidas/comparacion_modelos/proyeccion_2027.csv) y [evaluación vigente](../modelado/salidas/comparacion_modelos/resultados.json).
- [Caso municipal](CASO_MUNICIPAL.md) y [guion de demostración](GUION_PRESENTACION.md).
- [Verificación de entrega](verificacion_unificacion.json) y [prueba de navegador de demo7](../demo/verificacion/demo7/resultado.json).

El plan estatal usa cobertura inicial del 10% y efecto supuesto de 1.5 pp entre alcanzados, con variantes 0.3/3 pp. Son hipótesis del proyecto. El caso municipal SMS conserva el coeficiente externo de 0.30 pp; no debe confundirse con el plan estatal ni atribuirse a México como eficacia probada.

## Regenerar desde la raíz

```powershell
python -m pip install --index-url https://pypi.org/simple --target .task_packages reportlab==5.0.1 pymupdf==1.28.2 python-pptx==1.0.2 pillow==12.3.0
python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_demo7.py
node 02_Prediccion_y_escenarios_de_riesgo/entrega/generar_caso.cjs
python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo7.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/generar_reporte.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/presentacion/generar_presentacion.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/verificar_entrega.py
```

La prueba de demo7 necesita Edge instalado y genera las capturas del reporte. Los generadores buscan dependencias en `.task_packages` y en las carpetas `.packages` locales. La presentación utiliza Segoe UI de Windows; el reporte emplea Arial si está disponible. El PDF de la presentación se dibuja con la misma composición, sin conversión nativa desde PowerPoint: esa revisión sigue pendiente.

## Cierre de entrega

Las bases publicadas fijan el envío del ZIP identificado por equipo y eje hasta el 31 de octubre de 2026 a las 23:59, a ambos correos oficiales. Incorporar las dos cartas con firmas reales y comprobar el acuse de registro y la elegibilidad. Detalles, enlaces y estado en la [revisión de requisitos](REVISION_REQUISITOS_INE.md). No se preparó ni envió un paquete oficial con esta revisión.

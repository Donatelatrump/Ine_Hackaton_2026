# Entrega técnica de Umbral

Actualización: 22 de octubre de 2026. Equipo aguas.exe, Reto 2: Predicción y escenarios de riesgo de abstención.

La [revisión de requisitos del INE](REVISION_REQUISITOS_INE.md) identifica la evidencia de cada requisito y los pendientes administrativos. Esta carpeta no acredita registro, elegibilidad, firmas ni envío oficial.

## Archivos de revisión

- [Reporte metodológico y preventivo PDF](reporte/Umbral_reporte_metodologico_preventivo.pdf): 14 páginas, variables, evaluación, semáforo y prevención.
- [Presentación PDF](presentacion/Umbral_presentacion.pdf) y [PPTX editable](presentacion/Umbral_presentacion.pptx): diez diapositivas.
- [Umbral](../demo/demo7.html) y [guía de ejecución](../demo/DEMO7.md): mapas sin/con acción, diferencias y exportación de distribución CSV.
- [Base histórica agregada](../datos_preparados/municipios_historico_con_calidad.csv), [proyecciones de los cuatro modelos](../modelado/salidas/comparacion_modelos/proyeccion_2027.csv) y [evaluación vigente](../modelado/salidas/comparacion_modelos/resultados.json).
- [Caso municipal](CASO_MUNICIPAL.md) y [guion de demostración](GUION_PRESENTACION.md).
- [Verificación de entrega](verificacion_unificacion.json) y [prueba de navegador de Umbral](../demo/verificacion/demo7/resultado.json).

El plan estatal usa cobertura inicial del 10% y efecto supuesto de 1.5 pp entre alcanzados, con variantes 0.3/3 pp. Son hipótesis del proyecto. El caso municipal SMS conserva el coeficiente externo de 0.30 pp; no debe confundirse con el plan estatal ni atribuirse a México como eficacia probada.

## Revisión documental del 22 de octubre

Se contrastaron los entregables técnicos con la convocatoria oficial vigente y los resultados del experimento existente. Las cartas de cesión y de decir verdad quedaron fuera del alcance de esta revisión.

- Presentación PDF/PPTX: diez diapositivas; se explicita el resultado top50 de 2024 (referencia 27/50 frente a 19/50 del modelo) y se actualizan el cierre y la referencia al guion de cuatro bloques.
- Reporte PDF: catorce páginas; se precisa `log(1 + LN)` y se distingue el uso predictivo de edad y urbanización de las tipologías explicativas posteriores.
- Caso municipal: instrucciones actualizadas a Umbral, separado del escenario estatal. Sus cifras se reprodujeron con `generar_caso.cjs`.
- Validación: cifras principales contrastadas con el benchmark, enlaces locales Markdown existentes, textos y tablas coincidentes entre PPTX y PDF, y comprobación de límites y superposiciones de los PDF. Se revisaron sus vistas renderizadas. Las huellas de la prueba de navegador existente corresponden a los recursos actuales; no se volvió a ejecutar el navegador ni a entrenar modelos.

El editable todavía requiere revisión de render dentro de PowerPoint. La comprobación del PDF y del contenido OOXML no sustituye esa revisión.

## Descargas y sección de acciones

El plan estatal mantiene su cálculo fijo (10% de cobertura y 1.5 pp de efecto supuesto). El simulador permite modificar acciones y su alcance, sin alterar ese cálculo estatal. Se retiró el editor de planes estatales alternativos.

La consulta CSV conserva 14 columnas del método seleccionado y la distribución CSV 19 columnas, sin los totales territoriales repetidos ni las recomendaciones del flujo anterior. La descarga Excel ofrece tablas con títulos, encabezados, bordes, filas alternadas, filtros y encabezados inmovilizados. Separa los datos municipales de las fuentes y supuestos en dos hojas. Las claves INE se guardan como texto y los resultados como números. El CSV conserva su función de intercambio de datos sin formato visual.

## Regenerar desde la raíz

```powershell
python -m pip install --index-url https://pypi.org/simple --target .task_packages reportlab==5.0.1 pymupdf==1.28.2 python-pptx==1.0.2 pillow==12.3.0
python umbral/tools/construir_demo7.py
node umbral/entrega/generar_caso.cjs
python umbral/demo/verificar_demo7.py
python umbral/entrega/reporte/generar_reporte.py
python umbral/entrega/presentacion/generar_presentacion.py
python umbral/entrega/verificar_entrega.py
```

La prueba de Umbral necesita Edge instalado y genera las capturas del reporte. Los generadores buscan dependencias en `.task_packages` y en las carpetas `.packages` locales. La presentación utiliza Segoe UI de Windows; el reporte emplea Arial si está disponible. El PDF de la presentación se dibuja con la misma composición, sin conversión nativa desde PowerPoint: esa revisión sigue pendiente.

## Cierre de entrega

Las bases publicadas fijan el envío del ZIP identificado por equipo y eje hasta el 31 de octubre de 2026 a las 23:59, a ambos correos oficiales. Incorporar las dos cartas con firmas reales y comprobar el acuse de registro y la elegibilidad. Detalles, enlaces y estado en la [revisión de requisitos](REVISION_REQUISITOS_INE.md). No se preparó ni envió un paquete oficial con esta revisión.

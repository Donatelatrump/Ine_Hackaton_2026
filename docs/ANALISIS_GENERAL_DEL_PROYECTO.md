# Estado vigente: Demo7 · 21 de octubre de 2026

La [revisión de requisitos del INE](../umbral/entrega/REVISION_REQUISITOS_INE.md) contrasta el Reto 2 con los archivos y pendientes. [Demo7](../umbral/demo/demo7.html) incorpora consulta territorial, planes estatales hipotéticos, mapas comparados y distribución exportable. Ver la [guía actual](../umbral/demo/DEMO7.md).

Se corrigieron los controles ocultos de cobertura, el recálculo al cambiar el catálogo, la descarga trazable de escenarios y los enlaces a resultados vigentes. Reporte de 14 páginas y presentación de 10 diapositivas regenerados para Demo7. Se conserva el experimento de cuatro modelos del 16 de octubre; no se reentrenó.

Las comprobaciones actuales están en `demo/verificacion/demo7/resultado.json` y `entrega/verificacion_unificacion.json`, dentro del track. Registro, elegibilidad, firmas, ZIP final y envío no están acreditados. Tampoco existe validación futura de 2027 ni eficacia causal demostrada del plan estatal.

El análisis siguiente corresponde a la reorganización anterior de demo6; sus fechas, rutas y pruebas describen esa etapa.

---

# Análisis general de Umbral

**Corte:** 16 de octubre de 2026. **Versión activa:** demo6.

## Estado del producto

Umbral es un prototipo de exploración electoral: mapa nacional, navegación por estados y municipios, antecedentes observados, comparación de cuatro regresores, exportación y contexto descriptivo estatal. La demo contiene 2,477 registros municipales y 1,783 estimaciones de 2027 del experimento seleccionado. Sin estimación no significa abstención cero.

La web consulta predicciones calculadas previamente; la rapidez de navegación no mide el tiempo de entrenamiento. La ficha estatal utiliza todos los registros de la entidad presentes en la demo, no solamente aquellos con predicción.

## Resultado metodológico vigente

| Modelo | MAE medio 2021/2024, pp | MAE ponderado medio, pp |
| --- | ---: | ---: |
| Ridge | 9.0094 | 5.2188 |
| **HistGradientBoosting** | **6.8360** | **4.6684** |
| LightGBM | 6.8304 | 4.8385 |
| CatBoost | 6.9089 | 4.6692 |

La selección favoreció HistGradientBoosting por menor error ponderado tras el empate práctico con LightGBM dentro de 0.05 pp. Ridge fue más rápido. La referencia obtiene más aciertos top50 que el ganador en 2024: menor MAE no significa superioridad en toda métrica. No existe una evaluación futura independiente para 2027.

La principal fortaleza es la trazabilidad: mismas variables y cohortes, cortes temporales, predicciones por municipio, modelo serializado, dependencias y hashes. No se reentrenó ni cambió ese experimento durante esta reorganización. Ver [resultados completos](../umbral/modelado/COMPARACION_4_MODELOS.md).

## Diagnóstico de mantenibilidad

| Hallazgo | Cambio aplicado o pendiente |
| --- | --- |
| Código actual mezclado con varias generaciones de demo | Código de demo6 en `src/demo6/`, organizado por responsabilidad |
| Controlador con resumen, gráfica y evidencia | Tres vistas separadas, con dependencias recibidas explícitamente |
| Capturas y copias anteriores junto a la página | 33 instantáneas y registros movidos a `demo/archivo/depuracion/` |
| CSS de ficha mezclado con estilos generales | Dos hojas en `styles/demo6/` |
| Documentos generales de etapas sucesivas | README actual y copias anteriores en `docs/archivo/` de la raíz |
| Falta de mapa de responsabilidades | Guías de arquitectura, contratos y registro de movimientos |
| Globales y redefiniciones de funciones | Estado encapsulado en el paquete y hooks explícitos; dependencias internas conservadas |
| Arranque por temporizadores | Dos sondeos eliminados; secuencia explícita y señal `umbral:ready` |
| Múltiples hojas CSS heredadas | Fuentes propias por responsabilidad y un paquete CSS; revisión de escritorio y móvil |

El inventario muestra puntos de concentración: `style.css` tiene 1,549 líneas, el motor anterior de capas tenía 524 y la aplicación heredada unos 59 KB antes de dividirse. El número de líneas no mide calidad por sí solo: varias funciones están comprimidas en líneas extensas.

## Organización y flujo

Los insumos originales alimentan auditoría y preparación. El histórico con calidad alimenta el experimento y su publicación en `demo/data/`. Otro generador publica las fichas descriptivas. La interfaz separa dominio de agregación, vistas, mapa, búsqueda y coordinación. Las funciones existentes de escenarios conservan compatibilidad dentro de `legacy/`. La aplicación anterior fue dividida y ya no existe como un único archivo.

Las fuentes compartidas, generadores, resultados congelados y entradas HTML mantienen sus rutas. Se preserva el orden explícito de carga: `datos_embebidos.js` aporta el contrato anterior; `comparacion_modelos.js` incorpora las salidas y metadatos del experimento vigente. Voto Vigía queda fuera de la reorganización.

El código de backend también tiene deuda: `ejecutar.py` realiza trabajo en nivel superior, por lo que importarlo puede iniciar cálculos y escrituras. Los generadores actuales deben ejecutarse por su comando, no importarse indiscriminadamente. Las herramientas nuevas de inventario y servidor no importan modelos y solo ejecutan su trabajo desde `main()`.

## Límites y riesgos

- Los límites municipales históricos no están armonizados y los cambios de catálogo pueden afectar comparaciones.
- Ponderar con SV+NV 2024 no equivale a proyectar el electorado de 2027.
- Población y estudios descriptivos no identifican motivos individuales de abstención ni efectos causales de intervenciones.
- Las fuentes revisadas no contienen 32 planes estatales validados. Los resultados nacionales o regionales no se atribuyen a municipios.
- Todavía no hay esquema tipado completo entre los productores de JSON y sus consumidores.
- El empaquetador raíz recorre todo salvo `.git`: antes del próximo paquete debe revisarse la exclusión de entornos y temporales. No se regeneró el ZIP.
- Los entregables PDF/PPT pueden requerir capturas nuevas para reflejar cambios posteriores de interfaz; no se regeneraron en este trabajo.

## Revisión realizada

Se inspeccionaron estructura, dependencias declaradas, rutas locales, responsabilidades y generadores. El inventario estático encuentra todos los scripts, estilos e imágenes declarados en `index.html`, `demo4.html`, `demo5.html` y `demo6.html` después de mover los archivos. Esto no acredita por sí solo el comportamiento en navegador.

La segunda etapa de reorganización pasó 29 pruebas de Node y las comprobaciones de navegador de demo6: navegación, históricos, métodos, agregaciones, exportaciones, ficha estatal, escenario existente y móvil, sin errores JavaScript. Se revisaron capturas. No se reentrenaron modelos.

## Próximos pasos técnicos

1. Continuar reduciendo dependencias léxicas internas con interfaces de componentes más pequeñas.
2. Mantener la secuencia de arranque y el contrato `umbral:ready`, ya implementados.
3. Formalizar y versionar el esquema de datos publicados.
4. Depurar selectores redundantes conservando la apariencia; el paquete y las fuentes propias ya están separados.
5. Revisar las exclusiones del empaquetador.

Son tareas pendientes, no cambios ya aplicados. Ver [arquitectura y comandos](../umbral/arquitectura/README.md).

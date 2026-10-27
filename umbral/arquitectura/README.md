# Arquitectura de Umbral

**Proyecto: Umbral. Equipo: Aguas.exe.**

`index.html`, en la raíz, abre `umbral/demo/demo7.html`. La aplicación carga datos y bibliotecas locales y consulta predicciones precalculadas; no requiere backend.

## Aplicación

`demo/build.demo7.config.json` establece el orden de los módulos de `src/demo7/`, los módulos compartidos de `src/demo6/` y sus estilos. `tools/construir_demo7.py` genera `demo/assets/demo7.js`, `demo7.css` y su manifiesto de huellas. Se conserva la denominación interna demo6 únicamente para los componentes compartidos; la entrada pública vigente es demo7.

`demo/data/` contiene los datos publicados y capas geográficas. `demo/vendor/` contiene Leaflet. Los documentos se resuelven desde `entrega/`, `modelado/` y `../../fuentes/` respecto de la aplicación.

## Reproducción

El análisis se conserva en `modelado/`, la preparación en `auditoria/` y `cartografia/`, y sus resultados en `datos_preparados/` y `modelado/salidas/`. La metodología y los archivos de dependencias describen su reproducción. Los documentos finales y sus generadores están en `entrega/`.

Consulta [los comandos de mantenimiento](../tools/README.md) y el [README principal](../../README.md).

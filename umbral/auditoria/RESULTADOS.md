# Resultado de auditor?a y preparaci?n municipal

Fecha: 5 de octubre de 2026. Alcance: seis bases CCPC y una referencia cartogr?fica del INE. Sin modelo predictivo entrenado.

## Resultado principal

Se revisaron 54,872,712 filas y se generaron 14,779 registros de municipio/a?o. Las 2,477 claves tienen pol?gono en la capa INE cob_2024, con metadatos de 9 de mayo de 2024.

Archivo recomendado: [municipios_historico_con_calidad.csv](../datos_preparados/municipios_historico_con_calidad.csv). Pol?gonos: [cartografia publicada](../demo/data/municipios.geojson). Diccionario y m?todo: [README](../datos_preparados/README.md).

## Cobertura anual

| A?o | Filas originales | Municipios | Entidades | LN | SV | NV | NS |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2,009 | 8,706,843 | 2,458 | 32 | 77,481,831 | 33,316,974 | 42,298,963 | 1,865,894 |
| 2,012 | 8,604,456 | 2,455 | 32 | 76,490,962 | 47,383,154 | 28,939,159 | 168,649 |
| 2,015 | 9,106,059 | 2,458 | 32 | 83,563,462 | 36,926,612 | 41,517,874 | 5,118,976 |
| 2,018 | 9,251,122 | 2,463 | 32 | 89,123,997 | 51,784,399 | 31,249,856 | 6,089,742 |
| 2,021 | 9,430,502 | 2,468 | 32 | 93,532,133 | 46,389,189 | 43,099,624 | 4,043,320 |
| 2,024 | 9,773,730 | 2,477 | 32 | 98,330,348 | 54,899,228 | 37,105,466 | 6,325,654 |

Los cuatro conteos sumados en la base municipal coinciden con los originales en cada a?o.

## Comprobaciones completas

- 192 CSV procesados con parser estricto y comillas expl?citas; ninguna fila omitida por errores de lectura.
- Cero n?meros inv?lidos en los campos de a?o, entidad, municipio, secci?n, sexo, edad y conteos utilizados para la agregaci?n.
- Cero conteos negativos, duplicados exactos y claves de desagregaci?n repetidas dentro de los archivos.
- Cero diferencias en LN = SV + NV + NS en las filas originales y agregadas.
- 32 entidades en cada a?o; claves de municipio/a?o ?nicas en la salida.
- Tasas verificadas contra sus conteos; denominadores cero conservados como tasas vac?as.
- Conciliaci?n independiente con el CSV completo de Aguascalientes 2024 usando el lector est?ndar de Python.
- Hashes SHA-256 de los ocho ZIP aportados coinciden con el inventario previo.
- GeoJSON reabierto: 2,477 claves ?nicas, geometr?as Polygon/MultiPolygon y cobertura del 100% de las claves de la base.

## Hallazgos que requieren tratamiento antes de modelar

- **73 registros municipales sin datos observados:** SV + NV = 0; no convertirlos en ceros ni entrenar con ellos como tasas reales.
- **1,891 registros con NS mayor de 10% de LN:** alerta exploratoria de calidad, no una regla oficial. Analizar sensibilidad y cobertura.
- **22 municipios sin los seis a?os:** conservarlos para visualizaci?n; no imputar historia a partir de municipios vecinos sin justificaci?n.
- **79 claves con nombres hist?ricos distintos:** revisar denominaciones, erratas y posibles cambios territoriales; no fusionar por nombre.
- **371 filas con edad superior a 120**, con aporte LN total de **373** repartido entre los seis a?os. El m?ximo observado es 140. Son conteos acumulados de registros, no personas ?nicas; se conservaron y marcaron.
- **44,154 registros con distrito federal vac?o o no num?rico** y **65,066 con distrito local vac?o o no num?rico**. Se observaron espacios en blanco como marcador. Ninguno de estos campos se us? para agrupar por municipio.

## Cartograf?a y comparabilidad

La capa descargada desde el portal de 2023 enlaza a cob_2022 y tiene metadatos 20220620. Se conserv? como referencia alternativa. La capa cob_2023 tiene metadatos 20230609 y 2,469 municipios: le faltan ocho claves observadas en 2024. La capa seleccionada cob_2024 tiene metadatos 20240509 y 2,477 municipios: cubre todas las claves observadas.

Fuente seleccionada: [portal INE](https://pautas.ine.mx/transparencia/mapas/index_2025.html) y [ZIP municipal](https://pautas.ine.mx/transparencia/mapas/cob_2024/MUNICIPIO.zip). Los metadatos y SHA-256 est?n en `../cartografia/metadatos_2024.json`.

La correspondencia se hizo por entidad y municipio INE, sin asumir claves INEGI. Los nombres se normalizaron solamente para detectar discrepancias, sin modificar los originales. Hay siete discrepancias nominales en 2024 y ninguna clave ausente. Ver `correspondencia_cartografia.csv`.

**La cobertura de claves no demuestra estabilidad de l?mites.** El GeoJSON sirve como referencia visual actual; los conteos hist?ricos siguen asociados a su marco original. No se armonizaron pol?gonos ni redistribuyeron electores. Tampoco se verific? validez topol?gica.

## Siguiente etapa t?cnica

Antes del modelo: definir una cohorte comparable para validaci?n temporal, tratar los municipios nuevos y los denominadores ausentes, realizar sensibilidad a no especificados y edades extremas, y documentar cambios territoriales relevantes. Una predicci?n municipal no debe presentarse como una explicaci?n causal.

## Evidencia y reproducci?n

`auditoria_archivos.csv/json`, `resumen_anual.csv/json`, `comparabilidad_municipal.csv`, `correspondencia_cartografia.csv` y `verificacion_final.json` contienen la evidencia. Los scripts y versiones est?n en esta carpeta; el orden de ejecuci?n se documenta en el README de datos preparados.

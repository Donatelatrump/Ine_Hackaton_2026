# Base nacional por municipio y año

Archivo recomendado: `municipios_historico_con_calidad.csv`. Incluye conteos, tasas y banderas de calidad. `municipios_historico.csv` conserva la agregación previa al cruce con la cartografía.

Ambos proceden únicamente de los seis ZIP CCPC históricos aportados por el usuario. Las modalidades adicionales no se concatenaron, porque sus esquemas y universos son diferentes. Los archivos originales permanecen intactos.

## Unidad y claves

Una fila por año, entidad INE y municipio INE. `clave_municipio_ine` concatena entidad de dos dígitos y municipio de tres dígitos; es una clave del proyecto basada en el INE, no una clave INEGI. Importar las claves como texto en Excel o en cualquier herramienta de análisis para conservar ceros iniciales.

El catálogo y GeoJSON de referencia visual están en `../cartografia/`, versión `cob_2024` del INE con metadatos de 9 de mayo de 2024. Las claves coinciden con todas las filas municipales; esto no implica igualdad de límites a través del tiempo. Los conteos históricos no se redistribuyeron a los límites de 2024.

## Columnas

| Campo | Significado |
|---|---|
| ano, tipo_eleccion | Año y clasificación intermedia/presidencial |
| entidad_ine, municipio_ine, clave_municipio_ine | Identificadores territoriales INE |
| entidad_nombre, municipio_nombre | Nombres presentes en los datos originales |
| filas_origen, variantes_nombre | Número de filas agregadas y nombres distintos dentro de municipio/año |
| ln | Suma de lista nominal de cuadernillos |
| sv, nv, ns | Sumas de registros con marca de voto, sin marca y no especificados |
| ln_18_29, ln_60_mas | Lista nominal agregada de 18–29 y de 60 años o más |
| ln_edad_mayor_120 | Lista nominal correspondiente a edades superiores a 120, conservada y señalada |
| ln_mujeres, ln_no_binario | Lista nominal por categorías SEXO=1 y SEXO=2 |
| ln_urbana, ln_rural, ln_mixta | Lista nominal por tipo de sección |
| participacion_pct | 100 × sv / (sv + nv) |
| abstencion_pct | 100 × nv / (sv + nv) |
| no_especificados_pct | 100 × ns / ln |
| observacion | Sin datos observados cuando sv + nv = 0 |
| estado_correspondencia_cartografia | Coincidencia de clave y nombre normalizado, o nombre pendiente de revisar |
| municipio_nombre_cartografia | Nombre de la capa cartográfica, sin sustituir el original |
| anos_disponibles, nombres_historicos_distintos | Cobertura y variaciones nominales por clave |
| cartografia_referencia | Versión de los polígonos usados en la comparación |
| alertas_calidad | Señales separadas por punto y coma; no son un semáforo de riesgo |

## Reglas y límites

- Los conteos se sumaron antes de calcular porcentajes. No se promediaron tasas de secciones.
- Las tasas vacías corresponden a denominador cero; no representan participación o abstención de cero.
- El umbral de no especificados mayor de 10% es una alerta exploratoria elegida para revisar calidad, no un criterio oficial ni una exclusión automática.
- Las edades superiores a 120 no se corrigieron ni eliminaron. Su aporte debe someterse a sensibilidad antes de construir predictores de composición etaria.
- El conteo no binario cero antes de 2024 refleja que esa categoría no existe en las bases previas; no demuestra ausencia de población no binaria.
- Los nombres con errores tipográficos o abreviaturas permanecen visibles. No se realizaron correspondencias territoriales por similitud de nombres.
- El campo distrito local contiene registros vacíos; no se usó para identificar municipios ni calcular tasas.
- La identidad LN = SV + NV + NS y la conservación anual de los cuatro conteos están verificadas. El universo es el de los cuadernillos documentados por CCPC, no todos los votos de los cómputos electorales.
- No se evaluó la validez topológica de los polígonos ni se armonizaron límites históricos. La base es adecuada para exploración y para diseñar la evaluación; el modelado exige tratar estas limitaciones.

## Reproducir

Dependencias en `../auditoria/requirements.txt`. Desde el workspace:

```powershell
python .\02_Prediccion_y_escenarios_de_riesgo\auditoria\procesar_ccpc.py
python .\02_Prediccion_y_escenarios_de_riesgo\cartografia\preparar_cartografia.py 2024
python .\02_Prediccion_y_escenarios_de_riesgo\auditoria\finalizar_revision.py
```

La última etapa verifica tasas, unicidad municipal, conservación de originales y una conciliación independiente del CSV completo de Aguascalientes 2024. Ver `../auditoria/verificacion_final.json` y `../auditoria/RESULTADOS.md`.

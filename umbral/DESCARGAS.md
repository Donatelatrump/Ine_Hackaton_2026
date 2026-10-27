# Descargas pendientes

**Estado actual:** las bases aportadas ya se auditaron y agregaron por municipio. La cartografía INE ya se descargó y convirtió a GeoJSON; cubre todas las claves presentes. Permanece pendiente la armonización territorial histórica para modelar. Ver [resultado completo](auditoria/RESULTADOS.md). Los bloques siguientes son antecedentes del proceso de descarga.

**Actualización:** el usuario ya aportó los seis ZIP históricos, dos ZIP de modalidades adicionales y cuatro PDF. Los ocho ZIP pasaron la verificación CRC. Ver [revisión inicial](auditoria/REVISION_INICIAL.md). Permanece pendiente conseguir cartografía compatible y auditar/agregar los datos. Los fallos y pasos siguientes corresponden al intento anterior y se conservan como referencia.

Estado comprobado el 5 de octubre de 2026: 0/4 PDF descargados; bases y cartografía sin descargar. El entorno rechaza conexiones salientes con WinError 10013. Este documento y las fichas son material elaborado localmente, no copias de archivos descargados del INE.

## Documentos oficiales

Desde una terminal con acceso a Internet, ubicada en esta carpeta:

```powershell
python .\descargar_documentos.py
```

El script usa los enlaces de `fuentes.json`, verifica la cabecera PDF, conserva los archivos existentes y registra tamaño, SHA-256 y estado. Guarda los archivos en `documentos_oficiales/`. La comprobación de cabecera no sustituye revisar que el PDF abra y corresponda al documento esperado.

## Bases históricas

Abrir [CCPC del INE](https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/) y revisar los materiales por año: 2009, 2012, 2015, 2018, 2021, 2024. Los destinos de estos enlaces no se pudieron resolver con la herramienta web, por lo que no se inventaron URLs ni nombres de archivos.

Si los materiales anuales no ofrecen una tabla territorial comparable, revisar la exportación del tablero. El [manual](https://ine.mx/wp-content/uploads/2025/06/Manual-Conteos-Censales-2009-2024.pdf), página 7, documenta descargas de datos y de tabla cruzada CSV/XLSX.

Para el proyecto nacional:

1. Seleccionar elecciones federales CCPC 2009–2024.
2. Seleccionar nivel municipio y todos los estados; documentar filtros activos.
3. Exportar conteos generales y, cuando sea posible, desagregaciones agregadas por edad, sexo y tipo de sección. Confirmar los campos antes de dar la extracción por completa.
4. Obtener diccionarios y notas metodológicas. Documentar denominadores, faltantes y cambios territoriales.
5. Guardar cada original junto a su URL y fecha. Comprobar que no sea una exportación parcial o limitada a los elementos visibles.
6. Conseguir geometrías oficiales compatibles. Su URL de descarga aún no está identificada.

La cartografía de referencia indicada por el portal CCPC tiene corte a mayo de 2023. Verificar compatibilidad antes de unir datos y polígonos. El portal también contiene información judicial 2024–2025; el alcance de este proyecto es la serie federal 2009–2024.

No existe todavía una base lista para entrenar. La integración y el modelo empiezan después de obtener y auditar los archivos reales.

# Revisión inicial de archivos locales

**Actualización:** esta revisión inicial ya fue ampliada con la auditoría completa, agregación municipal y descarga de cartografía. El estado actual está en [RESULTADOS.md](RESULTADOS.md). La lista de pendientes de este documento es histórica.

Fecha: 2026-10-05. Archivos aportados manualmente por el usuario.

## Resultado comprobado

- Seis ZIP principales: 2009, 2012, 2015, 2018, 2021 y 2024.
- Cada ZIP principal contiene 32 CSV y un diccionario: 192 CSV históricos en total.
- Dos ZIP adicionales: prisión preventiva 2024 y voto anticipado 2024; un CSV y un diccionario por modalidad.
- Los ocho ZIP pasaron la comprobación CRC de todos sus miembros mediante `ZipFile.testzip()`.
- Cuatro archivos PDF presentes con cabecera PDF válida. No se verificó su renderizado ni todas sus páginas.
- Inventario con tamaños, esquemas y SHA-256 en `inventario_local.json`.
- Diccionarios extraídos en `diccionarios/`, conservando sus bytes originales.

Los seis años comparten estos 16 campos:

`AELEC, FELECCION, EDOCVE, EDONOM, MPIOCVE, MPIONOM, SECCION, TIPOSEC, DEF, DEL, SEXO, EDAD, LN, SV, NV, NS`.

Hay aproximadamente 3.73 GB descomprimidos en los seis ZIP principales. Se conservaron comprimidos; no es necesario duplicar todos los CSV para inspeccionarlos o procesarlos por flujo.

## Implicaciones para el proyecto

Los datos principales permiten plantear una agregación por año, entidad y municipio con los conteos LN, SV, NV y NS. Los registros observados son conteos desagregados por sección, edad y sexo; no son una tabla municipal ya preparada.

Los diccionarios definen las claves municipales como claves INE. No se debe asumir que corresponden directamente a claves INEGI ni construir un GEOID para cartografía sin verificar la equivalencia.

Los diccionarios 2009 y 2024 describen referencias distritales diferentes (DERFE 2021 y DERFE 2023, respectivamente). Aunque nuestro nivel sea municipio, falta auditar la comparabilidad territorial de cada año.

El diccionario de 2024 incorpora sexo 2, no binario. Debe conservarse su aporte al total y no tratar su ausencia histórica como dato faltante equivalente.

Los diccionarios indican que la fuente son los cuadernillos de lista nominal y que no se contempla casilla especial ni voto desde el extranjero. Esto limita la interpretación del universo; no deben confundirse estos conteos con los cómputos electorales.

Los archivos de voto anticipado y prisión preventiva presentan otros esquemas. Se conservaron en el inventario; no se deben concatenar con los seis años principales sin una metodología específica.

## Pendiente

1. Auditoría completa de filas: tipos, años, estados, municipios, duplicados, faltantes y valores negativos.
2. Verificar la relación LN = SV + NV + NS, documentando cualquier excepción antes de calcular tasas.
3. Agregar conteos por municipio, comprobar conservación de totales y generar tasas con denominadores documentados.
4. Comparar claves/nombres y cobertura municipal entre años. Determinar correspondencias territoriales verificables.
5. Obtener cartografía oficial compatible; no hay archivos SHP, GeoJSON o GPKG en el inventario actual.

Esta revisión confirma integridad de los contenedores y uniformidad de cabeceras. Todavía no acredita calidad estadística completa, equivalencia territorial ni disponibilidad de una base lista para modelar.

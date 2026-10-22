# Revisión de requisitos del INE — Umbral

Revisión del 21 de octubre de 2026. Eje elegido: **Reto 2, Predicción y escenarios de riesgo de abstención**. Referencias contrastadas: [micrositio oficial](https://ine.mx/hackathon-2026/), [convocatoria oficial](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf) y [copia del proyecto](../documentos_oficiales/Convocatoria_Hackaton-1.pdf). Los números de página siguientes son los del PDF, empezando en 1.

La revisión técnica no acredita una candidatura aceptada. Hay productos técnicos y pendientes administrativos que solo el equipo puede acreditar. No se deduce elegibilidad ni paridad a partir de nombres o fotografías.

Actualización documental del 22 de octubre: se volvió a consultar la convocatoria y se revisaron reporte, presentación, guion y caso municipal contra los resultados vigentes. El detalle y las comprobaciones están en el [registro de revisión técnica](README.md#revisión-documental-del-22-de-octubre). Las dos cartas quedaron excluidas por instrucción del equipo; las referencias administrativas de esta matriz se conservan como antecedente de la revisión del día 21.

## Requisito y evidencia concreta

| Requisito | Evidencia en el proyecto | Estado y alcance |
|---|---|---|
| Un solo eje y datos CCPC 2009–2024 (pp. 2–3) | [Base histórica](../datos_preparados/municipios_historico_con_calidad.csv), [metodología](../modelado/METODOLOGIA.md) | Implementado para Reto 2; perfiles y comunicación apoyan ese eje. |
| Modelo con historia y variables sociodemográficas agregadas (p. 3) | 15 variables, entre ellas edad y urbanización; [protocolo](../modelado/PROTOCOLO_COMPARACION_4_MODELOS.md), [comparación](../modelado/COMPARACION_4_MODELOS.md) | Cuatro regresores y referencia. Selección retrospectiva, sin validación futura. No se alteraron ni reentrenaron modelos en esta revisión. |
| Escenarios sin/con intervención hipotética (p. 3) | [Umbral](../demo/demo7.html), plan estatal y simulador internacional | Mapas pareados, diferencia en pp y cobertura editable. Efecto estatal explícitamente supuesto; no prueba eficacia institucional. |
| Riesgo territorial interpretable (pp. 3–4) | Semáforo en mapas y CSV; reporte, sección 5 | Tercios nacionales por método, umbrales fijos entre escenarios y categoría sin estimación. |
| Prevención y priorización de recursos (pp. 3–4) | [Planes estatales](../../docs/PLANES_ACCION_ESTATALES_PARTICIPACION.md), [caso municipal](CASO_MUNICIPAL.md), distribución y ficha | Actores propuestos, actividades, indicadores y horizonte; capacidad en personas. Costos, atribuciones y efectividad requieren validación. |
| Reporte PDF de 10–15 cuartillas (p. 4) | [Reporte de 14 páginas](reporte/Umbral_reporte_metodologico_preventivo.pdf) | Sincronizado con Umbral: variables, evaluación, semáforo, escenarios y prevención. Se interpreta una cuartilla como una página carta; la convocatoria no define la unidad ni exige la tipografía del Reto 1 para Reto 2. |
| Mapa ejecutable y base CSV/XLSX agregada (pp. 4–5) | [HTML ejecutable local](../demo/demo7.html), [GeoJSON](../demo/data/municipios.geojson), [CSV histórico](../datos_preparados/municipios_historico_con_calidad.csv), [CSV de proyecciones](../modelado/salidas/comparacion_modelos/proyeccion_2027.csv) | Disponibles localmente; el CSV descargado desde la distribución añade ambos escenarios, semáforo, modelo, denominador y fuente. Mantener la estructura del proyecto. |
| Presentación de hasta 10 diapositivas (p. 4) | [PDF](presentacion/Umbral_presentacion.pdf), [PPTX editable](presentacion/Umbral_presentacion.pptx) | Diez diapositivas, actualizadas con plan y semáforo de Umbral. PDF generado directamente; render nativo de PowerPoint pendiente. |
| Código o repositorio (p. 4) | [Repositorio](https://github.com/Donatelatrump/Ine_Hackaton_2026), [guía de ejecución](../demo/DEMO7.md) | Código local y generadores disponibles. Esta revisión no publica cambios en el repositorio remoto. |
| Dos cartas firmadas por todos los integrantes (p. 4) | [Cesión](../documentos_oficiales/Carta-de-cesion-de-derechos_Hackaton-1.pdf), [declaratoria](../documentos_oficiales/Carta-declaratoria-de-decir-la-verdad_Hackaton.pdf) | Formatos disponibles; no se acreditan firmas. La cesión también se anexa al registro según p. 6. |
| Registro y elegibilidad (pp. 1, 4) | No consta acreditación en la entrega revisada | Verificar acuse, integrantes y requisitos con la organización. El plazo publicado de registro terminó el 15 de octubre. |
| ZIP identificado por equipo y eje, envío a ambos correos antes del límite (p. 5) | Archivos técnicos revisados; empaquetador general existente | Paquete final con cartas y envío no acreditados. Fecha publicada: 31 de octubre de 2026, 23:59. Destinatarios: `grecia.castro@ine.mx` y `cirse.rodriguez@ine.mx`. No se ha enviado correo. |

## Cambios de esta revisión

- Entradas, guía y servidor orientados a Umbral; conserva `--demo 6` para consultar la versión anterior.
- Descargas locales de base, proyecciones y evaluación vigente. Se retiran enlaces que presentaban el experimento anterior como resultado del actual.
- Distribución CSV con tasas antes/después, semáforo y umbrales, método, acción, fuente, denominador y supuestos, incluso para municipios pendientes y sin estimación.
- Supuesto del plan estatal visible junto al resultado: 10% de cobertura y 1.5 pp entre alcanzados, con sensibilidad 0.3/3 pp. No se suman efectos de actividades superpuestas.
- Reporte, presentación y guion alineados con Umbral. Verificador de entrega actualizado para usar el modelo y caso vigentes, sin reutilizar una comprobación de navegador antigua.

## Correspondencia con los cinco criterios de evaluación

| Criterio oficial (p. 5) | Evidencia que puede valorar el comité | Límite o siguiente paso |
|---|---|---|
| Apego a la temática | CCPC, proyección territorial, escenarios y prevención del Reto 2 | No presentar perfiles como inscripción adicional al Reto 1. |
| Claridad y solidez | Cortes temporales, comparación con referencia, errores, fuentes, exclusiones y denominadores | Pocos ciclos y sin validación prospectiva; en top50 de 2024 la referencia supera al modelo seleccionado. |
| Originalidad y creatividad | Consulta territorial integrada con plan estatal, comparación de mapas, distribución y ficha exportable | Es una descripción del aporte; no acredita que sea una idea inédita. |
| Viabilidad de aprovechamiento institucional | Funcionamiento local, recursos por personas y responsables/indicadores propuestos | Acordar flujo, atribuciones, sedes, capacidad y costos reales con el área usuaria. |
| Potencial de aplicación institucional | Piloto propuesto con seguimiento y evaluación previa a ampliación | Sin adopción confirmada, impacto causal ni beneficio monetario demostrado. |

## Pendientes que requieren al equipo

1. Acreditar registro oportuno y requisitos: equipo paritario de 2–4 personas, edad 18–35 al cierre, nacionalidad y residencia, credencial vigente, ausencia de incompatibilidades y representante con cuenta bancaria mexicana a su nombre. No subir documentos personales al repositorio público.
2. Incorporar las dos cartas con las firmas reales de todas las personas integrantes. Revisar autoría y atribuciones de recursos de terceros; los datos y bibliotecas conservan sus avisos y licencias.
3. Preparar el ZIP final con nombre de equipo y eje, abrirlo en otra computadora y revisar todas las descargas. El empaquetador general recorre el workspace: no usarlo como acreditación de una entrega oficial revisada ni incluir dependencias, temporales o información privada sin revisión.
4. Enviar el paquete completo a ambos destinatarios dentro del plazo y conservar acuse. Las bases señalan que faltar un entregable obligatorio causa descalificación; disponer de la demo no sustituye el trámite.

## Evidencia de comprobación

[Prueba de Umbral](../demo/verificacion/demo7/resultado.json), [verificación de entrega](verificacion_unificacion.json), [guía de reproducción](../demo/DEMO7.md). Las huellas de archivos permiten comprobar que el resultado corresponde a los recursos revisados. Ninguna de estas verificaciones prueba la precisión de 2027 ni el efecto causal de una acción.

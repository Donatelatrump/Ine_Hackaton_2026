# Umbral: demo local

## Recorrido de la página (6 de octubre)

1. **Explora el territorio:** entidad, municipio y criterio de prioridad. Método, catálogo y estabilidad mínima están en opciones avanzadas. La escala, acción y cobertura total se definen en el paso 3.
2. **Revisa las prioridades:** mapa y lista junto a la ficha. Se distinguen el dato observado 2024, la estimación exploratoria 2027 y el escenario hipotético. La ficha resume motivos, revisión necesaria y acción; el detalle técnico se despliega.
3. **Explora una intervención:** selecciona sin intervención, SMS (Suecia o Estados Unidos), llamada para elaborar un plan de votación o escenario personalizado. Consulta cita original, estimador, cobertura e incertidumbre. Compara tasas antes/después y descarga el escenario con sus fuentes. Un cambio pequeño puede mantener el color del mapa.

La evidencia completa, el resumen del plan y la frontera están en desplegables; el resultado adverso de 2024 permanece visible.

**Sin estimación:** municipio gris con antecedentes insuficientes, tasa no calculable o NS sobre el 10% en algún antecedente requerido. No significa abstención cero ni riesgo bajo. No recibe puesto predictivo ni intervención simulada. La ficha muestra su causa y propone revisar datos; el contador y listado respetan el filtro actual. Son 694 en el universo nacional; el filtro inicial de catálogo deja 478. Estas exclusiones pueden apartar territorios con necesidad alta.

En capacidad por personas, la estabilidad y la frontera comparan top N entre variantes, con N igual al número de municipios del plan. No recalculan el presupuesto humano para cada variante. El filtro mínimo usa N previo al filtro; ficha y frontera usan N final.

**Versión corregida:** abre con doble clic en `index.html`, sin Python ni internet para datos/librerías. Mantener carpeta completa; usa datos JS incrustados. Capas Base/Intervención/Δ, lentes, estabilidad, fichas y entidad. Escenario con SV+NV 2024, NS fuera. **Cobertura total y distribución (paso 3)** por prioridad o proporcional, con estabilidad mínima como filtro avanzado; **ficha «¿Por qué este municipio?»** con razones, robustez, acuerdo de métodos, perfil CCPC, acción e hipótesis; **frontera de decisión** (núcleo 6/6, zona de revisión, fuera). [Correcciones](../CORRECCIONES_Y_ESTADO.md).

Desde la raíz `Ine_Hackaton`:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener la terminal activa. Detener con Ctrl+C. El servidor es opcional en esta versión.

Seleccionar entidad, buscar por nombre/clave y revisar el filtro de catálogo constante. En el paso 1: criterio de prioridad y estabilidad mínima. En el paso 3: seleccionar acción y cobertura; solo el modo personalizado usa respuesta supuesta. Mapa y plan se actualizan. Las filas y municipios abren la ficha explicativa y el perfil CCPC. Descargar plan exporta toda la selección con la fuente de la acción, incluso si la tabla solo muestra 25.

La vista inicial conserva el filtro de entidades con catálogo constante: 1,144 estimaciones. Al desmarcarlo se muestran 1,783 estimaciones nacionales. Permanecen visibles los municipios sin estimación y los territorios fuera del filtro se atenúan. Cartografía simplificada exclusivamente para visualización, sin teselas ni librerías remotas. Los enlaces oficiales del pie requieren internet si se abren.

Proyección 2027 exploratoria; 2024 adverso visible. SV+NV 2024 define tasas y limita alcance, NS fuera, no electorado proyectado. La **estabilidad de prioridad** es la frecuencia con que un municipio entra en la selección entre las seis variantes de método y calidad; no es probabilidad calibrada. El perfil CCPC por edad, sexo y tipo de sección es una **capa explicativa** calculada de los conteos crudos: no alimenta al modelo y no implica causalidad. El rango ±21.05 pp se conserva solo como error histórico.

### Acciones con fuentes verificadas

El paso 3 permite elegir municipio, estado o México. La cobertura introducida es **un total para el territorio**, no un alcance repetido en cada municipio. Se distribuye por prioridad o proporcionalmente a SV+NV 2024 hasta agotar capacidad o población observable; los municipios sin estimación no reciben asignación. Los controles anteriores de capacidad por municipio quedan ocultos porque este flujo usa personas totales. Elegir territorio sincroniza el buscador; elegir un estado o municipio desde el buscador también sincroniza la escala de simulación.

La comparación principal usa toda la población observable de los municipios estimables del territorio bajo los filtros activos, incluidos los no atendidos; su abstención permanece base. El resumen del plan conserva el promedio específico de municipios atendidos y lo identifica. La descarga de lectura contiene escala, territorio, cobertura y denominador del agregado territorial. El filtro de catálogo puede excluir territorios incluso en México; se informa en el resumen y puede desactivarse.

En SMS, la pregunta visible es «¿A cuántas personas planeas enviar el SMS en total?». Se cuentan personas distintas previstas para envío, no cantidad de mensajes o lectores. El término ITT se conserva en la evidencia y exportación porque identifica el estimador publicado. En la llamada se cuentan conversaciones efectivamente completadas. La capacidad operativa la proporciona el usuario: CCPC no permite inferirla.

La página abre sin intervención. El catálogo y sus citas están en `decision.js`; los coeficientes permanecen fijos. Las referencias y localizadores se detallan en [EVIDENCIA_INTERVENCIONES.md](../modelado/EVIDENCIA_INTERVENCIONES.md). No son una calibración para México ni una recomendación automática de campaña.

Con evidencia: votos adicionales = cobertura × efecto publicado en pp / 100, limitado por los abstencionistas esperados en esa cobertura (cobertura × tasa municipal / 100). Reducción municipal = 100 × votos adicionales / (SV+NV 2024). La tasa municipal entre cubiertos es un supuesto; la pertinencia de población, canal, contenido y contexto requiere revisión. SMS usa personas asignadas (ITT), no lectores efectivos; la llamada usa contactos efectivos (ATT), no intentos. No se suman efectos indirectos ni acciones.

Para SMS se trasladan aritméticamente los límites publicados usando el mismo efecto para todos los municipios; el rango agregado no supone efectos independientes. No incluye incertidumbre del predictor ni de transferencia a México. La llamada informa su error estándar publicado sin inventar un intervalo. El modo personalizado conserva la fórmula previa de respuesta entre abstencionistas y se identifica sin fuente causal. Las recomendaciones preventivas por perfil se distinguen de la acción que realmente se simuló.

La descarga municipal y su archivo de lectura incluyen acción, unidad, estimador, efecto, cita, DOI, incertidumbre y límites. Los votos esperados se exportan con decimales. Pruebas: `node --test demo/decision.test.cjs demo/intervenciones.test.cjs` desde la carpeta del track; `python demo/verificar_intervenciones.py` verifica apertura local, controles, CSV, presupuesto y vista móvil con Edge y Playwright en `.task_packages`.

Pruebas vigentes de navegador: `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py` ejecuta el verificador actual y regenera las capturas, sin servidor. Requiere Playwright y Edge; dependencias en `.task_packages`. `verificar_intervenciones.py` comprueba los controles y CSV; `capturar_demo.py` guarda imágenes y configuración en `verificacion/`. Node ejecuta 21 pruebas con `decision.test.cjs` e `intervenciones.test.cjs`. Leaflet 1.9.4 conserva su licencia en `vendor/LICENSE`.

Entrega unificada el 6 de octubre de 2026: [caso municipal](../entrega/CASO_MUNICIPAL.md) y [guion de presentación](../entrega/GUION_PRESENTACION.md). Estabilidad de selección es frecuencia descriptiva; las variantes comparten datos y pueden equivocarse juntas.

### Vista por estados

El mapa nacional muestra las 32 entidades. Al pulsar un estado se abren sus municipios; al pulsar un municipio se acerca y resalta. El clic derecho vuelve un nivel y Vista nacional regresa directamente a México. Los resúmenes estatales respetan los filtros y ponderan las tasas por SV+NV 2024 de municipios con estimación; los faltantes no cuentan como cero. La frecuencia de selección está disponible en la vista municipal.

`data/estados.js` conserva la cartografía local. Para regenerarla: instalar Shapely y ejecutar `python data/generar_estados.py` desde la carpeta demo. Los límites derivan de los municipios simplificados y son solo referencia visual.

### Distribución y alcance de datos

Prioridad concentra la cobertura por ranking y puede asignarla entera a un municipio. Proporcional reparte entre los elegibles según SV+NV 2024; el método de mayor resto conserva el total entero y desempata por clave. No se busca maximizar efecto causal ni se demuestra superioridad de una distribución. El filtro mínimo de estabilidad restringe el conjunto antes de distribuir.

La etiqueta nacional es «México: municipios con estimación incluidos». El resumen muestra el total del catálogo, municipios estimables incluidos, sin estimación dentro del filtro y excluidos. No extrapola el promedio a los territorios ausentes. La misma cobertura y selección permanecen fijas entre Base, Intervención y Diferencia.

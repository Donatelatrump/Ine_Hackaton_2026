# Umbral: demo local

## Recorrido de la página (6 de octubre)

1. **Define tu capacidad:** entidad, búsqueda, capacidad por municipios o personas y objetivo. Método, catálogo y estabilidad mínima están en «Ajustar método y calidad de datos».
2. **Revisa las prioridades:** mapa y lista junto a la ficha. Se distinguen el dato observado 2024, la estimación exploratoria 2027 y el escenario hipotético. La ficha resume motivos, revisión necesaria y acción; el detalle técnico se despliega.
3. **Explora una intervención:** alcance y respuesta supuestos, tasas antes/después, reducción en puntos porcentuales y descarga. Un cambio pequeño puede mantener el color del mapa.

La evidencia completa, el resumen del plan y la frontera están en desplegables; el resultado adverso de 2024 permanece visible.

**Sin estimación:** municipio gris con antecedentes insuficientes, tasa no calculable o NS sobre el 10% en algún antecedente requerido. No significa abstención cero ni riesgo bajo. No recibe puesto predictivo ni intervención simulada. La ficha muestra su causa y propone revisar datos; el contador y listado respetan el filtro actual. Son 694 en el universo nacional; el filtro inicial de catálogo deja 478. Estas exclusiones pueden apartar territorios con necesidad alta.

En capacidad por personas, la estabilidad y la frontera comparan top N entre variantes, con N igual al número de municipios del plan. No recalculan el presupuesto humano para cada variante. El filtro mínimo usa N previo al filtro; ficha y frontera usan N final.

**Versión corregida:** abre con doble clic en `index.html`, sin Python ni internet para datos/librerías. Mantener carpeta completa; usa datos JS incrustados. Capas Base/Intervención/Δ, lentes, estabilidad, fichas y entidad. Escenario con SV+NV 2024, NS fuera. **Capacidad territorial o humana (paso 1)** con capacidad territorial o humana y estabilidad mínima; **ficha «¿Por qué este municipio?»** con razones, robustez, acuerdo de métodos, perfil CCPC, acción e hipótesis; **frontera de decisión** (núcleo 6/6, zona de revisión, fuera). [Correcciones](../CORRECCIONES_Y_ESTADO.md).

Desde la raíz `Ine_Hackaton`:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener la terminal activa. Detener con Ctrl+C. El servidor es opcional en esta versión.

Seleccionar entidad, buscar por nombre/clave y revisar el filtro de catálogo constante. En el paso 1: capacidad por municipios o por personas alcanzables, criterio de prioridad y estabilidad mínima; el plan sugerido resume selección, entidades, base observable, núcleo robusto, casos por revisar y escenario. Ajustar alcance y respuesta supuesta; mapa y plan se actualizan. Las filas y municipios abren la ficha explicativa y el perfil CCPC. Descargar plan exporta toda la selección, incluso si la tabla solo muestra 25.

La vista inicial conserva el filtro de entidades con catálogo constante: 1,144 estimaciones. Al desmarcarlo se muestran 1,783 estimaciones nacionales. Permanecen visibles los municipios sin estimación y los territorios fuera del filtro se atenúan. Cartografía simplificada exclusivamente para visualización, sin teselas ni librerías remotas. Los enlaces oficiales del pie requieren internet si se abren.

Proyección 2027 exploratoria; 2024 adverso visible. SV+NV 2024 define tasas y limita alcance, NS fuera, no electorado proyectado. La **estabilidad de prioridad** es la frecuencia con que un municipio entra en la selección entre las seis variantes de método y calidad; no es probabilidad calibrada. El perfil CCPC por edad, sexo y tipo de sección es una **capa explicativa** calculada de los conteos crudos: no alimenta al modelo y no implica causalidad. El rango ±21.05 pp se conserva solo como error histórico.

Pruebas del navegador: instalar `playwright==1.63.0` en `.task_packages` y ejecutar `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py` con servidor activo. Usa Edge instalado en su ruta estándar de Windows; capturas y resultado se guardan en `verificacion/`. Son 28 comprobaciones, incluida apertura `file://`. Node prueba escenario, estabilidad, capacidad humana y frontera sin navegador (12 pruebas). Leaflet: 1.9.4, licencia incluida en `vendor/LICENSE`. Datos de la demo: `resultados.json`, `evaluacion_adicional.json`, `perfil_demografico.json` y geometría simplificada, todo incrustado en `data/datos_embebidos.js`.

Entrega unificada el 6 de octubre de 2026: [caso municipal](../entrega/CASO_MUNICIPAL.md) y [guion de presentación](../entrega/GUION_PRESENTACION.md). Estabilidad de selección es frecuencia descriptiva; las variantes comparten datos y pueden equivocarse juntas.

### Vista por estados

El mapa nacional muestra las 32 entidades. Al pulsar un estado se abren sus municipios; al pulsar un municipio se acerca y resalta. El clic derecho vuelve un nivel y Vista nacional regresa directamente a México. Los resúmenes estatales respetan los filtros y ponderan las tasas por SV+NV 2024 de municipios con estimación; los faltantes no cuentan como cero. La frecuencia de selección está disponible en la vista municipal.

`data/estados.js` conserva la cartografía local. Para regenerarla: instalar Shapely y ejecutar `python data/generar_estados.py` desde la carpeta demo. Los límites derivan de los municipios simplificados y son solo referencia visual.

# Umbral Demo7

Versión revisada el 21 de octubre de 2026 para el **Reto 2: Predicción y escenarios de riesgo de abstención**. [Revisión de requisitos y pendientes](../entrega/REVISION_REQUISITOS_INE.md).

## Abrir y reconstruir

Desde la raíz del repositorio:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py --build
```

Abrir [demo7 local](http://127.0.0.1:8000/02_Prediccion_y_escenarios_de_riesgo/demo/demo7.html). También funciona abriendo `demo7.html` directamente: datos y Leaflet son locales. Conservar la estructura del proyecto para abrir PDF, CSV y fuentes relativas. Solo los enlaces externos requieren internet. `--demo 6` conserva la entrada anterior.

Solo reconstruir:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_demo7.py
```

Editar `src/demo7/`, `styles/demo7.css` y `demo7.html`. El orden de fuentes está en `build.demo7.config.json`; parte del motor procede de `src/demo6/` y `styles/demo6/`. No editar manualmente `assets/demo7.js`, `assets/demo7.css` ni los datos generados. Cambiar una fuente compartida exige revisar ambas versiones.

## Recorrido

1. Elegir estado, municipio, año y método. Las elecciones 2009–2024 son observadas; 2027 es exploratoria. HistGradientBoosting es el método inicial. El gris representa datos insuficientes, no abstención cero.
2. Consultar antecedentes, perfil agregado, errores retrospectivos y comparación de modelos. Los dos cortes 2021/2024 participaron en la selección; no validan 2027. MAE medio del modelo seleccionado: 6.8360 pp. En top50 de 2024 la referencia acierta 27 y el seleccionado 19.
3. Con un estado seleccionado, abrir el plan propuesto. El escenario inicial supone cobertura del 10% y efecto de 1.5 pp entre alcanzados; variantes conservadora/optimista: 0.3/3 pp. Los coeficientes son supuestos del proyecto, no eficacia comprobada del plan. Se aplica un único efecto sobre una población compartida, sin sumar actividades. Las estrategias internacionales conservan su propia fuente y estimador.
4. Comparar mapas sin/con intervención; usar diferencias para cambios pequeños. El semáforo usa tercios nacionales de las tasas del método activo: bajo < corte inferior, medio desde el inferior y < superior, alto ≥ superior. Los cortes se conservan entre escenarios y no son umbrales oficiales ni probabilidades calibradas.
5. Descargar la distribución CSV completa, aunque la tabla esté filtrada o paginada, y la ficha imprimible. En Documentos están el reporte, la presentación, la base histórica, la proyección de los cuatro modelos, la evaluación vigente y el código.

«Ver un caso de ejemplo» prepara la clave histórica 23008 y 1,000 SMS; conserva el método elegido. «Recorrido para presentar» elige HistGradientBoosting y guía cinco pasos, con cierre mediante botón o Escape. La ficha descargada es un HTML autónomo imprimible que resume los primeros cinco municipios atendidos; el CSV contiene la distribución completa. Las tres vistas de mapa sincronizan el encuadre. Las órbitas de portada se pueden pausar y respetan movimiento reducido.

## Datos y exportaciones

La abstención es `100 × NV / (SV + NV)`. El denominador del escenario es SV+NV 2024 de los municipios estimables incluidos; no proyecta el electorado de 2027. Municipios pendientes permanecen en el agregado sin cambio; los no estimables se identifican y no cuentan como cero.

`Umbral_demo7_distribucion.csv` conserva clave INE (cinco caracteres; importar como texto), estado de atención, cobertura asignada, tasa base y posterior, reducción en pp, semáforo en ambos escenarios (`bajo`, `medio`, `alto`, `sin_datos`), umbrales, base observable, año, método, catálogo, territorio, reparto, acción, efecto o respuesta, estimador, fuente y límites. Celdas numéricas vacías significan ausencia de estimación. Los límites del efecto pertenecen al supuesto o estudio, no a la incertidumbre predictiva de 2027.

El escenario cumple `H = min(cobertura × efecto/100, cobertura × tasa_base/100)` y `tasa_posterior = tasa_base − 100 × H / base_observable`. El modo personalizado usa respuesta entre abstencionistas y la registra por separado. La agregación pondera por base observable.

`data/resultados.json` y `data/metricas.json` pertenecen al experimento anterior; sirven como insumo compartido. Demo7 incorpora el complemento `data/comparacion_modelos.js`. Las descargas vigentes apuntan a `data/comparacion_modelos.json` y a `modelado/salidas/comparacion_modelos/`, evitando atribuir resultados antiguos al modelo actual.

## Verificación

```powershell
node --test 02_Prediccion_y_escenarios_de_riesgo/demo/decision.test.cjs 02_Prediccion_y_escenarios_de_riesgo/demo/intervenciones.test.cjs
python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo7.py
python 02_Prediccion_y_escenarios_de_riesgo/entrega/verificar_entrega.py
```

La prueba de navegador utiliza Edge instalado y Python estándar, con un perfil temporal exclusivo. Revisa arranque local, enlaces de entrega, mapas, cobertura cero, cambio de método, exportación trazable y vista móvil; guarda evidencias en `verificacion/demo7/`. El verificador de entrega comprueba páginas, diapositivas, cifras del caso y la huella de los recursos web. Las pruebas no acreditan inscripción, firmas ni validación institucional.

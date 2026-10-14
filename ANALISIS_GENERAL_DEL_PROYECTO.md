# Umbral — explicación del proyecto y análisis general

**Proyecto:** Umbral, atlas de decisión municipal.
**Concurso:** Hackathon INE 2026, Reto 2 (predicción y escenarios de riesgo de abstención).
**Equipo:** aguas.exe — Martin Isai Nuñez Villeda y Cesar Donnet Hernandez Gastelum.
**Corte del documento:** 6 de octubre de 2026; actualizado con acciones citadas y distribución territorial.
**Estado:** prototipo funcional y evaluación retrospectiva; entrega formal pendiente de actos humanos (registro, firmas, envío).

Este documento explica **todo el proyecto** y ofrece un **análisis general** con datos observados. No sustituye al reporte metodológico y preventivo de la convocatoria; es una guía de lectura y una valoración honesta de fortalezas, límites y riesgos.

---

## 1. Qué es el proyecto

Umbral es una herramienta de **priorización territorial auditable**. Responde una decisión concreta:

> Si un área de educación cívica dispone de cobertura total para una acción, ¿cuáles conviene revisar primero, con qué respaldo, qué tan confiable es esa prioridad y qué puede hacerse después?

Combina una **referencia sencilla** (la abstención de la última elección del mismo tipo) con un **ajuste Ridge regularizado**, muestra la **calidad del dato** y ofrece **escenarios** sin y con intervención hipotética. Prioriza por **tasa de abstención estimada** (con lentes alternativos de volumen y deterioro), no por número absoluto.

**Qué es:** una herramienta de priorización auditable y un registro explícito de supuestos.
**Qué no es:** un predictor validado de 2027, un asignador automático de recursos, ni una demostración de causalidad.

---

## 2. Contexto: el Hackathon y los tres retos

La convocatoria propone tres retos. El proyecto eligió el **Reto 2** por decisión del usuario.

| Carpeta | Reto | Contenido del repositorio |
|---|---|---|
| `01_Perfiles_ciudadanos_de_participacion/` | Reto 1: perfiles ciudadanos | solo README y recursos (no desarrollado) |
| `02_Prediccion_y_escenarios_de_riesgo/` | **Reto 2: predicción y escenarios** | **desarrollo completo** |
| `03_Comunicacion_y_visualizacion/` | Reto 3: comunicación y visualización | solo README y recursos (no desarrollado) |

**Fechas y envío** (convocatoria, págs. 4–5): registro hasta el **15 de octubre de 2026**; entrega hasta el **31 de octubre de 2026, 23:59**, en ZIP identificado por equipo y eje, por correo a `grecia.castro@ine.mx` y `cirse.rodriguez@ine.mx`.

**Requisitos del Reto 2:** reporte metodológico y preventivo de **10 a 15 cuartillas** (PDF) con variables, semáforo territorial y recomendaciones preventivas y de priorización de recursos; **mapa ejecutable que compare con y sin intervención** más la **base anonimizada** (CSV/XLSX). Entregables generales: **presentación ≤10 diapositivas**, **código/repositorio** y **cartas firmadas**.

> **Criterio de "cuartilla":** la convocatoria **no lo define**. El "Documento técnico" del Reto 1 sí fija Arial/Calibri 11 e interlineado 1.5, pero para sus 8–12 cuartillas. Aquí se interpreta **1 cuartilla = 1 página carta de PDF (una cara)**; conviene confirmarlo con la organización. El reporte usa **14 de 15**.

---

## 3. Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `README.md` | Entrada del proyecto y estado |
| `EXPLICACION_DEL_PROYECTO.md` | Narrativa de desarrollo |
| `ANALISIS_GENERAL_DEL_PROYECTO.md` | Este documento |
| `01_…/ 03_…/` | Retos no desarrollados |
| `02_…/documentos_oficiales/` | Convocatoria, cartas, manual CCPC |
| `02_…/auditoria/` | Scripts, inventarios y resultados de auditoría |
| `02_…/datos_preparados/` | Base municipal agregada y calidad |
| `02_…/cartografia/` | Geometría INE de referencia |
| `02_…/modelado/` | Código, tests, metodología, resultados y salidas |
| `02_…/demo/` | Aplicación, datos incrustados, librería y evidencias |
| `02_…/entrega/` | Reporte PDF y presentación PPTX/PDF |
| `docs/superpowers/` | Especificación, planes y registros de decisiones |
| `Ine_Hackaton_completo.zip` | Respaldo completo **previo** a las correcciones (ver §11) |

---

## 4. Datos

### 4.1 Fuente y volumen auditado

- **Conteos Censales de Participación Ciudadana (CCPC) del INE**, datos **agregados y disociados**, sin datos personales.
- Seis elecciones ordinarias: **2009, 2012, 2015, 2018, 2021 y 2024**.
- **54,872,712 filas** de **192 CSV** auditadas; **14,779 registros municipio-año** y **2,477 claves**.
- Prisión preventiva y voto anticipado se conservan como fuentes separadas (no se concatenaron).

La auditoría verificó integridad CRC, duplicados, identidades y reconciliación de conteos; la suma de los cuatro conteos agregados coincide con los originales en cada año. Evidencia: `auditoria/RESULTADOS.md`, `auditoria/verificacion_final.json`.

### 4.2 Definiciones

```text
SV = participación registrada        NV = no participación
NS = participación no especificada   LN = SV + NV + NS
abstención observable (%) = 100 × NV / (SV + NV)     [si SV+NV > 0]
NS (%)                    = 100 × NS / LN
```

Se suman conteos antes de calcular porcentajes; **NS nunca se trata como abstención**. Una tasa vacía es denominador cero, no abstención de cero.

### 4.3 Calidad y cobertura

- Regla principal: **NS ≤10%** en el antecedente más reciente y el del mismo tipo; la evaluación exige además objetivo observable con NS ≤10%.
- Sensibilidad a **NS ≤5%** y **NS ≤20%**.
- Estimaciones 2027: **1,783**; sin estimación: **694** sobre 2,477 claves (nunca riesgo cero; gris con motivo).

### 4.4 Variables del predictor (10)

Abstención del mismo tipo, abstención del último proceso, su diferencia, logaritmo de LN, proporción 18–29, proporción 60+ sin edades extremas, proporción urbana, NS de ambos antecedentes y tipo de elección. **Omitidas:** sexo, escolaridad y variables externas no verificadas (sexo se usa solo en la capa explicativa posterior).

### 4.5 Límites de los datos

Una **clave municipal constante no prueba límites ni población constantes**. No hay armonización histórica de fronteras; los conteos no se redistribuyeron a los límites de 2024.

---

## 5. Modelo

- **Referencia:** última elección del **mismo tipo** (2015 para 2021, 2018 para 2024, 2021 para 2027). Si no hay antecedente válido, no se sustituye por otro tipo.
- **Ridge sobre el residual** de la referencia: StandardScaler + Ridge, **alpha=10 fijado antes de ver métricas**, salida truncada a [0,100].
- **Cortes (sin fuga temporal):** evaluación 2021 con etiquetas 2015/2018; 2024 con 2015/2018/2021; proyección 2027 con 2015/2018/2021/2024. Cada ejemplo usa solo características anteriores a su año objetivo.
- **Regla de selección** fijada en 2021: adoptar Ridge solo si mejora el MAE ≥1% y no empeora MAE ponderado ni precisión top50.
- **2021 es selección, no prueba independiente.** El corte 2024 no se usó para reajustar alpha.

---

## 6. Evidencia y resultados

| Corte | Método | n | MAE pp | MAE pond. pp | Top 50 |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia | 1,490 | 12.12 | 8.05 | 16/50 |
| 2021 | Ridge | 1,490 | **9.21** | **5.49** | **19/50** |
| 2024 | Referencia | 1,476 | **5.64** | **3.54** | 27/50 |
| 2024 | Ridge | 1,476 | 8.58 | 4.49 | 27/50 |

**Lectura honesta:** Ridge mejora ~**23.9%** el MAE en 2021, pero recupera solo 19/50 y **pierde en 2024** (**+52.2%** de MAE). No hay ganador universal; se conserva como método exploratorio con la referencia visible.

**Sensibilidad (cohortes distintas, no resultados comparables):** 2021 con NS ≤5% → 1,007 municipios (MAE 12.69 referencia / 9.86 Ridge); con NS ≤20% → 1,960 (12.20 / 9.16). Catálogo de claves constante: 2021 = 1,050; 2024 = 948; el filtro deja **1,144** estimaciones actuales.

**Bootstrap** por entidad (500 réplicas, semilla 123) solo como sensibilidad espacial; no es incertidumbre temporal.

### 6.1 Análisis posteriores (congelados)

Definidos después del experimento original y antes de calcularlos; **no reajustan** alpha ni la selección.

| Corte | Método | Spearman | Precisión roja | Recobrado rojo | Rojos predichos |
|---|---|---:|---:|---:|---:|
| 2021 | Referencia | 0.485 | 46.76% | 81.52% | 849 |
| 2021 | Ridge | 0.599 | 54.89% | 73.72% | 654 |
| 2024 | Referencia | 0.827 | 88.50% | 37.88% | 113 |
| 2024 | Ridge | 0.811 | 98.18% | 20.45% | 55 |

El umbral rojo se aprende en entrenamiento y se congela por corte (47.814% en 2021; 47.726% en 2024). En 2024 una precisión alta convive con **recobrado bajo**: identifica pocos altos.

**Error por tamaño (P90, 2024 Ridge):** <10 mil → 18.08 pp; 10–100 mil → 14.05 pp; ≥100 mil → 6.74 pp. Describe heterogeneidad, **no** es intervalo prospectivo.

**Estabilidad en seis variantes** (2 métodos × NS 5/10/20): un municipio es **núcleo robusto** si entra en 6/6; **zona de revisión** si entra en 1–5; **fuera** si 0. La incertidumbre del ranking sustituye al rango ±21.05 pp (que queda solo como error histórico).

---

## 7. Producto: la demo Umbral

Abre con **doble clic** en `demo/index.html` (datos incrustados; sin servidor, sin internet, `file://`). Capacidades:

- Mapa nacional, semáforo relativo (tercios), estado gris con motivo.
- **Capas Base / Con intervención / Δ** con umbrales base fijos.
- **Ficha "¿por qué este municipio?"**: posición de prioridad, riesgo, estabilidad, razones verificables, robustez 6/6, acción, hipótesis y cómo evaluarla.
- **Perfil CCPC observado** por edad, sexo y tipo de sección, como capa explicativa **separada del modelo**.
- **Planeación territorial**: municipio, estado o México incluido; acción citada, cobertura total y distribución por prioridad o proporcional a SV+NV 2024; plan y CSV con fuentes.
- **Frontera de decisión**: núcleo robusto, zona de revisión y fuera; piloto aleatorio propuesto.
- Vista por entidad y exportación con supuestos.

---

## 8. Entregables generados

| Entregable | Estado | Ruta |
|---|---|---|
| Reporte metodológico y preventivo | ✅ 14 páginas / 8 secciones | `02_…/entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf` |
| Presentación ejecutiva | ✅ 10 diapositivas | `02_…/entrega/presentacion/Umbral_presentacion.pptx` (+ PDF) |
| Mapa + base anonimizada | ✅ demo + CSV/XLSX + GeoJSON | `02_…/demo/`, `02_…/datos_preparados/` |
| Código/repositorio | ✅ repo privado + paquete | este repositorio |
| Cartas firmadas | ❌ formato disponible, sin firmas | `02_…/documentos_oficiales/` |
| Registro / envío oficial | ❌ no acreditados | — |

### 8.1 Verificación

| Tipo | N | Herramienta |
|---|---|---|
| Pruebas Python | 15 | `unittest` (`modelado/tests/`) |
| Pruebas Node | 12 | `node:test` (`demo/decision.test.cjs`) |
| Comprobaciones de navegador | 24 | Playwright + Edge (`demo/verificar_demo.py`) |
| Integridad de artefactos | — | `modelado/verificar_artefactos.py` |
| Reporte | 14 páginas | `generar_reporte.py` (texto y geometría) |

Las pruebas verifican **comportamiento y consistencia del software**, no precisión prospectiva ni eficacia de una intervención.

---

## 9. Análisis general

### 9.1 Fortalezas

1. **Honestidad metodológica:** no se declara ganador, no se oculta 2024, no se inventan costos ni causalidad.
2. **Auditoría verificable:** cada cifra rastrea a un archivo con hash; integridad conciliada.
3. **Decisión, no solo ML:** convierte la incertidumbre en diseño institucional (capacidad, frontera, piloto).
4. **Incertidumbre de ranking** comunicada como frecuencia entre variantes y acuerdo de métodos.
5. **Ejecutable y portable:** abre sin servidor ni recursos remotos.

### 9.2 Debilidades y riesgos

| Riesgo | Naturaleza |
|---|---|
| Profundidad temporal escasa | 6 procesos, 3 intermedias → transferibilidad baja |
| 2024 desfavorable | Ridge no supera a la referencia en presidencial |
| Sesgo de cohorte | `NS ≤10%` puede excluir zonas con necesidad alta |
| Territorio | clave constante **no** prueba límites constantes; sin armonización |
| Semáforo relativo | tercios, no probabilidad calibrada |
| Perfil CCPC | agregado municipal; riesgo de **falacia ecológica** |
| Prevención | acción propuesta **sin piloto ejecutado** ni validación institucional |
| Presentación | no describe aún ficha, perfil, Modo Director ni frontera |
| Administrativo | registro, firmas y envío no acreditados |

### 9.3 Frente a los cinco criterios de evaluación

| Criterio | Valoración |
|---|---|
| Alineación temática | **Alta** (CCPC agregado, riesgo, escenarios, prevención) |
| Solidez y claridad | **Alta** en método y transparencia; media en validación prospectiva |
| Originalidad | **Media-alta**; el diferencial es la frontera de decisión + piloto, no un algoritmo exótico |
| Viabilidad | **Alta** técnica (reproducible, local); institucional **no demostrada** |
| Aplicación institucional | Potencial claro, **no acreditada** |

### 9.4 Veredicto

Proyecto **metodológicamente serio y bien auditado**, que responde una pregunta operativa concreta y comunica sus límites. Su mayor activo es la **coherencia entre evidencia, incertidumbre y diseño institucional**; su mayor pasivo, la **falta de validación institucional y de profundidad temporal**, más los **pendientes administrativos**.

---

## 10. Cumplimiento y pendientes

**Cumplido (técnico):** datos auditados, modelo con referencia, evaluación retrospectiva, análisis posteriores congelados, semáforo, escenarios, demo con base anonimizada, reporte y presentación.

**Pendiente (humano/institucional):**

1. Confirmar **registro, elegibilidad y composición paritaria** según convocatoria.
2. **Firmar** las cartas de cesión y de decir verdad por todas las personas integrantes.
3. **Enviar** por el medio y plazo oficiales.
4. **Armonizar** límites históricos o justificar la cohorte.
5. **Validar** responsables, recursos y diseño de piloto con el área usuaria.
6. Confirmar con la organización el criterio de **"cuartilla"**.

La presentación se regeneró el 6 de octubre con ficha, perfil descriptivo, cobertura total y distribución territorial, frontera y caso 23008. Ver [caso completo](02_Prediccion_y_escenarios_de_riesgo/entrega/CASO_MUNICIPAL.md) y [guion](02_Prediccion_y_escenarios_de_riesgo/entrega/GUION_PRESENTACION.md).

---

## 11. Reproducción

Desde la raíz del repositorio (`Ine_Hackaton`):

```powershell
python -m pip install --target .task_packages -r 02_Prediccion_y_escenarios_de_riesgo/modelado/requirements.txt
python -m unittest discover -s 02_Prediccion_y_escenarios_de_riesgo/modelado/tests
python 02_Prediccion_y_escenarios_de_riesgo/modelado/ejecutar.py
python 02_Prediccion_y_escenarios_de_riesgo/modelado/ampliar_analisis.py
python 02_Prediccion_y_escenarios_de_riesgo/modelado/perfil_demografico.py
python 02_Prediccion_y_escenarios_de_riesgo/demo/preparar_datos.py
node --test 02_Prediccion_y_escenarios_de_riesgo/demo/decision.test.cjs
python 02_Prediccion_y_escenarios_de_riesgo/modelado/imprimir_cifras.py
```

Demo: abrir `02_Prediccion_y_escenarios_de_riesgo/demo/index.html` con doble clic (o servir con `python -m http.server 8765 --directory 02_Prediccion_y_escenarios_de_riesgo/demo`).

> **Paquete:** `Ine_Hackaton_completo.zip` es un respaldo **anterior** a las correcciones del track 2 (no incluye la demo corregida, `entrega/` ni los análisis posteriores). La entrega técnica vigente es este repositorio; para reconstruirlo: `python empaquetar_proyecto.py`.

---

## 12. Glosario

- **CCPC:** Conteos Censales de Participación Ciudadana.
- **SV / NV / NS / LN:** sí votó / no votó / no especificado / lista nominal.
- **Ridge:** regresión lineal regularizada; aquí ajusta el residual de la referencia.
- **Núcleo robusto:** municipio que entra en la selección en las 6/6 variantes.
- **Frontera de decisión:** zona donde la selección cambia según método, calidad o criterio.
- **MAE:** error absoluto medio en puntos porcentuales.

## 13. Fuentes

- [Hackathon INE 2026](https://ine.mx/hackathon-2026/).
- [Convocatoria oficial](https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf).
- [Conteos Censales de Participación Ciudadana](https://ine.mx/transparencia/datos-abiertos/visualizacion-datos/conteos-censales-participacion/).
- [Portal cartográfico INE](https://pautas.ine.mx/transparencia/mapas/index_2025.html).

## 14. Evidencia interna

- [Auditoría](02_Prediccion_y_escenarios_de_riesgo/auditoria/RESULTADOS.md).
- [Base y calidad](02_Prediccion_y_escenarios_de_riesgo/datos_preparados/README.md).
- [Resultados del modelo](02_Prediccion_y_escenarios_de_riesgo/modelado/RESULTADOS.md).
- [Metodología](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md).
- [Correcciones y estado](02_Prediccion_y_escenarios_de_riesgo/CORRECCIONES_Y_ESTADO.md).
- [Análisis del track](02_Prediccion_y_escenarios_de_riesgo/ANALISIS_TRACK_2.md).
- [Demo](02_Prediccion_y_escenarios_de_riesgo/demo/README.md).

## Actualización del simulador y evidencia de acciones

La interfaz distingue focalizar por prioridad de distribuir proporcionalmente a SV+NV 2024. Ambas son reglas del proyecto, no efectos publicados. La cobertura se introduce como total, sin repetirla en cada municipio. México significa municipios estimables incluidos bajo los filtros; se muestran exclusiones. El promedio territorial incluye municipios no atendidos.

Las acciones usan coeficientes, estimadores e incertidumbre de publicaciones originales; [catálogo y citas](02_Prediccion_y_escenarios_de_riesgo/modelado/EVIDENCIA_INTERVENCIONES.md). El traslado a México es hipotético. Caso 23008: SMS Suecia a 1,000 personas previstas implica 3 votos esperados y reducción de 0.0011748 pp, no 155 votos de una respuesta supuesta de 25%. Los talleres siguen como propuesta sin coeficiente causal. Las pruebas vigentes y las capturas se describen en la [demo](02_Prediccion_y_escenarios_de_riesgo/demo/README.md).

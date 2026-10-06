# Correcciones autorizadas del track 2

Fuente: archivo de recomendaciones aportado por el usuario, `Nuevo documento de texto (3).txt`. Autorización: «corrige en base a esto». Ejecución directa de cambios locales y actualización del repositorio privado autorizado; no nueva aprobación del mismo alcance.

## Diseño y límites

Mantener Ridge alpha=10, cortes y selección original. Nuevas métricas son análisis posteriores, definidos aquí antes de calcular: Spearman con rangos promedio en empates; precisión/recobrado del tercio alto con umbral percentil 2/3 aprendido en entrenamiento y congelado por corte, también para persistencia. Error p90 por tamaño con bins de denominador observado previo (<10 mil, 10–100 mil, ≥100 mil). No reajustar modelo con estas métricas.

Escenario corregido: población de referencia observable 2024 = SV+NV; tanto cobertura máxima como reducción y ponderación usan esa base. NS fuera del escenario, informe separado, no población 2027 proyectada. Campo requerido observado; nunca fallback silencioso a LN para datos nuevos.

Seis variantes 2027: dos métodos × NS 5/10/20, entrenamientos idénticos al procedimiento previo, sin retuning. Frecuencia de entrada topN calculada con filtro y criterio activos; las variantes no elegibles cuentan como no seleccionadas y se informa elegibilidad por separado. Núcleo robusto solo si entra en las seis; estabilidad descriptiva, no probabilidad/confianza calibrada. Catálogo territorial como indicador separado, sin certificar límites.

Lentes tasa, volumen estimado sobre observados, deterioro frente a último mismo tipo; concordancia entre listas. Escenario cartográfico Base/Con intervención/Δ con umbrales base fijos. Inversión: alcance/respuesta requeridos para bajar nivel y factibilidad bajo límites, respuestas cero/ausencia sin divisiones inválidas. Estado gris y motivo de exclusión específico.

Prevención con tipologías observables, responsables propuestos, cobertura, condiciones, personas como recurso, medición y mecanismo hipotético. Piloto aleatorio propuesto dentro de conjunto elegible y balanceado alrededor del corte; cercanía de score no acredita equivalencia ni causalidad. Vista operativa por entidad; no inventar correspondencia distrital ausente.

Datos incrustados en JS para apertura file:// sin fetch, sin dependencias remotas. Reporte 12 páginas PDF y presentación ≤10 diapositivas con resultados reales; información de equipo no inventada, firmas/registro no realizados por agente. Paquete técnico autónomo con código local accesible al jurado, formatos de cartas sin firmar y pendientes administrativos visibles.

## Tareas

- [x] Pruebas RED/GREEN: métricas nuevas, frecuencia, lente, denominador, inversión.
- [x] Extensión de análisis y generación de datos, sin alterar experimento original.
- [x] Demo corregida con capas, fichas, vista entidad, exportación y file://.
- [x] Reporte PDF 10–15 páginas y presentación ≤10 diapositivas, revisados visualmente (trabajos documentales independientes en paralelo).
- [x] Comando de cifras, documentación vigente, paquete y verificación real.
- [x] Revisión independiente final, corregir hallazgos, commit/push y entrega.

Los requisitos humanos faltantes se solicitan mientras se avanza: nombre/equipo, registro y firmas. No son autorización para inventar identidad, firmar, registrar o enviar por correo.

## Ejecución y evidencia (2026-10-05)

- Pruebas: 15 unittest (`modelado/tests/`, incluida `test_ampliacion.py`) y 9 pruebas Node (`demo/decision.test.cjs`) en verde. Integridad de artefactos verificada con `modelado/verificar_artefactos.py`.
- Navegador real (Edge headless vía Playwright): 19 comprobaciones en `demo/verificar_demo.py`, incluidas capas Base/Intervención/Δ, estabilidad 6/6, lentes, resumen por entidad, fichas/exclusiones y apertura `file://`.
- Cifras: `modelado/imprimir_cifras.py` reproduce la configuración inicial (50 municipios, núcleo robusto 9/50). Los valores de `evaluacion_adicional.json` coinciden con `CORRECCIONES_Y_ESTADO.md` y con reporte/presentación (Spearman 0.485/0.599 · 0.827/0.811; umbrales 47.814%/47.726%).
- Documentos: reporte de 12 páginas y presentación de 10 diapositivas generados y revisados por render local; PPTX verificado estructuralmente, pendiente de motor PowerPoint.
- Revisión independiente final: sin hallazgos críticos ni importantes en código. Se corrigió documentación obsoleta: `ANALISIS_TRACK_2.md` y `EXPLICACION_DEL_PROYECTO.md` citaban «11 pruebas Python, 5 Node y 11 comprobaciones de navegador»; se actualizó a los conteos vigentes (15/9/19).
- Límites que permanecen explícitos: sin armonización histórica de límites, sin validación institucional, sin causalidad, y registro/firmas/envío pendientes de las personas participantes.

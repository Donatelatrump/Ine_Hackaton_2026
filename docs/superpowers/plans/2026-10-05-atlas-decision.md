# Atlas de decisión municipal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** demostrar una decisión municipal con validación temporal, calidad visible y escenarios documentados.
**Architecture:** núcleo de análisis puro; ejecución reproducible con scikit-learn; demo local estática alimentada por JSON y GeoJSON simplificado.
**Tech Stack:** Python, numpy/pandas/scikit-learn, shapely, HTML/CSS/JS, Leaflet local, unittest y node:test.
**Spec:** `docs/superpowers/specs/2026-10-05-atlas-decision-design.md`.

## Global Constraints

Alpha=10; datos solamente previos al objetivo; cortes 2021/2024; selección en 2021 con MAE 1% mejor y métricas ponderada/top50 no peores; NS 10% principal; sensibilidad 5% y 20%. Sin afirmar causalidad, estabilidad de límites o cobertura probabilística prospectiva. Trabajo local dentro del workspace; no publicación externa. Originales intactos.

## Review Focus

- Antecedente del mismo tipo ausente: devolver proyección ausente, no rellenarla con presidencial.
- NS o denominadores inválidos: excluir de estimación, preservar en mapa.
- Empates y capacidad superior a datos: selección determinista, máximo disponible.
- Respuesta cero, alcance superior a electorado y entradas no finitas: escenario sin errores o cifras imposibles.
- Datos y exportación con nombres acentuados: UTF-8, texto escapado y controles responsivos.

### Task 1: Núcleo y validación retrospectiva

**Files:** `02_Prediccion_y_escenarios_de_riesgo/modelado/core.py`, `modelado/ejecutar.py`, `modelado/tests/test_core.py`.
**Interfaces:** `make_features(history, target_year, ns_limit) -> dict|None`; `metricas(y,pred,weights,keys,k) -> dict`; `choose_model(baseline,candidate) -> str`; `scenario(items,capacity,reach,response) -> dict`.
- [x] Escribir y ejecutar tests que fallen: fuga de objetivo/futuro, falta de mismo tipo, calidad, métricas con valores manuales, elección de referencia, escenarios limitados.
- [x] Implementar funciones, ejecutar unittest completo.
- [x] Ejecutar cortes congelados 2021/2024, exportar cohortes, métricas y proyección 2027; comparar sensibilidad y catálogos constantes.
- [x] Verificar que cada característica se apoya en años anteriores y que no hay NaN JSON, claves duplicadas o valores fuera de rango.

### Task 2: Demo de decisión local

**Files:** `demo/index.html`, `demo/style.css`, `demo/app.js`, `demo/decision.js`, `demo/decision.test.cjs`, `demo/data/`, `demo/vendor/`.
**Interfaces:** consume `resultados.json` y `municipios.geojson`; exporta selección filtrada y escenario con supuestos en CSV.
- [x] Escribir node:test con ranking, ausencia, límites y respuesta cero; comprobar RED.
- [x] Implementar la decisión JS y comprobar GREEN.
- [x] Crear interfaz accesible y mapa sin teselas externas; instalar Leaflet local, copiar resultados y geometría simplificada.
- [x] Arrancar servidor local, probar búsqueda, filtros, detalle, escenario, exportación y vista móvil con navegador headless; inspeccionar captura.

### Task 3: Evidencia y revisión

**Files:** `modelado/RESULTADOS.md`, `modelado/METODOLOGIA.md`, `demo/README.md`, README del track y registro `docs/superpowers/plans/2026-10-05-atlas-decision-ledger.md`.
- [x] Documentar resultados reales, selección, limitaciones, instrucciones y pendientes del concurso.
- [x] Ejecutar unittest y node:test completos, y verificaciones reales del artefacto.
- [x] Una revisión independiente de análisis, escenario y demo; corregir hallazgos importantes con pruebas.
- [x] Entregar URL local, resultados principales y estado honesto del modelo.

No hay repositorio Git en este workspace: registrar evidencias en el ledger en lugar de crear un repositorio o ejecutar pasos de commit/worktree que no aplican. El usuario autorizó aplicar el enfoque y continuar; ejecutar inline sin nueva ronda de confirmación.

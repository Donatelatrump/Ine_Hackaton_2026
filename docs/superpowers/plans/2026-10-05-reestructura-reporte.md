# Reestructura del reporte a la plantilla de 8 secciones — Track 2

Fuente: mensaje del usuario con la plantilla del «reporte metodológico y preventivo (15 cuartillas)» y la petición de verificar si el documento actual la sigue y corregirlo si no.

## Hallazgo

El reporte vigente tenía 12 páginas y un reparto distinto (portada, problema, fuentes, método, evidencia, análisis posteriores, semáforo, escenarios, prevención, piloto, operación, reproducibilidad). No correspondía a las 8 secciones ni al presupuesto de páginas de la plantilla.

## Decisión

Se reestructuró a **14 páginas / 8 secciones** (deja una de margen sobre el máximo de 15):

| Sección | Páginas |
|---|---|
| Portada y resumen ejecutivo | 1 |
| 1. Problema y decisión | 1 |
| 2. Datos y variables | 2 |
| 3. Modelo | 2 |
| 4. Evidencia y límites | 2 |
| 5. Semáforo (con figura) | 1 |
| 6. Escenarios (con figura de tres paneles) | 1 |
| 7. Prevención y priorización | 3 |
| 8. Viabilidad y uso responsable | 1 |

## Tareas

- [x] Revisar el reporte contra la plantilla y detectar la brecha de estructura.
- [x] Reestructurar el generador a 8 secciones y 14 páginas.
- [x] Añadir tablas de variables y de viabilidad, y tres tablas con pie de fuente.
- [x] Añadir figuras (mapa del semáforo y tres paneles de escenario) con captura del mapa base.
- [x] Actualizar referencias de 12 a 14 páginas en la documentación.
- [x] Verificar la generación (14 páginas, sin desbordes) y el conteo de figuras/tablas.

## Criterio de «cuartilla»

La convocatoria (página 4) pide 10-15 **cuartillas** para el Reto 2 y no define la unidad; el «Documento técnico» del Reto 1 sí fija Arial/Calibri 11 e interlineado 1.5, pero para 8-12 cuartillas. Se interpreta **1 cuartilla = 1 página carta de PDF (una cara)**, uso habitual del término, y se recomienda confirmarlo con la organización. El reporte usa 14 de 15.

## Evidencia (2026-10-05)

- `entrega/reporte/generar_reporte.py` regenera el PDF, la fuente Markdown, los renders por página, la hoja de contacto y `verificacion.json`.
- Generación: **14 páginas**, texto extraíble y cajas dentro del tamaño carta; sin desbordes. Página 9 con 1 figura; página 10 con 3 imágenes (paneles del escenario).
- Captura `demo/verificacion/mapa_base.png` añadida a `verificar_demo.py`; verificación de navegador 24/24 sin errores.
- Límites: la presentación sigue sin describir las nuevas capas; el diccionario de datos y las tablas largas permanecen en el CSV/XLSX y el repositorio, no en el PDF.

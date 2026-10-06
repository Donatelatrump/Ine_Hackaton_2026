# Reporte Umbral - Tecnocalidos

Versión técnica para revisión del track 2, 5 de octubre de 2026. El PDF tiene 14 páginas en 8 secciones (portada y resumen ejecutivo, problema, datos y variables, modelo, evidencia y límites, semáforo, escenarios, prevención y priorización, viabilidad). No acredita registro, firmas ni envío oficial.

## Criterio de cuartilla

La convocatoria pide **10 a 15 cuartillas** para el Reto 2 y **no define la unidad**. En este trabajo se interpreta **1 cuartilla = 1 página carta de PDF (una cara)**, coherente con el uso habitual del término. Se recomienda confirmarlo con la organización; por eso el reporte usa 14 de las 15 permitidas y deja el diccionario de datos y las tablas largas en el CSV/XLSX y el repositorio.

## Archivos

- `Umbral_reporte_metodologico_preventivo.pdf`: reporte de lectura.
- `Umbral_reporte_fuente.md`: texto generado, tablas y contenido de las 14 páginas.
- `generar_reporte.py`: fuente de autoría y regeneración. Para cambios permanentes editar este script y regenerar.
- `verificacion.json`: conteo de páginas, hash y comprobaciones geométricas/textuales.
- `revision_visual/`: PNG por página y hoja de contacto de la versión generada.

## Regenerar

Desde la raíz del repositorio:

```powershell
python -m pip install --target 02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/.packages reportlab==5.0.1 pymupdf==1.28.2 pypdf==6.19.0
python 02_Prediccion_y_escenarios_de_riesgo/entrega/reporte/generar_reporte.py
```

También admite dependencias instaladas en el entorno Python. Usa Arial de Windows cuando está disponible; en otros sistemas usa Helvetica. Lee `modelado/salidas/metricas.json` y `evaluacion_adicional.json`. La falta del segundo se declara explícitamente y nunca produce cifras inventadas. Para reproducir esta versión se requiere conservar ambos insumos.

La carpeta `.packages` es una instalación local auxiliar; no es fuente de datos y puede omitirse del paquete técnico si se aporta el comando de instalación. Los datos originales y la ejecución del modelo tienen su propia reproducibilidad, separada de regenerar el reporte.

## Verificación realizada

Se generaron 14 páginas con texto extraíble y cajas dentro del tamaño carta. Se incrustan dos figuras (mapa del semáforo y tres paneles de escenario) y tres tablas (métricas, variables y viabilidad). Se renderizó cada página mediante PyMuPDF, alternativa local disponible a Poppler, y se inspeccionaron la hoja de contacto y páginas densas a resolución de lectura. Se confirmó legibilidad de tablas, referencias y fichas, sin superposición ni texto recortado. La última comprobación se registra en `verificacion.json`; las pruebas de documento no acreditan precisión futura ni impacto causal.

El marcador de operación de autoría del skill PDF se ejecutó correctamente antes de la primera creación. La convocatoria oficial se abrió y contrastó en páginas 3-5: método/escenarios, reporte de 10-15 cuartillas y mínimos de entrega. Fuente: https://ine.mx/wp-content/uploads/2026/09/Convocatoria_Hackaton-1.pdf.

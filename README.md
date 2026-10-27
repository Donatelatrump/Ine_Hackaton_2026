# Umbral

**Equipo: Aguas.exe** · Reto 2: Predicción y escenarios de riesgo de abstención.

Umbral permite explorar antecedentes electorales municipales, comparar modelos de abstención y simular escenarios de participación. Incluye mapas, contexto estatal, fuentes consultadas y exportaciones de resultados.

## Abrir el proyecto

1. Si recibiste un ZIP, **extrae todo su contenido**.
2. Abre **[index.html](index.html)** con doble clic en Edge, Chrome o Firefox.
3. Selecciona un estado o municipio y explora los resultados y las acciones.

La aplicación incluye sus datos, estilos, scripts y biblioteca de mapas. Para consultarla no necesitas instalar Python ni Node, ni conectarte a internet. Los enlaces a sitios externos sí requieren conexión. Conserva las carpetas junto al HTML de inicio.

## Contenido de la entrega

| Ruta | Contenido |
| --- | --- |
| `index.html` | Acceso directo a Umbral. |
| `umbral/demo/` | Aplicación vigente, datos publicados, imágenes y código web. |
| `umbral/entrega/` | Reporte, presentación, caso municipal y revisión de requisitos. |
| `umbral/modelado/` | Código, dependencias, metodología y resultados de los modelos. |
| `umbral/datos_preparados/` | Bases procesadas para análisis y consulta. |
| `umbral/auditoria/` y `umbral/cartografia/` | Procesamiento, calidad de datos y cartografía. |
| `umbral/documentos_oficiales/` | Insumos y documentación oficial del reto. |
| `fuentes/` | Bases explicativas, estudios y documentos consultados en su formato original. |
| `docs/` | Explicación del proyecto, planes estatales y referencias complementarias. |
| `umbral/arquitectura/` y `umbral/tools/` | Documentación técnica y herramientas de mantenimiento. |
| `tools/` | Empaquetado y procesamiento cartográfico auxiliar. |

## Documentos para evaluación

- [Reporte metodológico y preventivo (PDF)](umbral/entrega/reporte/Umbral_reporte_metodologico_preventivo.pdf).
- [Presentación (PDF)](umbral/entrega/presentacion/Umbral_presentacion.pdf) y [versión editable (PPTX)](umbral/entrega/presentacion/Umbral_presentacion.pptx).
- [Guion](umbral/entrega/GUION_PRESENTACION.md) y [caso municipal](umbral/entrega/CASO_MUNICIPAL.md).
- [Metodología](umbral/modelado/METODOLOGIA.md) y [comparación de cuatro modelos](umbral/modelado/COMPARACION_4_MODELOS.md).
- [Fuentes de información](fuentes/README.md).
- [Revisión de requisitos y pendientes de entrega](umbral/entrega/REVISION_REQUISITOS_INE.md).

## Alcance de los resultados

Los años 2009–2024 contienen antecedentes observados; **2027 es una proyección exploratoria**. La aplicación consulta resultados precalculados y no entrena modelos al navegar.

Se compararon Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. El modelo inicial es HistGradientBoosting, con MAE medio de 6.836 puntos porcentuales en los cortes retrospectivos de 2021 y 2024. Estos cortes participaron en la selección y no validan la proyección de 2027.

Las fichas estatales son descriptivas. Los escenarios incluyen supuestos de cobertura y efecto; no representan eficacia causal demostrada. El gris indica datos insuficientes, no abstención cero.

## Ejecución y mantenimiento técnico

El servidor local es opcional. Desde la raíz, con Python 3:

```powershell
python umbral/tools/servir_demo.py
```

Abre `http://127.0.0.1:8000/`. Para reconstruir la web después de modificar sus fuentes:

```powershell
python umbral/tools/construir_demo7.py
```

Las fuentes vigentes están en `umbral/demo/src/demo7/`. Los módulos de `src/demo6/` y estilos de `styles/demo6/` conservados son dependencias compartidas de la aplicación actual. `build.demo7.config.json` define su composición. No edites manualmente los paquetes de `assets/` ni los datos generados. Consulta [la guía funcional](umbral/demo/DEMO7.md) y [las dependencias del modelo](umbral/modelado/requirements.txt) para reproducir el análisis.

Verificaciones disponibles (Node para JavaScript; Python y Edge para la prueba de navegador):

```powershell
node --test umbral/demo/decision.test.cjs umbral/demo/intervenciones.test.cjs umbral/demo/demo6.test.cjs
python umbral/demo/verificar_demo7.py
```

Para producir el ZIP oficial del Reto 2 con comprobación de integridad:

```powershell
python tools/empaquetar_proyecto.py
```

Se genera `Aguas.exe_Reto_2_Prediccion_y_escenarios_de_riesgo_de_abstencion.zip`: reporte PDF, presentación PDF, ambas cartas firmadas de `umbral/entrega/`, base histórica y proyecciones CSV, `index.html` autónomo y `codigo/` con las fuentes activas y el experimento de cuatro modelos. No incluye archivos `.md`, versiones anteriores, pruebas, cachés ni documentos auxiliares de desarrollo. Las firmas se conservan sin modificar los PDF originales. El HTML del ZIP se reconstruye con `python codigo/construir_web.py`.

También incluye `Info_extra/`, con las investigaciones y bases originales de `fuentes/` y los recursos de las páginas guardadas. El apartado «Investigaciones y fuentes complementarias» del HTML enlaza esas copias locales. Extrae todo el ZIP para conservar las rutas.

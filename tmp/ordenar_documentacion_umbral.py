from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'docs/archivo';archive.mkdir(exist_ok=True)
for name in ['README.md','ANALISIS_GENERAL_DEL_PROYECTO.md']:
 dest=archive/(Path(name).stem+'_antes_reorganizacion_20261016.md')
 if dest.exists():raise FileExistsError(dest)
 shutil.copy2(ROOT/name,dest)
readme='''# Umbral · demo6

Exploración de antecedentes electorales, proyecciones municipales y contexto estatal. Versión actual: **demo6**. Voto Vigía es otro proyecto y se mantiene separado.

## Abrir la aplicación

Desde la raíz del repositorio:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py
```

Abrir [demo6 local](http://127.0.0.1:8000/02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html). El servidor incluye las carpetas de fuentes para que funcionen los enlaces de las fichas. La página también puede abrirse directamente desde su archivo HTML.

## Orientarse en el proyecto

- [Análisis general actual](ANALISIS_GENERAL_DEL_PROYECTO.md).
- [Arquitectura, carpetas y mantenimiento](02_Prediccion_y_escenarios_de_riesgo/arquitectura/README.md).
- [Código de demo6 y contratos](02_Prediccion_y_escenarios_de_riesgo/demo/src/demo6/README.md).
- [Guía funcional de demo6](02_Prediccion_y_escenarios_de_riesgo/demo/DEMO6.md).
- [Fichas estatales y fuentes](02_Prediccion_y_escenarios_de_riesgo/demo/FICHAS_ESTATALES.md).
- [Metodología vigente](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md).
- [Comparación real de cuatro modelos](02_Prediccion_y_escenarios_de_riesgo/modelado/COMPARACION_4_MODELOS.md).
- [Entregables](02_Prediccion_y_escenarios_de_riesgo/entrega/README.md) y [acuerdos de colaboración](CONTRIBUTING.md).

## Estado del modelo

Se compararon Ridge, HistGradientBoosting, LightGBM y CatBoost con las mismas 15 variables históricas. Demo6 usa HistGradientBoosting por defecto: MAE medio 6.836 pp en los cortes 2021 y 2024, frente a 9.009 de Ridge. LightGBM obtuvo 6.830 pp; el empate práctico dentro de 0.05 pp se resolvió por menor error ponderado. Ridge fue más rápido. La selección es retrospectiva y no valida 2027.

La web consulta predicciones precalculadas; no reentrena al navegar. Las fichas estatales son descriptivas y no demuestran causas individuales ni efectos de intervenciones.

## Desarrollo

Los cambios de la web actual se realizan en `02_Prediccion_y_escenarios_de_riesgo/demo/src/demo6/` y `demo/styles/demo6/`. Las fuentes originales y los datos publicados conservan su ubicación. No editar manualmente los JSON/JS generados.

El inventario estático se regenera con:

```powershell
python 02_Prediccion_y_escenarios_de_riesgo/tools/inventario.py
```

Las instrucciones del experimento usan `.venv_modelos` y su archivo de dependencias congeladas. Las demos anteriores conservan sus entradas HTML y recursos compartidos.

## Histórico

La documentación previa a esta reorganización se conserva en [docs/archivo](docs/archivo/README.md). Los comandos y cifras históricos deben interpretarse según su versión. Las capturas y copias de depuración de la web están en `demo/archivo/depuracion/`.
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')

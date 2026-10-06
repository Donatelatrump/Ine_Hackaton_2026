# Ine_Hackaton_2026

Proyecto **Umbral**, atlas de decisión municipal para el track 2 del Hackathon INE 2026: predicción y escenarios de riesgo de abstención, con cobertura nacional por municipio.

## Documentación

- [Por qué, qué y cómo se desarrolló](EXPLICACION_DEL_PROYECTO.md).
- [Resultados reales y limitaciones](02_Prediccion_y_escenarios_de_riesgo/modelado/RESULTADOS.md).
- [Metodología y reproducción](02_Prediccion_y_escenarios_de_riesgo/modelado/METODOLOGIA.md).
- [Instrucciones de la demo](02_Prediccion_y_escenarios_de_riesgo/demo/README.md).

## Ejecutar la demo

Desde la raíz del repositorio:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765. La demo preparada funciona con recursos locales y no requiere reentrenar.

## Datos y archivos grandes

El repositorio conserva las tres carpetas de tracks, fuentes originales, bases procesadas, código, demo, pruebas y documentación. Los ZIP y la cartografía original se almacenan mediante Git LFS. Después de clonar con Git LFS instalado:

```powershell
git lfs pull
```

`Ine_Hackaton_completo.zip` es una entrega completa anterior a la creación del repositorio e incluye las dependencias locales y el manifiesto de sus archivos. Las dependencias instaladas y cachés quedan fuera del historial Git; para reproducir el análisis se reinstalan según `modelado/requirements.txt` dentro del track 2. El script de empaquetado excluye los metadatos internos `.git` al regenerar el archivo.

## Estado

Modelo y demo exploratorios, pruebas e integridad verificadas. Ridge mejora en el corte 2021 y pierde frente a la referencia en 2024. La proyección 2027 no constituye predicción prospectiva validada ni demuestra efectos causales. Los entregables formales del concurso y armonización territorial histórica siguen pendientes.

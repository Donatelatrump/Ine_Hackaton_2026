# Umbral: demo local

Desde la raíz `Ine_Hackaton`:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener la terminal activa. Detener con Ctrl+C. No abrir index.html directamente: el navegador necesita servir los JSON.

Seleccionar entidad, buscar por nombre/clave y revisar el filtro de catálogo constante. Ajustar capacidad, alcance y respuesta supuesta; mapa y plan se actualizan. Las filas y municipios abren antecedentes. Descargar plan exporta toda la selección, incluso si la tabla solo muestra 25.

La vista inicial conserva el filtro de entidades con catálogo constante: 1,144 estimaciones. Al desmarcarlo se muestran 1,783 estimaciones nacionales. Permanecen visibles los municipios sin estimación y los territorios fuera del filtro se atenúan. Cartografía simplificada exclusivamente para visualización, sin teselas ni librerías remotas. Los enlaces oficiales del pie requieren internet si se abren.

La proyección 2027 es exploratoria. Resultados de 2024 adversos al modelo, rango de error histórico, calidad y supuestos se muestran expresamente. LN 2024 limita alcance, no proyecta electorado futuro; escenario sin efecto causal demostrado.

Pruebas del navegador: instalar `playwright==1.63.0` en `.task_packages` y ejecutar `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py` con servidor activo. Usa Edge instalado en su ruta estándar de Windows; capturas y resultado se guardan en `verificacion/`. Node prueba el escenario sin navegador. Leaflet: 1.9.4, licencia incluida en `vendor/LICENSE`.

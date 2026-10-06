# Umbral: demo local

**Versión corregida:** abre con doble clic en `index.html`, sin Python ni internet para datos/librerías. Mantener carpeta completa; usa datos JS incrustados. Capas Base/Intervención/Δ, lentes, estabilidad, fichas y entidad. Escenario con SV+NV 2024, NS fuera. [Correcciones](../CORRECCIONES_Y_ESTADO.md).

Desde la raíz `Ine_Hackaton`:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener la terminal activa. Detener con Ctrl+C. El servidor es opcional en esta versión.

Seleccionar entidad, buscar por nombre/clave y revisar el filtro de catálogo constante. Ajustar capacidad, alcance y respuesta supuesta; mapa y plan se actualizan. Las filas y municipios abren antecedentes. Descargar plan exporta toda la selección, incluso si la tabla solo muestra 25.

La vista inicial conserva el filtro de entidades con catálogo constante: 1,144 estimaciones. Al desmarcarlo se muestran 1,783 estimaciones nacionales. Permanecen visibles los municipios sin estimación y los territorios fuera del filtro se atenúan. Cartografía simplificada exclusivamente para visualización, sin teselas ni librerías remotas. Los enlaces oficiales del pie requieren internet si se abren.

Proyección 2027 exploratoria; 2024 adverso visible. SV+NV 2024 define tasas y limita alcance, NS fuera, no electorado proyectado. Frecuencia no probabilística; escenario sin causalidad demostrada.

Pruebas del navegador: instalar `playwright==1.63.0` en `.task_packages` y ejecutar `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py` con servidor activo. Usa Edge instalado en su ruta estándar de Windows; capturas y resultado se guardan en `verificacion/`. Node prueba el escenario sin navegador. Leaflet: 1.9.4, licencia incluida en `vendor/LICENSE`.

# Umbral: demo local

**Versión corregida:** abre con doble clic en `index.html`, sin Python ni internet para datos/librerías. Mantener carpeta completa; usa datos JS incrustados. Capas Base/Intervención/Δ, lentes, estabilidad, fichas y entidad. Escenario con SV+NV 2024, NS fuera. **Modo Director** con capacidad territorial o humana y confianza mínima; **ficha «¿Por qué este municipio?»** con razones, robustez, acuerdo de métodos, perfil CCPC, acción e hipótesis; **frontera de decisión** (núcleo 6/6, zona de revisión, fuera). [Correcciones](../CORRECCIONES_Y_ESTADO.md).

Desde la raíz `Ine_Hackaton`:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory 02_Prediccion_y_escenarios_de_riesgo/demo
```

Abrir http://127.0.0.1:8765 y mantener la terminal activa. Detener con Ctrl+C. El servidor es opcional en esta versión.

Seleccionar entidad, buscar por nombre/clave y revisar el filtro de catálogo constante. En Modo Director: capacidad por municipios o por personas alcanzables, criterio de prioridad y confianza mínima; el plan sugerido resume selección, entidades, base observable, núcleo robusto, casos por revisar y escenario. Ajustar alcance y respuesta supuesta; mapa y plan se actualizan. Las filas y municipios abren la ficha explicativa y el perfil CCPC. Descargar plan exporta toda la selección, incluso si la tabla solo muestra 25.

La vista inicial conserva el filtro de entidades con catálogo constante: 1,144 estimaciones. Al desmarcarlo se muestran 1,783 estimaciones nacionales. Permanecen visibles los municipios sin estimación y los territorios fuera del filtro se atenúan. Cartografía simplificada exclusivamente para visualización, sin teselas ni librerías remotas. Los enlaces oficiales del pie requieren internet si se abren.

Proyección 2027 exploratoria; 2024 adverso visible. SV+NV 2024 define tasas y limita alcance, NS fuera, no electorado proyectado. La **confianza de prioridad** es la frecuencia con que un municipio entra en la selección entre las seis variantes de método y calidad; no es probabilidad calibrada. El perfil CCPC por edad, sexo y tipo de sección es una **capa explicativa** calculada de los conteos crudos: no alimenta al modelo y no implica causalidad. El rango ±21.05 pp se conserva solo como error histórico.

Pruebas del navegador: instalar `playwright==1.63.0` en `.task_packages` y ejecutar `python 02_Prediccion_y_escenarios_de_riesgo/demo/verificar_demo.py` con servidor activo. Usa Edge instalado en su ruta estándar de Windows; capturas y resultado se guardan en `verificacion/`. Son 24 comprobaciones, incluida apertura `file://`. Node prueba escenario, confianza, capacidad humana y frontera sin navegador (12 pruebas). Leaflet: 1.9.4, licencia incluida en `vendor/LICENSE`. Datos de la demo: `resultados.json`, `evaluacion_adicional.json`, `perfil_demografico.json` y geometría simplificada, todo incrustado en `data/datos_embebidos.js`.

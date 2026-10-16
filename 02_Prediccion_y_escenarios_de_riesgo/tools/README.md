# Herramientas de desarrollo

Desde la raíz del repositorio:

| Comando | Propósito |
| --- | --- |
| `python 02_Prediccion_y_escenarios_de_riesgo/tools/construir_web.py` | Compilar las fuentes de demo6 en paquetes JS/CSS y registrar sus hashes |
| `python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py --build` | Servir el workspace en localhost:8000 y mostrar la URL de demo6 |
| `python 02_Prediccion_y_escenarios_de_riesgo/tools/servir_demo.py --port 8765` | Elegir otro puerto |
| `python 02_Prediccion_y_escenarios_de_riesgo/tools/inventario.py` | Registrar fuentes y referencias HTML en `arquitectura/inventario.json` |

Estas herramientas utilizan solo la biblioteca estándar. El inventario no ejecuta modelos, pruebas ni navegador. El servidor se limita a `127.0.0.1` y se detiene con Ctrl+C.

Los generadores conservan sus rutas originales porque algunas forman parte de la procedencia del experimento:

- `modelado/comparar_modelos.py`: experimento de cuatro familias.
- `modelado/publicar_comparacion_demo6.py`: publicación de resultados.
- `modelado/generar_fichas_estatales.py`: contexto descriptivo de las entidades.
- `demo/preparar_datos.py`: preparación histórica de recursos locales.
- `entrega/generar_caso.cjs`, `entrega/reporte/generar_reporte.py` y `entrega/presentacion/generar_presentacion.py`: entregables.

No ejecutar todos los generadores por defecto: la preparación histórica y la publicación actual tienen responsabilidades y fuentes distintas. Seguir las instrucciones del documento correspondiente.

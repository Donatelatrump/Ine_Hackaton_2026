# Herramientas de Umbral

Ejecutar desde la raíz del proyecto con Python 3:

```powershell
python umbral/tools/construir_demo7.py
python umbral/tools/servir_demo.py --build
python umbral/tools/inventario.py
```

El servidor opcional muestra Umbral en `http://127.0.0.1:8000/`; se detiene con Ctrl+C. Usa `--port 8765` para elegir otro puerto. Abrir `index.html` directamente no requiere servidor.

Los generadores de modelos y documentos se conservan junto a sus insumos. No es necesario ejecutarlos para consultar la aplicación. Para empaquetar, usa `python tools/empaquetar_proyecto.py` desde la raíz.

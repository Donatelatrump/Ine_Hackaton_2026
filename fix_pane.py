#!/usr/bin/env python
# Fixed encoding version
with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace
old = "map.createPane('municipal-geography');"
new = "map.createPane('municipal-geography');\nmap.createPane('tile-pane');"

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success: Added tile-pane creation")
else:
    print("Pattern not found, searching for municipal-geography...")
    idx = content.find("municipal-geography")
    if idx >= 0:
        print(f"Found at index {idx}: {repr(content[idx:idx+50])}")
    else:
        print("municipal-geography not found either")
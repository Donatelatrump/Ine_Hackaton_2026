#!/usr/bin/env python
with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'rb') as f:
    content = f.read()

# Search for createPane with any quote style
patterns = [
    b"createPane('municipal-geography')",
    b'createPane("municipal-geography")',
    b"createPane('municipal-geography')\n",
    b'createPane("municipal-geography")\n',
]

found = False
for pattern in patterns:
    idx = content.find(pattern)
    if idx >= 0:
        print(f'Found pattern: {pattern}')
        print('Context bytes:', repr(content[idx-10:idx+60]))
        found = True
        # Replace it
        new_pattern = b"createPane('municipal-geography');\nmap.createPane('tile-pane');"
        if pattern in content[:idx+100]:
            # Found near the right area, do replacement
            content = content.replace(pattern, new_pattern)
            with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'wb') as f:
                f.write(content)
            print('Replacement done!')
        break

if not found:
    # Try searching more broadly for municipal-geography
    idx = content.find(b'municipal-geography')
    if idx >= 0:
        print(f'municipal-geography found at byte {idx}')
        print('Context:', repr(content[idx-30:idx+50]))
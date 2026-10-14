#!/usr/bin/env python
with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'rb') as f:
    content = f.read()

# The exact pattern found: pane:'municipal-geography'
# We need to add map.createPane('tile-pane') after map.createPane('municipal-geography')

# Find the line with createPane and municipal-geography
old = b"pane:'municipal-geography'"
idx = content.find(old)
if idx >= 0:
    # Find the start of this line (look backwards for the semicolon or map.createPane)
    # The pattern is inside L.geoJSON options: renderer:L.canvas({pane:'municipal-geography'})
    # We need to add map.createPane('tile-pane'); somewhere appropriate
    
    # Let's find map.createPane('municipal-geography') 
    old2 = b"map.createPane('municipal-geography')"
    idx2 = content.find(old2)
    if idx2 >= 0:
        # Add after this line
        new = b"map.createPane('municipal-geography');\nmap.createPane('tile-pane');"
        content = content.replace(old2, new)
        with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'wb') as f:
            f.write(content)
        print('Success: Added tile-pane creation after municipal-geography')
    else:
        print('map.createPane(\"municipal-geography\") not found, trying alternative...')
        # Try to find any createPane and add tile-pane after it
        idx3 = content.find(b"createPane")
        if idx3 >= 0:
            # Find the end of this createPane call
            idx4 = content.find(b";", idx3)
            if idx4 >= 0:
                old3 = content[idx3:idx4+1]
                new3 = old3 + b"\nmap.createPane('tile-pane');"
                content = content.replace(old3, new3)
                with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\aplicacion.js', 'wb') as f:
                    f.write(content)
                print('Success: Added tile-pane after createPane')
            else:
                print('Could not find semicolon after createPane')
        else:
            print('createPane not found at all')
else:
    print('pane:\"municipal-geography\" not found in expected context')
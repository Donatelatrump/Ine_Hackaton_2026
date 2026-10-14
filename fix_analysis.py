with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove panel class from analysis
content = content.replace('<section class="analysis panel" id="paso-2">', '<section class="analysis" id="paso-2">')

with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Removed panel class from analysis')
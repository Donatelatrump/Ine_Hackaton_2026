with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<section class="analysis" id="paso-2">', '<section class="analysis panel" id="paso-2">')

with open(r'C:\Users\Donnet\Desktop\Ine_Hackaton\02_Prediccion_y_escenarios_de_riesgo\demo\index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Added panel class back to analysis')
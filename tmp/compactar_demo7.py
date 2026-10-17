from pathlib import Path
import re

demo=Path(__file__).resolve().parents[1]/'02_Prediccion_y_escenarios_de_riesgo/demo'
path=demo/'demo7.html'
html=path.read_text(encoding='utf-8')
if 'id="d7-impact-caption"' in html:
    raise SystemExit('La presentación compacta ya está integrada.')
def disclose(element_id,tag,title):
    global html
    pattern=rf'(<{tag}\b[^>]*\bid="{element_id}"[^>]*>.*?</{tag}>)'
    html,n=re.subn(pattern,lambda m:f'<details class="d7-inline-details"><summary>{title}</summary>{m[1]}</details>',html,count=1,flags=re.S)
    if n!=1:raise ValueError('Missing element: '+element_id)
disclose('d6-plan-comparison-note','p','Supuestos y límites del cálculo')
disclose('d7-action-assumption','p','Origen de los valores iniciales')
disclose('d7-map-explanation','p','Cómo leer el mapa')
disclose('action-evidence','div','Evidencia de la acción')
disclose('d6-preset-note','p','Detalles del ejemplo')
disclose('d6-model-note','p','Cómo se eligió el modelo')
html=html.replace('<div class="d6-plan-comparison-values" id="d6-plan-comparison-values">','<p id="d7-impact-caption" class="d6-note">Escenario hipotético de una actividad del plan.</p><div class="d6-plan-comparison-values" id="d6-plan-comparison-values">',1)
html=html.replace('Selecciona una actividad, define personas alcanzadas y ajusta el efecto supuesto entre quienes reciben la acción. Se calcula una actividad a la vez; sus efectos no se suman.','Elige una actividad y ajusta alcance y efecto. Se calcula una a la vez.')
html=html.replace('Revisa el diagnóstico y las acciones propuestas. En la misma tarjeta, configura cobertura y compara escenarios con el mismo método de predicción.','Revisa el plan estatal, su impacto estimado y la distribución municipal.')
html=html.replace('Recurso mostrado: personas que se supone alcanzar. No representa presupuesto monetario ni capacidad confirmada. La prioridad depende del criterio elegido.','Cobertura expresada en personas; capacidad supuesta.')
html=html.replace('v=7-visible-change','v=7-compact')
path.write_text(html,encoding='utf-8')
print('Long explanations moved to disclosure panels; main controls and figures remain visible.')

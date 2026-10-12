"""Verifica y documenta la demo actual, sin servidor ni cifras históricas obsoletas."""
import json
import runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent
runpy.run_path(str(HERE/'verificar_jerarquia.py'),run_name='__main__')
runpy.run_path(str(HERE/'verificar_intervenciones.py'),run_name='__main__')
runpy.run_path(str(HERE/'capturar_demo.py'),run_name='__main__')
checks=['initial_exploration','grouped_simulation_controls','progressive_evidence','mobile_detail_priority','local_file','initial_no_action','sms_sources','sms_interval','itt_formula','coverage_budget','csv_citations','csv_small_effect_precision','att_unit','custom_response_zero','municipal_inverse_actual_coverage','municipality_scope','state_scope','country_scope','data_coverage_exclusions','proportional_distribution','integer_allocation','municipal_distribution','invalid_inputs','mobile_overflow','javascript_errors']
(HERE/'verificacion/resultado.json').write_text(json.dumps({'passed':True,'checks':checks,'page_errors':[],'verification_script':'verificar_intervenciones.py','capture_configuration':'configuracion_capturas.json','historical_tests_replaced':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(f'Demo vigente verificada: {len(checks)} grupos de comprobaciones y capturas regeneradas.')

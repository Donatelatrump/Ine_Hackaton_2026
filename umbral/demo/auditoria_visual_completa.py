"""Recorrido ampliado de controles y vistas, reutilizando la aceptación de Edge."""
from pathlib import Path
p=Path(__file__).with_name('verificar_demo7.py').resolve()
extra=Path(__file__).with_name('recorrido_visual_completo.py').read_text(encoding='utf-8')
s=p.read_text(encoding='utf-8')
s=s.replace("    sources=['demo7.html'",'    exec('+repr(extra)+', globals(), globals())\n    sources=[\'demo7.html\'')
exec(compile(s,str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})

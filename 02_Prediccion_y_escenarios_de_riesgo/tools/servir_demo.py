"""Sirve desde la raíz compartida para resolver documentos locales de las fichas."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import argparse

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--build',action='store_true',help='Reconstruir los recursos de demo6 antes de servir')
    args=parser.parse_args()
    if args.build:
        from construir_web import main as build_web
        build_web()
    handler=partial(SimpleHTTPRequestHandler,directory=str(ROOT))
    with ThreadingHTTPServer(('127.0.0.1',args.port),handler) as server:
        print(f'Umbral: http://127.0.0.1:{args.port}/02_Prediccion_y_escenarios_de_riesgo/demo/demo6.html',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass

if __name__=='__main__':main()

"""Genera la cartografía de la demo a partir del shapefile CONABIO/INEGI AGEM 2024.

Salidas (todas desde la MISMA fuente, para que estado y municipio compartan línea de límite):
  02_Prediccion_y_escenarios_de_riesgo/demo/data/municipios.geojson          (capa que dibuja la demo)
  02_Prediccion_y_escenarios_de_riesgo/demo/data/municipios_conabio.geojson  (copia con nombres INE)
  02_Prediccion_y_escenarios_de_riesgo/demo/data/estados.js                  (window.UMBRAL_STATES)

El límite estatal se obtiene disolviendo los polígonos municipales oficiales por
entidad (make_valid + union_all). No se aplican buffers ni erosiones: en los
estados de prueba (09, 23, 02) el union produce geometrías válidas sin huecos, y
el buffer previo añadía ~0.02–0.09% de área artificial redondeando esquinas.

Solo se simplifica con preservación de topología para reducir tamaño; la
tolerancia es un parámetro, no una deformación de los límites oficiales.

Regenera también demo/data/datos_embebidos.js si se pasa --embebidos, porque la demo
lee la geometría desde ese archivo y no desde municipios.geojson.

Uso:
  python process_conabio.py --tolerancia-municipios 0.002 --embebidos
  python process_conabio.py --solo-estados      # regenera solo estados.js

La fuente CONABIO es INEGI AGEM 2024 reproyectada a WGS84; requiere citar la
fuente (licencia CC BY-NC 2.5 MX, ver cartografia/municipiosmx_conabio/municipiosmx.xml).
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.task_packages'))
import geopandas as gpd
from shapely import make_valid, union_all
from shapely.geometry import mapping

TRACK = ROOT / '02_Prediccion_y_escenarios_de_riesgo'
SHP = TRACK / 'cartografia' / 'municipiosmx_conabio' / 'municipiosmx.shp'
DEMO_DATA = TRACK / 'demo' / 'data'
RESULTADOS = DEMO_DATA / 'resultados.json'

def fix_mojibake(texto):
    """El DBF del shapefile está doblemente mal codificado (UTF-8 leído como CP1252)."""
    try:
        # Latin-1 conserva también bytes C1 como 0x81, que CP1252 no puede codificar.
        return texto.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def normalizar(texto):
    texto = ''.join(c for c in unicodedata.normalize('NFD', fix_mojibake(texto).upper())
                    if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^A-Z0-9]', '', texto)


ALIAS_NOMBRES = {
    'CINTALAPADEFIGUEROA': 'CINTALAPA',
    'GENERALSIMONBOLIVAR': 'SIMONBOLIVAR',
    'JONACATEPECDELEANDROVALLE': 'JONACATEPEC',
    'ELCARMEN': 'CARMEN',
    'HEROICAVILLATEZOATLANDESEGURAYLUNACUNADELAINDEPENDENCIADEOAXACA':
        'HVILLATEZOATLANSEGURAYLUNACUNAINDOAX',
    'VILLADESANTIAGOCHAZUMBA': 'SANTIAGOCHAZUMBA',
    'HEROICOSANMARTINDELOSCANSECOS': 'SANMARTINDELOSCANSECOS',
    'AHUALULCODELSONIDO13': 'AHUALULCO',
    'ZILTLALTEPECDETRINIDADSANCHEZSANTOS': 'ZITLALTEPECDETRINIDADSANCHEZSANTOS',
    'COSAMALOAPANDECARPIO': 'COSAMALOAPAN',
    'ZONTECOMATLANDELOPEZYFUENTES': 'ZONTECOMATLAN',
    'OZULUAMADEMASCARENAS': 'OZULUAMA',
}

# La base del modelo conserva el municipio anterior a la creación de Villa de Pozos.
# Se integra su polígono al San Luis Potosí histórico para mantener las 2,477 claves.
REAGREGAR_A_BASE = {('24', 'VILLADEPOZOS'): '24028'}


def normalizar_para_cruce(texto):
    nombre = re.sub(r'DTO\d+', '', normalizar(texto))
    nombre = ALIAS_NOMBRES.get(nombre, nombre)
    return nombre.replace('GENERAL', 'GRAL').replace('DOCTOR', 'DR')


def base_por_estado():
    """{estado: {nombre_normalizado: [clave_base]}} y {clave_base: nombre_normalizado}."""
    filas = json.loads(RESULTADOS.read_text(encoding='utf-8'))['municipios']
    tabla, nombres = {}, {}
    for m in filas:
        nombre = normalizar(m.get('name', ''))
        tabla.setdefault(m['state'], {}).setdefault(nombre, []).append(m['key'])
        nombres[m['key']] = nombre
    return tabla, nombres


def remapear_por_nombre(gdf):
    """Asocia los polígonos con las claves de resultados por nombre dentro de la entidad.

    Los dos cortes numeran algunos municipios en distinto orden. Los nombres se comparan
    tras normalizar acentos, abreviaturas y alias oficiales. Cuando un nombre se repite,
    ambos listados se ordenan por clave y se emparejan en ese orden. Villa de Pozos se
    agrega al San Luis Potosí de la base, cuyo corte aún no contiene la nueva clave.
    """
    _, nombres = base_por_estado()
    grupos_base = defaultdict(list)
    for clave, nombre in nombres.items():
        grupos_base[(clave[:2], normalizar_para_cruce(nombre))].append(clave)

    grupos_fuente = defaultdict(list)
    pares = {}
    for _, row in gdf.iterrows():
        clave = row['clave_municipio_ine']
        grupo = (clave[:2], normalizar_para_cruce(row['nom_mun']))
        if grupo not in grupos_base and grupo in REAGREGAR_A_BASE:
            destino = REAGREGAR_A_BASE[grupo]
            assert destino in nombres and destino[:2] == grupo[0], (
                f'La clave de agregación {destino} no existe en la base para {grupo[0]}'
            )
            pares[clave] = destino
        else:
            grupos_fuente[grupo].append(clave)

    for grupo in sorted(set(grupos_fuente) | set(grupos_base)):
        fuente = sorted(grupos_fuente.get(grupo, []))
        base = sorted(grupos_base.get(grupo, []))
        assert len(fuente) == len(base), (
            f'No coincide el grupo {grupo}: fuente={fuente}, base={base}'
        )
        pares.update(zip(fuente, base))

    assert len(pares) == len(gdf), 'El remapeo no cubrió todos los polígonos'
    assert set(pares.values()) == set(nombres), 'El remapeo no cubrió todas las claves de la base'
    return pares


def clean(geometry):
    return make_valid(geometry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tolerancia-estados', type=float, default=0.002,
                        help='Simplificación de estados en grados (~220 m); 0 = exacto.')
    parser.add_argument('--tolerancia-municipios', type=float, default=0.0,
                        help='Simplificación de municipios_conabio.geojson; 0 = sin simplificar.')
    parser.add_argument('--solo-estados', action='store_true')
    parser.add_argument('--embebidos', action='store_true',
                        help='Regenera demo/data/datos_embebidos.js con la nueva geometría.')
    args = parser.parse_args()

    assert SHP.exists(), f'No se encontró {SHP}'
    gdf = gpd.read_file(SHP)
    assert gdf.crs is not None and gdf.crs.to_epsg() == 4326, f'CRS inesperado: {gdf.crs}'
    gdf['clave_municipio_ine'] = gdf['cve_ent'].astype(str).str.zfill(2) + gdf['cve_mun'].astype(str).str.zfill(3)
    gdf['entidad_ine'] = gdf['clave_municipio_ine'].str[:2]
    gdf['municipio_ine'] = gdf['clave_municipio_ine'].str[2:]
    assert gdf['clave_municipio_ine'].is_unique
    assert all(gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon']))
    assert gdf.geometry.is_valid.all()

    # La geometría se asocia con la clave de la base en `properties.key`, que usa la demo.
    remap_vals = remapear_por_nombre(gdf)
    gdf['clave_demo'] = gdf['clave_municipio_ine'].map(remap_vals)
    claves_base = {m['key'] for m in json.loads(RESULTADOS.read_text(encoding='utf-8'))['municipios']}
    assert set(gdf['clave_demo']) == claves_base, 'La capa no coincide con las claves de la base'
    conteo_claves = gdf['clave_demo'].value_counts()
    agregadas = sorted(conteo_claves[conteo_claves > 1].index)
    assert agregadas == ['24028'], f'Agregaciones inesperadas: {agregadas}'
    faltantes = claves_base - set(gdf['clave_demo'])
    assert not faltantes, f'La base tiene {len(faltantes)} claves sin polígono: {sorted(faltantes)}'
    renombrados = int((gdf['clave_demo'] != gdf['clave_municipio_ine']).sum())
    print(f'Vinculación por nombre: {len(gdf) - renombrados} polígonos conservan su clave y '
          f'{renombrados} se ajustan al corte de la base; Villa de Pozos se agrega a 24028.', flush=True)

    DEMO_DATA.mkdir(parents=True, exist_ok=True)

    if not args.solo_estados:
        features = []
        for key, grupo in gdf.groupby('clave_demo', sort=True):
            row = grupo.sort_values('clave_municipio_ine').iloc[0]
            claves_inegi = sorted(grupo['clave_municipio_ine'])
            geometry = clean(union_all([clean(g) for g in grupo.geometry]))
            if args.tolerancia_municipios > 0:
                geometry = geometry.simplify(args.tolerancia_municipios, preserve_topology=True)
            assert not geometry.is_empty and geometry.geom_type in ('Polygon', 'MultiPolygon')
            propiedades = {'key': key, 'entidad_ine': key[:2],
                           'municipio_ine': key[2:],
                           'municipio_nombre': fix_mojibake(row['nom_mun']),
                           'clave_inegi': claves_inegi[0]}
            if len(claves_inegi) > 1:
                propiedades['claves_inegi'] = claves_inegi
            features.append({'type': 'Feature', 'id': key,
                             'properties': propiedades,
                             'geometry': mapping(geometry)})
        collection_mun = {'type': 'FeatureCollection', 'features': features}
        for name in ('municipios.geojson', 'municipios_conabio.geojson'):
            output = DEMO_DATA / name
            output.write_text(json.dumps(collection_mun, ensure_ascii=False, separators=(',', ':')),
                              encoding='utf-8')
            print(f'Municipios: {len(features)} features -> {output} '
                  f'({output.stat().st_size / 1024 / 1024:.1f} MB, tolerancia {args.tolerancia_municipios})', flush=True)
        if args.embebidos:
            embed_municipal_geometry(DEMO_DATA, collection_mun)

    # El límite estatal se disuelve desde la MISMA geometría municipal que dibuja la demo, para que
    # las dos capas compartan línea de límite. Agrupar por la clave de la base conserva la renumeración.
    states = []
    for estado, sub in gdf.groupby('entidad_ine'):
        geometry = union_all([clean(g) for g in sub.geometry])
        geometry = make_valid(geometry)
        if args.tolerancia_estados > 0:
            geometry = geometry.simplify(args.tolerancia_estados, preserve_topology=True)
        assert not geometry.is_empty and geometry.geom_type in ('Polygon', 'MultiPolygon'), estado
        states.append({'type': 'Feature', 'properties': {'state': estado}, 'geometry': mapping(geometry)})
    states.sort(key=lambda f: f['properties']['state'])
    assert len(states) == 32, f'Se esperaban 32 entidades, salieron {len(states)}'
    collection = {'type': 'FeatureCollection', 'features': states}
    payload = json.dumps(collection, ensure_ascii=False, separators=(',', ':'))
    output = DEMO_DATA / 'estados.js'
    output.write_text('window.UMBRAL_STATES=' + payload + ';\n', encoding='utf-8')
    print(f'Estados: {len(states)} entidades -> {output} '
          f'({output.stat().st_size / 1024:.0f} KB, tolerancia {args.tolerancia_estados})', flush=True)

    (DEMO_DATA / 'cartografia_metadatos.json').write_text(json.dumps({
        'fuente': 'CONABIO/INEGI, Áreas geoestadísticas municipales (AGEM) 2024, escala 1:250000',
        'licencia': 'CC BY-NC 2.5 MX — citar INEGI y CONABIO',
        'crs': 'WGS84 EPSG:4326',
        'shapefile': str(SHP.relative_to(ROOT)),
        'municipios_originales': int(len(gdf)),
        'municipios_salida': int(len(claves_base)),
        'tolerancia_estados_grados': args.tolerancia_estados,
        'tolerancia_municipios_grados': args.tolerancia_municipios,
        'vinculacion': 'nombres normalizados y alias explícitos por entidad; homónimos emparejados por orden de clave',
        'agregaciones': [{'claves_conabio': ['24028', '24059'], 'clave_base': '24028',
                          'motivo': 'Villa de Pozos se integra al San Luis Potosí del corte de la base'}],
        'claves_con_estimacion': len(claves_base),
        'poligonos_sin_estimacion': len(set(gdf['clave_demo']) - claves_base),
        'fecha_generacion': date.today().isoformat(),
        'advertencia': 'Capa de referencia visual. Los límites oficiales vigentes son los del INEGI; '
                       'la coincidencia de claves no demuestra estabilidad de límites históricos.'
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Metadatos escritos.', flush=True)


def embed_municipal_geometry(demo_data, collection):
    """Sustituye la línea window.UMBRAL_GEO de datos_embebidos.js; conserva datos y perfil."""
    path = demo_data / 'datos_embebidos.js'
    lines = path.read_text(encoding='utf-8').splitlines()
    marker = 'window.UMBRAL_GEO='
    payload = marker + json.dumps(collection, ensure_ascii=True, separators=(',', ':')) + ';'
    hits = [i for i, line in enumerate(lines) if line.startswith(marker)]
    assert len(hits) == 1, f'Se esperaba una sola línea {marker}, hay {len(hits)}'
    lines[hits[0]] = payload
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'datos_embebidos.js: UMBRAL_GEO actualizado ({len(payload) / 1024 / 1024:.1f} MB)', flush=True)


if __name__ == '__main__':
    main()

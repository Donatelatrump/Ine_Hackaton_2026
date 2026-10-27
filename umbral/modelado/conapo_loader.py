"""Carga y procesa proyecciones CONAPO municipales para features demográficos."""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # Subir a Ine_Hackaton/
CONAPO_DIR = ROOT / 'fuentes' / 'Bases_de_datos_explicativos'

def load_conapo_ggrupos():
    """Carga pobproy_ggrupos.csv y agrega HOMBRES+MUJERES por municipio-año.
    
    Returns:
        dict: {clave_municipio_5d: {año: {POB_00_011, POB_012_29, POB_30_59, POB_60_mm, POB_TOTAL}}}
    """
    path = CONAPO_DIR / 'pobproy_ggrupos.csv'
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # Agregar sexos
    agg = df.groupby(['CLAVE', 'ANO'], as_index=False).agg({
        'POB_00_011': 'sum',
        'POB_012_29': 'sum',
        'POB_30_59': 'sum',
        'POB_60_mm': 'sum',
        'POB_TOTAL': 'sum',
    })
    
    # Indexar por clave (string 5 dígitos) y año
    result = {}
    for _, row in agg.iterrows():
        clave = str(int(row['CLAVE'])).zfill(5)
        año = int(row['ANO'])
        if clave not in result:
            result[clave] = {}
        result[clave][año] = {
            'POB_00_011': float(row['POB_00_011']),
            'POB_012_29': float(row['POB_012_29']),
            'POB_30_59': float(row['POB_30_59']),
            'POB_60_mm': float(row['POB_60_mm']),
            'POB_TOTAL': float(row['POB_TOTAL']),
        }
    return result


def load_conapo_quinq1():
    """Carga pobproy_quinq1.csv y agrega HOMBRES+MUJERES por municipio-año.
    
    Returns:
        dict: {clave_municipio_5d: {año: {POB_00_04, POB_05_09, ..., POB_85_mm}}}
    """
    path = CONAPO_DIR / 'pobproy_quinq1.csv'
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    # Columnas quinquenales
    quin_cols = [c for c in df.columns if c.startswith('POB_')]
    
    agg = df.groupby(['CLAVE', 'ANO'], as_index=False)[quin_cols].sum()
    
    result = {}
    for _, row in agg.iterrows():
        clave = str(int(row['CLAVE'])).zfill(5)
        año = int(row['ANO'])
        if clave not in result:
            result[clave] = {}
        result[clave][año] = {c: float(row[c]) for c in quin_cols}
    return result


def load_conapo_inddemo():
    """Carga pobproy_inddemo.csv (ya viene agregado municipal, un registro por sexo-año).
    
    Promedia índices entre sexos.
    """
    path = CONAPO_DIR / 'pobproy_inddemo.csv'
    df = pd.read_csv(path, encoding='utf-8-sig')
    
    idx_cols = ['EDAD_MED', 'IND_ENV_60', 'IND_ENV_65', 
                'RAZ_DEP_ADU', 'RAZ_DEP_INF', 'RAZ_DEP', 'RHM']
    
    agg = df.groupby(['CLAVE', 'ANO'], as_index=False)[idx_cols].mean()
    
    result = {}
    for _, row in agg.iterrows():
        clave = str(int(row['CLAVE'])).zfill(5)
        año = int(row['ANO'])
        if clave not in result:
            result[clave] = {}
        result[clave][año] = {c: float(row[c]) for c in idx_cols}
    return result


def get_projected_demographics(clave, target_year, conapo_ggrupos, conapo_quinq1=None):
    """Obtiene features demográficos proyectados para un municipio-año.
    
    Args:
        clave: str, clave municipal 5 dígitos
        target_year: int, año objetivo (ej. 2027)
        conapo_ggrupos: dict from load_conapo_ggrupos()
        conapo_quinq1: dict from load_conapo_quinq1() (optional, para 18-29 exacto)
    
    Returns:
        dict con keys: prop_18_29, prop_60_mas, prop_0_11, prop_30_59, 
                       log_crecimiento_pob (vs 2024), pob_total_proy
        None si no hay datos
    """
    if clave not in conapo_ggrupos:
        return None
    datos = conapo_ggrupos[clave]
    if target_year not in datos or 2024 not in datos:
        return None
    
    proy = datos[target_year]
    base = datos[2024]
    
    pob_total_proy = proy['POB_TOTAL']
    pob_total_base = base['POB_TOTAL']
    
    # Proporciones proyectadas
    prop_18_29 = proy['POB_012_29'] / pob_total_proy if pob_total_proy > 0 else 0
    prop_60_mas = proy['POB_60_mm'] / pob_total_proy if pob_total_proy > 0 else 0
    prop_0_11 = proy['POB_00_011'] / pob_total_proy if pob_total_proy > 0 else 0
    prop_30_59 = proy['POB_30_59'] / pob_total_proy if pob_total_proy > 0 else 0
    
    # Crecimiento poblacional 2024->target (log)
    log_crecimiento = 0.0
    if pob_total_base > 0 and pob_total_proy > 0:
        import math
        log_crecimiento = math.log(pob_total_proy / pob_total_base)
    
    # Si tenemos quinquenales, recalcular 18-29 exacto (15-19 + 20-24 + 25-29)
    if conapo_quinq1 and clave in conapo_quinq1 and target_year in conapo_quinq1[clave]:
        q = conapo_quinq1[clave][target_year]
        pob_18_29 = q.get('POB_015_019', 0) + q.get('POB_020_24', 0) + q.get('POB_025_29', 0)
        if pob_total_proy > 0:
            prop_18_29 = pob_18_29 / pob_total_proy
    
    return {
        'prop_18_29_proy': prop_18_29,
        'prop_60_mas_proy': prop_60_mas,
        'prop_0_11_proy': prop_0_11,
        'prop_30_59_proy': prop_30_59,
        'log_crecimiento_pob_proy': log_crecimiento,
        'pob_total_proy': pob_total_proy,
    }


# Cache global
_CONAPO_GGRUPOS = None
_CONAPO_QUINQ1 = None
_CONAPO_INDEMO = None

def get_conapo_ggrupos():
    global _CONAPO_GGRUPOS
    if _CONAPO_GGRUPOS is None:
        _CONAPO_GGRUPOS = load_conapo_ggrupos()
    return _CONAPO_GGRUPOS

def get_conapo_quinq1():
    global _CONAPO_QUINQ1
    if _CONAPO_QUINQ1 is None:
        _CONAPO_QUINQ1 = load_conapo_quinq1()
    return _CONAPO_QUINQ1

def get_conapo_inddemo():
    global _CONAPO_INDEMO
    if _CONAPO_INDEMO is None:
        _CONAPO_INDEMO = load_conapo_inddemo()
    return _CONAPO_INDEMO

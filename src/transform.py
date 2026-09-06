import pandas as pd
import numpy as np
from .config import MESES
import logging

logger = logging.getLogger(__name__)

def clean_afiliados(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando dataset de afiliados...")
    
    df['num_personas'] = df['num_personas'].str.replace('.', '', regex=False)
    df['num_personas'] = pd.to_numeric(df['num_personas'], errors='coerce').fillna(0).astype(int)
    
    df['anio'] = df['anio'].astype(int)
    df['mes'] = df['mes'].astype(int)
    
    df = df[df['num_personas'] > 0].copy()
    
    logger.info(f"Registros después de limpieza: {len(df)}")
    return df

def clean_ips(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Limpiando dataset de IPS...")
    
    df['nivel_atencion'] = pd.to_numeric(df['nivel_atencion'], errors='coerce')
    df['cantidad_capacidad'] = pd.to_numeric(df['cantidad_capacidad'], errors='coerce').fillna(0).astype(int)
    
    df['nit'] = df['nit'].str.replace(',', '', regex=False)
    
    df = df.dropna(subset=['cod_prestador', 'nombre_prestador'])
    
    logger.info(f"Registros después de limpieza: {len(df)}")
    return df

def build_dim_tiempo(df_afiliados: pd.DataFrame, df_ips: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión tiempo...")
    
    meses_af = df_afiliados[['anio', 'mes']].drop_duplicates()
    
    fecha_corte = df_ips['fecha_corte'].dropna().unique()
    meses_ips = []
    for fc in fecha_corte:
        try:
            parts = fc.replace('Fecha corte REPS:', '').strip().split()
            month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
                        'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
            if len(parts) >= 3:
                m = month_map.get(parts[0], 1)
                y = int(parts[2])
                meses_ips.append({'anio': y, 'mes': m})
        except:
            pass
    
    df_meses_ips = pd.DataFrame(meses_ips) if meses_ips else pd.DataFrame(columns=['anio', 'mes'])
    dim_tiempo = pd.concat([meses_af, df_meses_ips]).drop_duplicates().reset_index(drop=True)
    
    dim_tiempo['nombre_mes'] = dim_tiempo['mes'].map(MESES)
    dim_tiempo['trimestre'] = (dim_tiempo['mes'] - 1) // 3 + 1
    dim_tiempo['semestre'] = np.where(dim_tiempo['mes'] <= 6, 1, 2)
    dim_tiempo['fecha_completa'] = pd.to_datetime(
        dim_tiempo['anio'].astype(str) + '-' + dim_tiempo['mes'].astype(str) + '-01'
    )
    
    dim_tiempo = dim_tiempo.sort_values(['anio', 'mes']).reset_index(drop=True)
    dim_tiempo['sk_tiempo'] = dim_tiempo.index + 1
    
    logger.info(f"Registros dim_tiempo: {len(dim_tiempo)}")
    return dim_tiempo

def build_dim_departamento(df_afiliados: pd.DataFrame, df_ips: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión departamento...")
    
    deptos_af = df_afiliados[['cod_depto', 'departamento']].drop_duplicates()
    deptos_af.columns = ['codigo', 'nombre']
    
    deptos_ips = df_ips[['departamento']].drop_duplicates()
    deptos_ips['codigo'] = deptos_ips['nombre'].str[:2].str.zfill(2)
    deptos_ips = deptos_ips[['codigo', 'nombre']]
    
    dim_dep = pd.concat([deptos_af, deptos_ips]).drop_duplicates(subset=['nombre']).reset_index(drop=True)
    dim_dep['sk_departamento'] = dim_dep.index + 1
    
    logger.info(f"Registros dim_departamento: {len(dim_dep)}")
    return dim_dep

def build_dim_municipio(df_afiliados: pd.DataFrame, df_ips: pd.DataFrame, 
                         dim_dep: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión municipio...")
    
    mun_af = df_afiliados[['cod_municipio', 'municipio', 'departamento']].drop_duplicates()
    mun_af.columns = ['codigo', 'nombre', 'depto_nombre']
    
    mun_ips = df_ips[['municipio', 'departamento']].drop_duplicates()
    mun_ips['codigo'] = mun_ips['municipio'].apply(lambda x: str(hash(x))[:8])
    mun_ips.columns = ['nombre', 'depto_nombre', 'codigo']
    mun_ips = mun_ips[['codigo', 'nombre', 'depto_nombre']]
    
    dim_mun = pd.concat([mun_af, mun_ips]).drop_duplicates(subset=['nombre', 'depto_nombre']).reset_index(drop=True)
    
    dep_map = dim_dep.set_index('nombre')['sk_departamento'].to_dict()
    dim_mun['sk_departamento'] = dim_mun['depto_nombre'].map(dep_map)
    dim_mun = dim_mun.dropna(subset=['sk_departamento'])
    dim_mun['sk_departamento'] = dim_mun['sk_departamento'].astype(int)
    
    dim_mun = dim_mun.drop(columns=['depto_nombre'])
    dim_mun['sk_municipio'] = dim_mun.index + 1
    
    logger.info(f"Registros dim_municipio: {len(dim_mun)}")
    return dim_mun

def build_dim_regimen(df_afiliados: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión régimen...")
    
    regimen_map = {
        'S': 'SUBSIDIADO',
        'E': 'ESPECIAL',
        'C': 'CONTRIBUTIVO'
    }
    
    dim_reg = df_afiliados[['id_regimen']].drop_duplicates().reset_index(drop=True)
    dim_reg.columns = ['codigo']
    dim_reg['descripcion'] = dim_reg['codigo'].map(regimen_map).fillna('DESCONOCIDO')
    dim_reg['sk_regimen'] = dim_reg.index + 1
    
    logger.info(f"Registros dim_regimen: {len(dim_reg)}")
    return dim_reg

def build_dim_ips(df_ips: pd.DataFrame, dim_mun: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión IPS...")
    
    dim_ips = df_ips[['cod_prestador', 'nombre_prestador', 'nit', 'naturaleza',
                       'nivel_atencion', 'gerente', 'direccion', 'email', 
                       'telefono', 'municipio']].drop_duplicates().reset_index(drop=True)
    
    dim_ips.columns = ['codigo_prestador', 'nombre', 'nit', 'naturaleza',
                        'nivel_atencion', 'gerente', 'direccion', 'email',
                        'telefono', 'municipio_nombre']
    
    mun_map = dim_mun.set_index('nombre')['sk_municipio'].to_dict()
    dim_ips['sk_municipio'] = dim_ips['municipio_nombre'].map(mun_map)
    dim_ips = dim_ips.dropna(subset=['sk_municipio'])
    dim_ips['sk_municipio'] = dim_ips['sk_municipio'].astype(int)
    
    dim_ips = dim_ips.drop(columns=['municipio_nombre'])
    dim_ips['sk_ips'] = dim_ips.index + 1
    
    logger.info(f"Registros dim_ips: {len(dim_ips)}")
    return dim_ips

def build_dim_tipo_capacidad(df_ips: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo dimensión tipo capacidad...")
    
    dim_tc = df_ips[['grupo_capacidad', 'desc_capacidad']].drop_duplicates().reset_index(drop=True)
    dim_tc.columns = ['grupo', 'descripcion']
    dim_tc['sk_tipo_capacidad'] = dim_tc.index + 1
    
    logger.info(f"Registros dim_tipo_capacidad: {len(dim_tc)}")
    return dim_tc

def build_fact_afiliados(df_afiliados: pd.DataFrame, dim_tiempo: pd.DataFrame,
                          dim_mun: pd.DataFrame, dim_reg: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo tabla de hechos afiliados...")
    
    tiempo_map = dim_tiempo.set_index(['anio', 'mes'])['sk_tiempo'].to_dict()
    mun_map = dim_mun.set_index('codigo')['sk_municipio'].to_dict()
    reg_map = dim_reg.set_index('codigo')['sk_regimen'].to_dict()
    
    fact = df_afiliados.copy()
    fact['sk_tiempo'] = fact.apply(lambda r: tiempo_map.get((r['anio'], r['mes'])), axis=1)
    fact['sk_municipio'] = fact['cod_municipio'].map(mun_map)
    fact['sk_regimen'] = fact['id_regimen'].map(reg_map)
    
    fact = fact.dropna(subset=['sk_tiempo', 'sk_municipio', 'sk_regimen'])
    fact['sk_tiempo'] = fact['sk_tiempo'].astype(int)
    fact['sk_municipio'] = fact['sk_municipio'].astype(int)
    fact['sk_regimen'] = fact['sk_regimen'].astype(int)
    
    fact = fact[['sk_tiempo', 'sk_municipio', 'sk_regimen', 'num_personas']]
    fact['sk_afiliado'] = fact.index + 1
    
    logger.info(f"Registros fact_afiliados: {len(fact)}")
    return fact

def build_fact_capacidad(df_ips: pd.DataFrame, dim_tiempo: pd.DataFrame,
                          dim_ips: pd.DataFrame, dim_tc: pd.DataFrame) -> pd.DataFrame:
    logger.info("Construyendo tabla de hechos capacidad...")
    
    tiempo_map = dim_tiempo.set_index(['anio', 'mes'])['sk_tiempo'].to_dict()
    
    df_ips_temp = df_ips.copy()
    df_ips_temp['anio'] = 2022
    df_ips_temp['mes'] = 11
    
    fact = df_ips_temp[['cod_prestador', 'municipio', 'grupo_capacidad', 'desc_capacidad',
                         'cantidad_capacidad', 'anio', 'mes']].copy()
    
    fact['sk_tiempo'] = fact.apply(lambda r: tiempo_map.get((r['anio'], r['mes'])), axis=1)
    
    ips_key = dim_ips.set_index(['codigo_prestador'])['sk_ips'].to_dict()
    fact['sk_ips'] = fact['cod_prestador'].map(ips_key)
    
    tc_key = dim_tc.set_index(['grupo', 'descripcion'])['sk_tipo_capacidad'].to_dict()
    fact['sk_tipo_capacidad'] = fact.apply(
        lambda r: tc_key.get((r['grupo_capacidad'], r['desc_capacidad'])), axis=1
    )
    
    fact = fact.dropna(subset=['sk_tiempo', 'sk_ips', 'sk_tipo_capacidad'])
    fact['sk_tiempo'] = fact['sk_tiempo'].astype(int)
    fact['sk_ips'] = fact['sk_ips'].astype(int)
    fact['sk_tipo_capacidad'] = fact['sk_tipo_capacidad'].astype(int)
    
    fact = fact[['sk_tiempo', 'sk_ips', 'sk_tipo_capacidad', 'cantidad_capacidad']]
    fact['sk_capacidad'] = fact.index + 1
    
    logger.info(f"Registros fact_capacidad: {len(fact)}")
    return fact
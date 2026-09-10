import pandas as pd
import numpy as np
from .config import (
    MONTHS, REGION_MAP, REGIME_MAP, DEPT_NORMALIZE,
    DEPT_DANE_CODES, normalize_text
)
import logging

logger = logging.getLogger(__name__)

def clean_affiliates(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning affiliates dataset...")
    
    df['num_persons'] = df['num_persons'].str.replace('.', '', regex=False)
    df['num_persons'] = pd.to_numeric(df['num_persons'], errors='coerce').fillna(0).astype(int)
    
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    
    df['department'] = df['department'].apply(normalize_text)
    df['municipality'] = df['municipality'].apply(normalize_text)
    
    df['department'] = df['department'].map(lambda x: DEPT_NORMALIZE.get(x, x))
    df = df.dropna(subset=['department'])
    
    df = df[df['num_persons'] > 0].copy()
    
    df['quarter'] = (df['month'] - 1) // 3 + 1
    df['periodo_codigo'] = df.apply(lambda r: f"{r['year']}-Q{r['quarter']}", axis=1)
    df['data_source'] = 'affiliates'
    df['data_snapshot_date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')
    
    logger.info(f"Records after cleaning: {len(df)}")
    return df

def clean_facilities(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning facilities dataset...")
    
    df['care_level'] = pd.to_numeric(df['care_level'], errors='coerce')
    df['installed_capacity'] = pd.to_numeric(df['installed_capacity'], errors='coerce').fillna(0).astype(int)
    
    df['nit'] = df['nit'].str.replace(',', '', regex=False)
    
    df['department'] = df['department'].apply(normalize_text)
    df['municipality'] = df['municipality'].apply(normalize_text)
    
    df['department'] = df['department'].map(lambda x: DEPT_NORMALIZE.get(x, x))
    df = df.dropna(subset=['department'])
    
    df = df.dropna(subset=['provider_code', 'provider_name'])
    
    df['data_source'] = 'facilities'
    df['data_snapshot_date'] = pd.to_datetime('2022-11-01')
    
    logger.info(f"Records after cleaning: {len(df)}")
    return df

def build_dim_time(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building time dimension...")
    
    time_records = []
    
    aff_periods = df_affiliates[['year', 'quarter']].drop_duplicates()
    for _, row in aff_periods.iterrows():
        time_records.append({
            'year': int(row['year']),
            'quarter': int(row['quarter']),
            'data_source': 'affiliates'
        })
    
    time_records.append({
        'year': 2022,
        'quarter': 4,
        'data_source': 'facilities'
    })
    
    dim_time = pd.DataFrame(time_records).drop_duplicates(subset=['year', 'quarter']).reset_index(drop=True)
    
    quarter_month_map = {1: 1, 2: 4, 3: 7, 4: 10}
    dim_time['month'] = dim_time['quarter'].map(quarter_month_map)
    dim_time['month_name'] = dim_time['month'].map(MONTHS)
    dim_time['semester'] = np.where(dim_time['quarter'] <= 2, 1, 2)
    dim_time['periodo_codigo'] = dim_time.apply(
        lambda r: f"{int(r['year'])}-Q{int(r['quarter'])}", axis=1
    )
    dim_time['full_date'] = pd.to_datetime(
        dim_time['year'].astype(str) + '-' + dim_time['month'].astype(str) + '-01'
    )
    dim_time = dim_time.drop(columns=['data_source'])
    
    dim_time = dim_time.sort_values(['year', 'quarter']).reset_index(drop=True)
    dim_time['sk_time'] = dim_time.index + 1
    
    logger.info(f"Time dimension records: {len(dim_time)}")
    return dim_time

def build_dim_geografia(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building geography dimension...")
    
    geo_aff = df_affiliates[['municipality_code', 'municipality', 'department_code',
                              'department', 'region']].drop_duplicates()
    geo_aff.columns = ['codigo_dane_municipio', 'municipio', 'codigo_dane_depto',
                        'departamento', 'region']
    
    dept_map = df_affiliates.drop_duplicates('department')[['department', 'department_code']].set_index('department')['department_code'].to_dict()
    
    geo_fac = df_facilities[['municipality', 'department']].drop_duplicates()
    geo_fac['codigo_dane_depto'] = geo_fac['department'].map(dept_map)
    geo_fac = geo_fac.dropna(subset=['codigo_dane_depto'])
    geo_fac['codigo_dane_municipio'] = geo_fac.apply(
        lambda r: f"{r['codigo_dane_depto']}{hash(r['municipality']) % 10000:04d}", axis=1
    )
    geo_fac['region'] = geo_fac['department'].map(REGION_MAP).fillna('Sin Region')
    geo_fac = geo_fac[['codigo_dane_municipio', 'municipio', 'codigo_dane_depto',
                        'departamento', 'region']]
    
    dim_geo = pd.concat([geo_aff, geo_fac]).drop_duplicates(
        subset=['codigo_dane_municipio']
    ).reset_index(drop=True)
    
    dim_geo['sk_geografia'] = dim_geo.index + 1
    
    logger.info(f"Geography dimension records: {len(dim_geo)}")
    return dim_geo

def build_dim_department(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building department dimension...")
    
    all_depts = set(df_affiliates['department'].unique()) | set(df_facilities['department'].unique())
    
    rows = []
    for dept in sorted(all_depts):
        code = DEPT_DANE_CODES.get(dept, df_affiliates[df_affiliates['department'] == dept]['department_code'].iloc[0]
                                   if dept in df_affiliates['department'].values else None)
        if code:
            rows.append({'code': code, 'name': dept})
    
    dim_dept = pd.DataFrame(rows).drop_duplicates(subset=['code']).reset_index(drop=True)
    dim_dept['sk_department'] = dim_dept.index + 1
    
    logger.info(f"Department dimension records: {len(dim_dept)}")
    return dim_dept

def build_dim_municipality(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame, 
                           dim_dept: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building municipality dimension...")
    
    mun_aff = df_affiliates[['municipality_code', 'municipality', 'department']].drop_duplicates()
    mun_aff.columns = ['code', 'name', 'dept_name']
    
    dept_to_sk = dim_dept.set_index('name')['sk_department'].to_dict()
    mun_aff['sk_department'] = mun_aff['dept_name'].map(dept_to_sk)
    mun_aff = mun_aff.drop(columns=['dept_name']).dropna(subset=['sk_department'])
    mun_aff['sk_department'] = mun_aff['sk_department'].astype(int)
    
    dim_mun = mun_aff.drop_duplicates(subset=['code']).reset_index(drop=True)
    dim_mun['sk_municipality'] = dim_mun.index + 1
    
    logger.info(f"Municipality dimension records: {len(dim_mun)}")
    return dim_mun

def build_dim_regime(df_affiliates: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building regime dimension...")
    
    dim_reg = df_affiliates[['regime_id']].drop_duplicates().reset_index(drop=True)
    dim_reg.columns = ['code']
    dim_reg['description'] = dim_reg['code'].map(REGIME_MAP).fillna('UNKNOWN')
    dim_reg['sk_regime'] = dim_reg.index + 1
    
    logger.info(f"Regime dimension records: {len(dim_reg)}")
    return dim_reg

def build_dim_facility(df_facilities: pd.DataFrame, dim_mun: pd.DataFrame,
                       dim_dept: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building facility dimension...")
    
    dim_fac = df_facilities[['provider_code', 'provider_name', 'nit', 'nature',
                              'care_level', 'manager', 'address', 'email', 
                              'phone', 'municipality', 'department']].drop_duplicates().reset_index(drop=True)
    
    dim_fac.columns = ['provider_code', 'name', 'nit', 'nature',
                        'care_level', 'manager', 'address', 'email',
                        'phone', 'municipality_name', 'dept_name']
    
    dept_to_sk = dim_dept.set_index('name')['sk_department'].to_dict()
    fac_muni_map = dim_mun.set_index(['name', 'sk_department'])['sk_municipality'].to_dict()
    
    dim_fac['sk_municipality'] = dim_fac.apply(
        lambda r: fac_muni_map.get((r['municipality_name'], dept_to_sk.get(r['dept_name']))), axis=1
    )
    dim_fac = dim_fac.dropna(subset=['sk_municipality'])
    dim_fac['sk_municipality'] = dim_fac['sk_municipality'].astype(int)
    
    dim_fac = dim_fac.drop(columns=['municipality_name', 'dept_name'])
    dim_fac['sk_facility'] = dim_fac.index + 1
    
    logger.info(f"Facility dimension records: {len(dim_fac)}")
    return dim_fac

def build_dim_capacity_type(df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building capacity type dimension...")
    
    dim_ct = df_facilities[['capacity_group', 'capacity_description']].drop_duplicates().reset_index(drop=True)
    dim_ct.columns = ['group', 'description']
    dim_ct['sk_capacity_type'] = dim_ct.index + 1
    
    logger.info(f"Capacity type dimension records: {len(dim_ct)}")
    return dim_ct

def build_fact_affiliates(df_affiliates: pd.DataFrame, dim_time: pd.DataFrame,
                          dim_geo: pd.DataFrame, dim_reg: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building affiliates fact table (quarterly granularity)...")
    
    time_map = dim_time.set_index(['year', 'quarter'])['sk_time'].to_dict()
    geo_map = dim_geo.set_index('codigo_dane_municipio')['sk_geografia'].to_dict()
    reg_map = dim_reg.set_index('code')['sk_regime'].to_dict()
    
    fact = df_affiliates.copy()
    fact['quarter'] = (fact['month'] - 1) // 3 + 1
    
    fact['sk_time'] = fact.apply(lambda r: time_map.get((r['year'], r['quarter'])), axis=1)
    fact['sk_geografia'] = fact['municipality_code'].map(geo_map)
    fact['sk_regime'] = fact['regime_id'].map(reg_map)
    
    fact = fact.dropna(subset=['sk_time', 'sk_geografia', 'sk_regime'])
    fact['sk_time'] = fact['sk_time'].astype(int)
    fact['sk_geografia'] = fact['sk_geografia'].astype(int)
    fact['sk_regime'] = fact['sk_regime'].astype(int)
    
    fact_agg = fact.groupby(['sk_time', 'sk_geografia', 'sk_regime']).agg(
        numero_afiliados=('num_persons', 'sum')
    ).reset_index()
    
    fact_agg['sk_affiliate'] = fact_agg.index + 1
    
    logger.info(f"Affiliates fact records (quarterly): {len(fact_agg)}")
    return fact_agg

def build_fact_facility_capacity(df_facilities: pd.DataFrame, dim_time: pd.DataFrame,
                                  dim_fac: pd.DataFrame, dim_ct: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building facility capacity fact table...")
    
    time_key = (2022, 4)
    sk_time_val = dim_time.set_index(['year', 'quarter']).loc[time_key, 'sk_time']
    if isinstance(sk_time_val, pd.Series):
        sk_time_val = sk_time_val.iloc[0]
    
    fact = df_facilities[['provider_code', 'capacity_group', 'capacity_description',
                           'installed_capacity']].copy()
    
    fac_key = dim_fac.set_index('provider_code')['sk_facility'].to_dict()
    fact['sk_facility'] = fact['provider_code'].map(fac_key)
    
    ct_key = dim_ct.set_index(['group', 'description'])['sk_capacity_type'].to_dict()
    fact['sk_capacity_type'] = fact.apply(
        lambda r: ct_key.get((r['capacity_group'], r['capacity_description'])), axis=1
    )
    
    fact['sk_time'] = sk_time_val
    
    fact = fact.dropna(subset=['sk_time', 'sk_facility', 'sk_capacity_type'])
    fact['sk_time'] = fact['sk_time'].astype(int)
    fact['sk_facility'] = fact['sk_facility'].astype(int)
    fact['sk_capacity_type'] = fact['sk_capacity_type'].astype(int)
    
    fact = fact[['sk_time', 'sk_facility', 'sk_capacity_type', 'installed_capacity']]
    fact['sk_capacity'] = fact.index + 1
    
    logger.info(f"Facility capacity fact records: {len(fact)}")
    return fact

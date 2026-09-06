import pandas as pd
import numpy as np
from .config import MONTHS
import logging

logger = logging.getLogger(__name__)

def clean_affiliates(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning affiliates dataset...")
    
    df['num_persons'] = df['num_persons'].str.replace('.', '', regex=False)
    df['num_persons'] = pd.to_numeric(df['num_persons'], errors='coerce').fillna(0).astype(int)
    
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    
    df = df[df['num_persons'] > 0].copy()
    
    logger.info(f"Records after cleaning: {len(df)}")
    return df

def clean_facilities(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Cleaning facilities dataset...")
    
    df['care_level'] = pd.to_numeric(df['care_level'], errors='coerce')
    df['installed_capacity'] = pd.to_numeric(df['installed_capacity'], errors='coerce').fillna(0).astype(int)
    
    df['nit'] = df['nit'].str.replace(',', '', regex=False)
    
    df = df.dropna(subset=['provider_code', 'provider_name'])
    
    logger.info(f"Records after cleaning: {len(df)}")
    return df

def build_dim_time(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building time dimension...")
    
    months_aff = df_affiliates[['year', 'month']].drop_duplicates()
    
    cutoff_date = df_facilities['cutoff_date'].dropna().unique()
    months_fac = []
    for cd in cutoff_date:
        try:
            parts = cd.replace('Fecha corte REPS:', '').strip().split()
            month_map = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
                        'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
            if len(parts) >= 3:
                m = month_map.get(parts[0], 1)
                y = int(parts[2])
                months_fac.append({'year': y, 'month': m})
        except:
            pass
    
    df_months_fac = pd.DataFrame(months_fac) if months_fac else pd.DataFrame(columns=['year', 'month'])
    dim_time = pd.concat([months_aff, df_months_fac]).drop_duplicates().reset_index(drop=True)
    
    dim_time['month_name'] = dim_time['month'].map(MONTHS)
    dim_time['quarter'] = (dim_time['month'] - 1) // 3 + 1
    dim_time['semester'] = np.where(dim_time['month'] <= 6, 1, 2)
    dim_time['full_date'] = pd.to_datetime(
        dim_time['year'].astype(str) + '-' + dim_time['month'].astype(str) + '-01'
    )
    
    dim_time = dim_time.sort_values(['year', 'month']).reset_index(drop=True)
    dim_time['sk_time'] = dim_time.index + 1
    
    logger.info(f"Time dimension records: {len(dim_time)}")
    return dim_time

def build_dim_department(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building department dimension...")
    
    depts_aff = df_affiliates[['department_code', 'department']].drop_duplicates()
    depts_aff.columns = ['code', 'name']
    
    depts_fac = df_facilities[['department']].drop_duplicates()
    depts_fac['code'] = depts_fac['name'].str[:2].str.zfill(2)
    depts_fac = depts_fac[['code', 'name']]
    
    dim_dept = pd.concat([depts_aff, depts_fac]).drop_duplicates(subset=['name']).reset_index(drop=True)
    dim_dept['sk_department'] = dim_dept.index + 1
    
    logger.info(f"Department dimension records: {len(dim_dept)}")
    return dim_dept

def build_dim_municipality(df_affiliates: pd.DataFrame, df_facilities: pd.DataFrame, 
                           dim_dept: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building municipality dimension...")
    
    mun_aff = df_affiliates[['municipality_code', 'municipality', 'department']].drop_duplicates()
    mun_aff.columns = ['code', 'name', 'dept_name']
    
    mun_fac = df_facilities[['municipality', 'department']].drop_duplicates()
    mun_fac['code'] = mun_fac['name'].apply(lambda x: str(hash(x))[:8])
    mun_fac.columns = ['name', 'dept_name', 'code']
    mun_fac = mun_fac[['code', 'name', 'dept_name']]
    
    dim_mun = pd.concat([mun_aff, mun_fac]).drop_duplicates(subset=['name', 'dept_name']).reset_index(drop=True)
    
    dept_map = dim_dept.set_index('name')['sk_department'].to_dict()
    dim_mun['sk_department'] = dim_mun['dept_name'].map(dept_map)
    dim_mun = dim_mun.dropna(subset=['sk_department'])
    dim_mun['sk_department'] = dim_mun['sk_department'].astype(int)
    
    dim_mun = dim_mun.drop(columns=['dept_name'])
    dim_mun['sk_municipality'] = dim_mun.index + 1
    
    logger.info(f"Municipality dimension records: {len(dim_mun)}")
    return dim_mun

def build_dim_regime(df_affiliates: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building regime dimension...")
    
    regime_map = {
        'S': 'SUBSIDIZED',
        'E': 'SPECIAL',
        'C': 'CONTRIBUTORY'
    }
    
    dim_reg = df_affiliates[['regime_id']].drop_duplicates().reset_index(drop=True)
    dim_reg.columns = ['code']
    dim_reg['description'] = dim_reg['code'].map(regime_map).fillna('UNKNOWN')
    dim_reg['sk_regime'] = dim_reg.index + 1
    
    logger.info(f"Regime dimension records: {len(dim_reg)}")
    return dim_reg

def build_dim_facility(df_facilities: pd.DataFrame, dim_mun: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building facility dimension...")
    
    dim_fac = df_facilities[['provider_code', 'provider_name', 'nit', 'nature',
                              'care_level', 'manager', 'address', 'email', 
                              'phone', 'municipality']].drop_duplicates().reset_index(drop=True)
    
    dim_fac.columns = ['provider_code', 'name', 'nit', 'nature',
                        'care_level', 'manager', 'address', 'email',
                        'phone', 'municipality_name']
    
    mun_map = dim_mun.set_index('name')['sk_municipality'].to_dict()
    dim_fac['sk_municipality'] = dim_fac['municipality_name'].map(mun_map)
    dim_fac = dim_fac.dropna(subset=['sk_municipality'])
    dim_fac['sk_municipality'] = dim_fac['sk_municipality'].astype(int)
    
    dim_fac = dim_fac.drop(columns=['municipality_name'])
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
                          dim_mun: pd.DataFrame, dim_reg: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building affiliates fact table...")
    
    time_map = dim_time.set_index(['year', 'month'])['sk_time'].to_dict()
    mun_map = dim_mun.set_index('code')['sk_municipality'].to_dict()
    reg_map = dim_reg.set_index('code')['sk_regime'].to_dict()
    
    fact = df_affiliates.copy()
    fact['sk_time'] = fact.apply(lambda r: time_map.get((r['year'], r['month'])), axis=1)
    fact['sk_municipality'] = fact['municipality_code'].map(mun_map)
    fact['sk_regime'] = fact['regime_id'].map(reg_map)
    
    fact = fact.dropna(subset=['sk_time', 'sk_municipality', 'sk_regime'])
    fact['sk_time'] = fact['sk_time'].astype(int)
    fact['sk_municipality'] = fact['sk_municipality'].astype(int)
    fact['sk_regime'] = fact['sk_regime'].astype(int)
    
    fact = fact[['sk_time', 'sk_municipality', 'sk_regime', 'num_persons']]
    fact['sk_affiliate'] = fact.index + 1
    
    logger.info(f"Affiliates fact records: {len(fact)}")
    return fact

def build_fact_facility_capacity(df_facilities: pd.DataFrame, dim_time: pd.DataFrame,
                                  dim_fac: pd.DataFrame, dim_ct: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building facility capacity fact table...")
    
    time_map = dim_time.set_index(['year', 'month'])['sk_time'].to_dict()
    
    df_fac_temp = df_facilities.copy()
    df_fac_temp['year'] = 2022
    df_fac_temp['month'] = 11
    
    fact = df_fac_temp[['provider_code', 'municipality', 'capacity_group', 'capacity_description',
                         'installed_capacity', 'year', 'month']].copy()
    
    fact['sk_time'] = fact.apply(lambda r: time_map.get((r['year'], r['month'])), axis=1)
    
    fac_key = dim_fac.set_index(['provider_code'])['sk_facility'].to_dict()
    fact['sk_facility'] = fact['provider_code'].map(fac_key)
    
    ct_key = dim_ct.set_index(['group', 'description'])['sk_capacity_type'].to_dict()
    fact['sk_capacity_type'] = fact.apply(
        lambda r: ct_key.get((r['capacity_group'], r['capacity_description'])), axis=1
    )
    
    fact = fact.dropna(subset=['sk_time', 'sk_facility', 'sk_capacity_type'])
    fact['sk_time'] = fact['sk_time'].astype(int)
    fact['sk_facility'] = fact['sk_facility'].astype(int)
    fact['sk_capacity_type'] = fact['sk_capacity_type'].astype(int)
    
    fact = fact[['sk_time', 'sk_facility', 'sk_capacity_type', 'installed_capacity']]
    fact['sk_capacity'] = fact.index + 1
    
    logger.info(f"Facility capacity fact records: {len(fact)}")
    return fact
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from .config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def load_dimension(conn, table_name: str, df: pd.DataFrame, pk_col: str):
    logger.info(f"Loading dimension {table_name}: {len(df)} records")
    
    cursor = conn.cursor()
    
    columns = [c for c in df.columns if c != pk_col]
    quoted = [f'"{c}"' for c in columns]
    values = df[columns].values.tolist()
    
    insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(quoted)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(cursor, insert_sql, values)
    conn.commit()
    
    logger.info(f"Dimension {table_name} loaded successfully")
    cursor.close()

def load_fact(conn, table_name: str, df: pd.DataFrame, pk_col: str):
    logger.info(f"Loading fact table {table_name}: {len(df)} records")
    
    cursor = conn.cursor()
    
    columns = [c for c in df.columns if c != pk_col]
    quoted = [f'"{c}"' for c in columns]
    values = df[columns].values.tolist()
    
    insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(quoted)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(cursor, insert_sql, values)
    conn.commit()
    
    logger.info(f"Fact table {table_name} loaded successfully")
    cursor.close()

def load_all(dimensions: dict, facts: dict):
    conn = get_connection()
    
    try:
        load_dimension(conn, 'dim_time', dimensions['time'], 'sk_time')
        load_dimension(conn, 'dim_department', dimensions['department'], 'sk_department')
        load_dimension(conn, 'dim_municipality', dimensions['municipality'], 'sk_municipality')
        load_dimension(conn, 'dim_regime', dimensions['regime'], 'sk_regime')
        load_dimension(conn, 'dim_geografia', dimensions['geografia'], 'sk_geografia')
        load_dimension(conn, 'dim_facility', dimensions['facility'], 'sk_facility')
        load_dimension(conn, 'dim_capacity_type', dimensions['capacity_type'], 'sk_capacity_type')
        
        load_fact(conn, 'fact_affiliates', facts['affiliates'], 'sk_affiliate')
        load_fact(conn, 'fact_facility_capacity', facts['capacity'], 'sk_capacity')
        
        logger.info("Load completed successfully")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during load: {e}")
        raise
    finally:
        conn.close()
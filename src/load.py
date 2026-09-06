import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from .config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def load_dimension(conn, table_name: str, df: pd.DataFrame, pk_col: str):
    logger.info(f"Cargando dimensión {table_name}: {len(df)} registros")
    
    cursor = conn.cursor()
    
    columns = [c for c in df.columns if c != pk_col]
    values = df[columns].values.tolist()
    
    insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(cursor, insert_sql, values)
    conn.commit()
    
    logger.info(f"Dimensión {table_name} cargada correctamente")
    cursor.close()

def load_fact(conn, table_name: str, df: pd.DataFrame, pk_col: str):
    logger.info(f"Cargando tabla de hechos {table_name}: {len(df)} registros")
    
    cursor = conn.cursor()
    
    columns = [c for c in df.columns if c != pk_col]
    values = df[columns].values.tolist()
    
    insert_sql = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(cursor, insert_sql, values)
    conn.commit()
    
    logger.info(f"Tabla de hechos {table_name} cargada correctamente")
    cursor.close()

def load_all(dimensions: dict, facts: dict):
    conn = get_connection()
    
    try:
        load_dimension(conn, 'dim_tiempo', dimensions['tiempo'], 'sk_tiempo')
        load_dimension(conn, 'dim_departamento', dimensions['departamento'], 'sk_departamento')
        load_dimension(conn, 'dim_municipio', dimensions['municipio'], 'sk_municipio')
        load_dimension(conn, 'dim_regimen', dimensions['regimen'], 'sk_regimen')
        load_dimension(conn, 'dim_ips', dimensions['ips'], 'sk_ips')
        load_dimension(conn, 'dim_tipo_capacidad', dimensions['tipo_capacidad'], 'sk_tipo_capacidad')
        
        load_fact(conn, 'fact_afiliados', facts['afiliados'], 'sk_afiliado')
        load_fact(conn, 'fact_capacidad_ips', facts['capacidad'], 'sk_capacidad')
        
        logger.info("Carga completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error durante la carga: {e}")
        raise
    finally:
        conn.close()
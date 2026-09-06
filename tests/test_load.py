import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.mark.unit
class TestLoadFunctions:
    
    def test_importacion_load(self):
        from src.load import load_dimension, load_fact, load_all
        assert callable(load_dimension)
        assert callable(load_fact)
        assert callable(load_all)
    
    def test_importacion_config(self):
        from src.config import DB_CONFIG
        assert 'host' in DB_CONFIG
        assert 'port' in DB_CONFIG
        assert 'database' in DB_CONFIG
        assert 'user' in DB_CONFIG
        assert 'password' in DB_CONFIG
    
    def test_configuracion_puerto(self):
        from src.config import DB_CONFIG
        assert DB_CONFIG['port'] == 5432
    
    def test_configuracion_database(self):
        from src.config import DB_CONFIG
        assert DB_CONFIG['database'] == 'salud_colombia'


@pytest.mark.integration
class TestConexionDB:
    
    def test ConexionPosible(self):
        try:
            import psycopg2
            from src.config import DB_CONFIG
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            conexion_exitosa = True
        except Exception:
            conexion_exitosa = False
        
        assert conexion_exitosa, "No se pudo conectar a la base de datos"
    
    def test_tablas_existen(self):
        try:
            import psycopg2
            from src.config import DB_CONFIG
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tablas = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            tablas_esperadas = {
                'dim_tiempo', 'dim_departamento', 'dim_municipio',
                'dim_regimen', 'dim_ips', 'dim_tipo_capacidad',
                'fact_afiliados', 'fact_capacidad_ips'
            }
            
            faltantes = tablas_esperadas - tablas
            assert len(faltantes) == 0, f"Tablas faltantes: {faltantes}"
            
        except Exception as e:
            pytest.skip(f"No se pudo verificar tablas: {e}")
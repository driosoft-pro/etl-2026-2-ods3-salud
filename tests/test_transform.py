import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extract import extract_all
from src.transform import (
    clean_afiliados, clean_ips,
    build_dim_tiempo, build_dim_departamento, build_dim_municipio,
    build_dim_regimen, build_dim_ips, build_dim_tipo_capacidad,
    build_fact_afiliados, build_fact_capacidad
)

@pytest.fixture(scope="module")
def raw_data():
    return extract_all()

@pytest.fixture(scope="module")
def df_afiliados_clean(raw_data):
    return clean_afiliados(raw_data['afiliados'])

@pytest.fixture(scope="module")
def df_ips_clean(raw_data):
    return clean_ips(raw_data['ips'])


@pytest.mark.unit
class TestCleanAfiliados:
    
    def test_limpia_num_personas(self, df_afiliados_clean):
        assert df_afiliados_clean['num_personas'].dtype in ['int64', 'int32'], \
            "num_personas debe ser entero"
        assert (df_afiliados_clean['num_personas'] >= 0).all(), \
            "num_personas no debe ser negativo"
    
    def test_convierte_anio(self, df_afiliados_clean):
        assert df_afiliados_clean['anio'].dtype in ['int64', 'int32'], \
            "anio debe ser entero"
    
    def test_convierte_mes(self, df_afiliados_clean):
        assert df_afiliados_clean['mes'].dtype in ['int64', 'int32'], \
            "mes debe ser entero"
    
    def test_elimina_ceros(self, df_afiliados_clean):
        assert (df_afiliados_clean['num_personas'] > 0).all(), \
            "No deben quedar registros con 0 afiliados"


@pytest.mark.unit
class TestCleanIPS:
    
    def test_limpia_capacidad(self, df_ips_clean):
        assert df_ips_clean['cantidad_capacidad'].dtype in ['int64', 'int32'], \
            "cantidad_capacidad debe ser entero"
    
    def test_elimina_nulos_criticos(self, df_ips_clean):
        assert df_ips_clean['cod_prestador'].notna().all(), \
            "cod_prestador no debe tener nulos"
        assert df_ips_clean['nombre_prestador'].notna().all(), \
            "nombre_prestador no debe tener nulos"


@pytest.mark.unit
class TestDimTiempo:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_afiliados_clean, df_ips_clean):
        self.dim = build_dim_tiempo(df_afiliados_clean, df_ips_clean)
    
    def test_es_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_tiene_sk(self):
        assert 'sk_tiempo' in self.dim.columns
    
    def test_sk_unico(self):
        assert self.dim['sk_tiempo'].is_unique
    
    def test_campos_completos(self):
        assert 'anio' in self.dim.columns
        assert 'mes' in self.dim.columns
        assert 'nombre_mes' in self.dim.columns
        assert 'trimestre' in self.dim.columns
        assert 'semestre' in self.dim.columns


@pytest.mark.unit
class TestDimDepartamento:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_afiliados_clean, df_ips_clean):
        self.dim = build_dim_departamento(df_afiliados_clean, df_ips_clean)
    
    def test_es_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_tiene_sk(self):
        assert 'sk_departamento' in self.dim.columns
    
    def test_sk_unico(self):
        assert self.dim['sk_departamento'].is_unique
    
    def test_tiene_codigo_nombre(self):
        assert 'codigo' in self.dim.columns
        assert 'nombre' in self.dim.columns


@pytest.mark.unit
class TestDimMunicipio:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_afiliados_clean, df_ips_clean):
        self.dim_dep = build_dim_departamento(df_afiliados_clean, df_ips_clean)
        self.dim = build_dim_municipio(df_afiliados_clean, df_ips_clean, self.dim_dep)
    
    def test_es_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_tiene_sk(self):
        assert 'sk_municipio' in self.dim.columns
    
    def test_tiene_fk_departamento(self):
        assert 'sk_departamento' in self.dim.columns
    
    def test_fk_valida(self):
        deptos_validos = set(self.dim_dep['sk_departamento'])
        fk_validas = self.dim['sk_departamento'].isin(deptos_validos)
        assert fk_validas.all(), "Hay foreign keys inválidas en sk_departamento"


@pytest.mark.unit
class TestDimRegimen:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_afiliados_clean):
        self.dim = build_dim_regimen(df_afiliados_clean)
    
    def test_es_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_tiene_sk(self):
        assert 'sk_regimen' in self.dim.columns
    
    def test_valores_validos(self):
        codigos = set(self.dim['codigo'])
        assert codigos <= {'S', 'E', 'C'}, f"Códigos inválidos: {codigos}"
    
    def test_descripciones(self):
        assert 'descripcion' in self.dim.columns
        assert (self.dim['descripcion'].notna()).all()


@pytest.mark.unit
class TestDimIPS:
    
    @pytest.fixture(autouse=True)
    def setup(self, raw_data):
        self.df_ips = clean_ips(raw_data['ips'])
        self.dim_dep = build_dim_departamento(
            clean_afiliados(raw_data['afiliados']), 
            self.df_ips
        )
        self.dim_mun = build_dim_municipio(
            clean_afiliados(raw_data['afiliados']),
            self.df_ips,
            self.dim_dep
        )
        self.dim = build_dim_ips(self.df_ips, self.dim_mun)
    
    def test_es_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_tiene_sk(self):
        assert 'sk_ips' in self.dim.columns
    
    def test_tiene_fk_municipio(self):
        assert 'sk_municipio' in self.dim.columns


@pytest.mark.unit
class TestFactAfiliados:
    
    @pytest.fixture(autouse=True)
    def setup(self, raw_data):
        self.df_af = clean_afiliados(raw_data['afiliados'])
        self.df_ips = clean_ips(raw_data['ips'])
        self.dim_tiempo = build_dim_tiempo(self.df_af, self.df_ips)
        self.dim_dep = build_dim_departamento(self.df_af, self.df_ips)
        self.dim_mun = build_dim_municipio(self.df_af, self.df_ips, self.dim_dep)
        self.dim_reg = build_dim_regimen(self.df_af)
        self.fact = build_fact_afiliados(self.df_af, self.dim_tiempo, self.dim_mun, self.dim_reg)
    
    def test_es_dataframe(self):
        assert isinstance(self.fact, pd.DataFrame)
    
    def test_tiene_medida(self):
        assert 'num_personas' in self.fact.columns
    
    def test_tiene_fks(self):
        assert 'sk_tiempo' in self.fact.columns
        assert 'sk_municipio' in self.fact.columns
        assert 'sk_regimen' in self.fact.columns
    
    def test_valores_positivos(self):
        assert (self.fact['num_personas'] > 0).all()
    
    def test_no_nulos(self):
        assert self.fact.notna().all().all()
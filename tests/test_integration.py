import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.mark.integration
class TestIntegracionCompleta:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from src.extract import extract_all
        from src.transform import (
            clean_afiliados, clean_ips,
            build_dim_tiempo, build_dim_departamento, build_dim_municipio,
            build_dim_regimen, build_dim_ips, build_dim_tipo_capacidad,
            build_fact_afiliados, build_fact_capacidad
        )
        
        self.raw = extract_all()
        self.df_af = clean_afiliados(self.raw['afiliados'])
        self.df_ips = clean_ips(self.raw['ips'])
        
        self.dim_tiempo = build_dim_tiempo(self.df_af, self.df_ips)
        self.dim_dep = build_dim_departamento(self.df_af, self.df_ips)
        self.dim_mun = build_dim_municipio(self.df_af, self.df_ips, self.dim_dep)
        self.dim_reg = build_dim_regimen(self.df_af)
        self.dim_ips = build_dim_ips(self.df_ips, self.dim_mun)
        self.dim_tc = build_dim_tipo_capacidad(self.df_ips)
        
        self.fact_af = build_fact_afiliados(self.df_af, self.dim_tiempo, self.dim_mun, self.dim_reg)
        self.fact_cap = build_fact_capacidad(self.df_ips, self.dim_tiempo, self.dim_ips, self.dim_tc)
    
    def test_todas_las_dimensiones(self):
        assert len(self.dim_tiempo) > 0
        assert len(self.dim_dep) > 0
        assert len(self.dim_mun) > 0
        assert len(self.dim_reg) > 0
        assert len(self.dim_ips) > 0
        assert len(self.dim_tc) > 0
    
    def test_todas_las_hechos(self):
        assert len(self.fact_af) > 0
        assert len(self.fact_cap) > 0
    
    def test_relaciones_consistentes(self):
        sk_tiempo_validos = set(self.dim_tiempo['sk_tiempo'])
        assert self.fact_af['sk_tiempo'].isin(sk_tiempo_validos).all()
        assert self.fact_cap['sk_tiempo'].isin(sk_tiempo_validos).all()
    
    def test_sin_duplicados_en_dimensiones(self):
        assert self.dim_tiempo['sk_tiempo'].is_unique
        assert self.dim_dep['sk_departamento'].is_unique
        assert self.dim_mun['sk_municipio'].is_unique
        assert self.dim_reg['sk_regimen'].is_unique
        assert self.dim_ips['sk_ips'].is_unique
        assert self.dim_tc['sk_tipo_capacidad'].is_unique
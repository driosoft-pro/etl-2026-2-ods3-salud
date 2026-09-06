import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.mark.integration
class TestFullIntegration:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        from src.extract import extract_all
        from src.transform import (
            clean_affiliates, clean_facilities,
            build_dim_time, build_dim_department, build_dim_municipality,
            build_dim_regime, build_dim_facility, build_dim_capacity_type,
            build_fact_affiliates, build_fact_facility_capacity
        )
        
        self.raw = extract_all()
        self.df_aff = clean_affiliates(self.raw['affiliates'])
        self.df_fac = clean_facilities(self.raw['facilities'])
        
        self.dim_time = build_dim_time(self.df_aff, self.df_fac)
        self.dim_dept = build_dim_department(self.df_aff, self.df_fac)
        self.dim_mun = build_dim_municipality(self.df_aff, self.df_fac, self.dim_dept)
        self.dim_reg = build_dim_regime(self.df_aff)
        self.dim_fac = build_dim_facility(self.df_fac, self.dim_mun)
        self.dim_ct = build_dim_capacity_type(self.df_fac)
        
        self.fact_aff = build_fact_affiliates(self.df_aff, self.dim_time, self.dim_mun, self.dim_reg)
        self.fact_cap = build_fact_facility_capacity(self.df_fac, self.dim_time, self.dim_fac, self.dim_ct)
    
    def test_all_dimensions(self):
        assert len(self.dim_time) > 0
        assert len(self.dim_dept) > 0
        assert len(self.dim_mun) > 0
        assert len(self.dim_reg) > 0
        assert len(self.dim_fac) > 0
        assert len(self.dim_ct) > 0
    
    def test_all_facts(self):
        assert len(self.fact_aff) > 0
        assert len(self.fact_cap) > 0
    
    def test_consistent_relationships(self):
        valid_sk_time = set(self.dim_time['sk_time'])
        assert self.fact_aff['sk_time'].isin(valid_sk_time).all()
        assert self.fact_cap['sk_time'].isin(valid_sk_time).all()
    
    def test_no_duplicates_in_dimensions(self):
        assert self.dim_time['sk_time'].is_unique
        assert self.dim_dept['sk_department'].is_unique
        assert self.dim_mun['sk_municipality'].is_unique
        assert self.dim_reg['sk_regime'].is_unique
        assert self.dim_fac['sk_facility'].is_unique
        assert self.dim_ct['sk_capacity_type'].is_unique
import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extract import extract_all
from src.transform import (
    clean_affiliates, clean_facilities,
    build_dim_time, build_dim_department, build_dim_municipality,
    build_dim_regime, build_dim_facility, build_dim_capacity_type,
    build_fact_affiliates, build_fact_facility_capacity
)

@pytest.fixture(scope="module")
def raw_data():
    return extract_all()

@pytest.fixture(scope="module")
def df_affiliates_clean(raw_data):
    return clean_affiliates(raw_data['affiliates'])

@pytest.fixture(scope="module")
def df_facilities_clean(raw_data):
    return clean_facilities(raw_data['facilities'])


@pytest.mark.unit
class TestCleanAffiliates:
    
    def test_cleans_num_persons(self, df_affiliates_clean):
        assert df_affiliates_clean['num_persons'].dtype in ['int64', 'int32'], \
            "num_persons must be integer"
        assert (df_affiliates_clean['num_persons'] >= 0).all(), \
            "num_persons must not be negative"
    
    def test_converts_year(self, df_affiliates_clean):
        assert df_affiliates_clean['year'].dtype in ['int64', 'int32'], \
            "year must be integer"
    
    def test_converts_month(self, df_affiliates_clean):
        assert df_affiliates_clean['month'].dtype in ['int64', 'int32'], \
            "month must be integer"
    
    def test_removes_zeros(self, df_affiliates_clean):
        assert (df_affiliates_clean['num_persons'] > 0).all(), \
            "No records with 0 affiliates should remain"


@pytest.mark.unit
class TestCleanFacilities:
    
    def test_cleans_capacity(self, df_facilities_clean):
        assert df_facilities_clean['installed_capacity'].dtype in ['int64', 'int32'], \
            "installed_capacity must be integer"
    
    def test_removes_critical_nulls(self, df_facilities_clean):
        assert df_facilities_clean['provider_code'].notna().all(), \
            "provider_code must not have nulls"
        assert df_facilities_clean['provider_name'].notna().all(), \
            "provider_name must not have nulls"


@pytest.mark.unit
class TestDimTime:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_affiliates_clean, df_facilities_clean):
        self.dim = build_dim_time(df_affiliates_clean, df_facilities_clean)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_time' in self.dim.columns
    
    def test_sk_unique(self):
        assert self.dim['sk_time'].is_unique
    
    def test_complete_fields(self):
        assert 'year' in self.dim.columns
        assert 'month' in self.dim.columns
        assert 'month_name' in self.dim.columns
        assert 'quarter' in self.dim.columns
        assert 'semester' in self.dim.columns


@pytest.mark.unit
class TestDimDepartment:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_affiliates_clean, df_facilities_clean):
        self.dim = build_dim_department(df_affiliates_clean, df_facilities_clean)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_department' in self.dim.columns
    
    def test_sk_unique(self):
        assert self.dim['sk_department'].is_unique
    
    def test_has_code_name(self):
        assert 'code' in self.dim.columns
        assert 'name' in self.dim.columns


@pytest.mark.unit
class TestDimMunicipality:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_affiliates_clean, df_facilities_clean):
        self.dim_dept = build_dim_department(df_affiliates_clean, df_facilities_clean)
        self.dim = build_dim_municipality(df_affiliates_clean, df_facilities_clean, self.dim_dept)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_municipality' in self.dim.columns
    
    def test_has_fk_department(self):
        assert 'sk_department' in self.dim.columns
    
    def test_valid_fk(self):
        valid_depts = set(self.dim_dept['sk_department'])
        valid_fk = self.dim['sk_department'].isin(valid_depts)
        assert valid_fk.all(), "There are invalid foreign keys in sk_department"


@pytest.mark.unit
class TestDimRegime:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_affiliates_clean):
        self.dim = build_dim_regime(df_affiliates_clean)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_regime' in self.dim.columns
    
    def test_valid_values(self):
        codes = set(self.dim['code'])
        assert codes <= {'S', 'E', 'C'}, f"Invalid codes: {codes}"
    
    def test_descriptions(self):
        assert 'description' in self.dim.columns
        assert (self.dim['description'].notna()).all()


@pytest.mark.unit
class TestDimFacility:
    
    @pytest.fixture(autouse=True)
    def setup(self, raw_data):
        self.df_fac = clean_facilities(raw_data['facilities'])
        self.dim_dept = build_dim_department(
            clean_affiliates(raw_data['affiliates']), 
            self.df_fac
        )
        self.dim_mun = build_dim_municipality(
            clean_affiliates(raw_data['affiliates']),
            self.df_fac,
            self.dim_dept
        )
        self.dim = build_dim_facility(self.df_fac, self.dim_mun)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_facility' in self.dim.columns
    
    def test_has_fk_municipality(self):
        assert 'sk_municipality' in self.dim.columns


@pytest.mark.unit
class TestFactAffiliates:
    
    @pytest.fixture(autouse=True)
    def setup(self, raw_data):
        self.df_aff = clean_affiliates(raw_data['affiliates'])
        self.df_fac = clean_facilities(raw_data['facilities'])
        self.dim_time = build_dim_time(self.df_aff, self.df_fac)
        self.dim_dept = build_dim_department(self.df_aff, self.df_fac)
        self.dim_mun = build_dim_municipality(self.df_aff, self.df_fac, self.dim_dept)
        self.dim_reg = build_dim_regime(self.df_aff)
        self.fact = build_fact_affiliates(self.df_aff, self.dim_time, self.dim_mun, self.dim_reg)
    
    def test_is_dataframe(self):
        assert isinstance(self.fact, pd.DataFrame)
    
    def test_has_measure(self):
        assert 'num_persons' in self.fact.columns
    
    def test_has_fks(self):
        assert 'sk_time' in self.fact.columns
        assert 'sk_municipality' in self.fact.columns
        assert 'sk_regime' in self.fact.columns
    
    def test_positive_values(self):
        assert (self.fact['num_persons'] > 0).all()
    
    def test_no_nulls(self):
        assert self.fact.notna().all().all()
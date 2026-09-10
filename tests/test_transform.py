import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extract import extract_all
from src.transform import (
    clean_affiliates, clean_facilities,
    build_dim_time, build_dim_geografia, build_dim_department, build_dim_municipality,
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
    
    def test_has_periodo_codigo(self):
        assert 'periodo_codigo' in self.dim.columns
        assert self.dim['periodo_codigo'].notna().all()
    
    def test_periodo_codigo_format(self):
        sample = self.dim['periodo_codigo'].iloc[0]
        assert '-' in sample and 'Q' in sample, \
            f"periodo_codigo format should be YYYY-QN, got: {sample}"


@pytest.mark.unit
class TestDimGeografia:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_affiliates_clean, df_facilities_clean):
        self.dim = build_dim_geografia(df_affiliates_clean, df_facilities_clean)
    
    def test_is_dataframe(self):
        assert isinstance(self.dim, pd.DataFrame)
    
    def test_has_sk(self):
        assert 'sk_geografia' in self.dim.columns
    
    def test_sk_unique(self):
        assert self.dim['sk_geografia'].is_unique
    
    def test_has_required_columns(self):
        for col in ['codigo_dane_municipio', 'municipio', 'codigo_dane_depto',
                     'departamento', 'region']:
            assert col in self.dim.columns, f"Missing column: {col}"
    
    def test_region_values(self):
        valid_regions = {'Amazonia', 'Orinoquia', 'Andina', 'Pacifico',
                         'Caribe', 'Insular', 'Sin Region'}
        actual = set(self.dim['region'].unique())
        assert actual <= valid_regions, f"Unexpected regions: {actual - valid_regions}"
    
    def test_no_null_departments(self):
        assert self.dim['departamento'].notna().all()


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
        self.dim_geo = build_dim_geografia(self.df_aff, self.df_fac)
        self.dim_reg = build_dim_regime(self.df_aff)
        self.fact = build_fact_affiliates(self.df_aff, self.dim_time, self.dim_geo, self.dim_reg)
    
    def test_is_dataframe(self):
        assert isinstance(self.fact, pd.DataFrame)
    
    def test_has_measure(self):
        assert 'numero_afiliados' in self.fact.columns
    
    def test_has_fks(self):
        assert 'sk_time' in self.fact.columns
        assert 'sk_geografia' in self.fact.columns
        assert 'sk_regime' in self.fact.columns
    
    def test_positive_values(self):
        assert (self.fact['numero_afiliados'] > 0).all()
    
    def test_no_nulls(self):
        assert self.fact.notna().all().all()
    
    def test_quarterly_granularity(self):
        assert len(self.fact) > 0
        merged = self.fact.merge(self.dim_time[['sk_time', 'year', 'quarter']], on='sk_time')
        grouped = merged.groupby(['sk_geografia', 'sk_regime', 'year', 'quarter']).size()
        assert (grouped == 1).all(), "Each combination of geo/regime/year/quarter should have exactly one row"


@pytest.mark.unit
class TestValidate:
    
    def test_import(self):
        from src.validate import (
            validate_foreign_keys, validate_measures,
            validate_no_duplicates, validate_raw_affiliates,
            validate_sum_consistency, run_all_validations
        )
    
    def test_validate_measures_clean(self):
        from src.validate import validate_measures
        df = pd.DataFrame({'numero_afiliados': [100, 200, 300]})
        errors = validate_measures(df, ['numero_afiliados'])
        assert len(errors) == 0
    
    def test_validate_measures_negative(self):
        from src.validate import validate_measures
        df = pd.DataFrame({'numero_afiliados': [100, -5, 300]})
        errors = validate_measures(df, ['numero_afiliados'])
        assert len(errors) > 0
    
    def test_validate_no_duplicates_clean(self):
        from src.validate import validate_no_duplicates
        df = pd.DataFrame({'sk_time': [1, 2], 'sk_geografia': [1, 2], 'sk_regime': [1, 1]})
        errors = validate_no_duplicates(df, ['sk_time', 'sk_geografia', 'sk_regime'])
        assert len(errors) == 0
    
    def test_validate_no_duplicates_with_dupes(self):
        from src.validate import validate_no_duplicates
        df = pd.DataFrame({'sk_time': [1, 1], 'sk_geografia': [1, 1], 'sk_regime': [1, 1]})
        errors = validate_no_duplicates(df, ['sk_time', 'sk_geografia', 'sk_regime'])
        assert len(errors) > 0

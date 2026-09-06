import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extract import extract_afiliados, extract_ips, extract_all

@pytest.mark.unit
class TestExtractAfiliados:
    
    def test_extrae_dataframe(self):
        df = extract_afiliados()
        assert isinstance(df, pd.DataFrame), "Debe retornar un DataFrame"
    
    def test_no_vacio(self):
        df = extract_afiliados()
        assert len(df) > 0, "El DataFrame no debe estar vacío"
    
    def test_columnas_renombradas(self):
        df = extract_afiliados()
        columnas_esperadas = ['cod_depto', 'departamento', 'cod_municipio', 
                              'municipio', 'id_regimen', 'anio', 'mes', 'num_personas']
        assert list(df.columns) == columnas_esperadas, \
            f"Columnas incorrectas: {list(df.columns)}"
    
    def test_tipos_string(self):
        df = extract_afiliados()
        for col in df.columns:
            assert df[col].dtype == 'object', f"Columna {col} debe ser string"


@pytest.mark.unit
class TestExtractIPS:
    
    def test_extrae_dataframe(self):
        df = extract_ips()
        assert isinstance(df, pd.DataFrame), "Debe retornar un DataFrame"
    
    def test_no_vacio(self):
        df = extract_ips()
        assert len(df) > 0, "El DataFrame no debe estar vacío"
    
    def test_columnas_renombradas(self):
        df = extract_ips()
        assert 'cod_prestador' in df.columns, "Falta columna cod_prestador"
        assert 'nombre_prestador' in df.columns, "Falta columna nombre_prestador"
        assert 'grupo_capacidad' in df.columns, "Falta columna grupo_capacidad"


@pytest.mark.unit
class TestExtractAll:
    
    def test_retorna_diccionario(self):
        result = extract_all()
        assert isinstance(result, dict), "Debe retornar un diccionario"
    
    def test_contiene_claves(self):
        result = extract_all()
        assert 'afiliados' in result, "Falta clave 'afiliados'"
        assert 'ips' in result, "Falta clave 'ips'"
    
    def test_valores_son_dataframes(self):
        result = extract_all()
        assert isinstance(result['afiliados'], pd.DataFrame)
        assert isinstance(result['ips'], pd.DataFrame)
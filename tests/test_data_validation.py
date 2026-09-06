import pytest
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

AFILIADOS_FILE = 'Número_de_afiliados_por_departamento,_municipio_y_régimen_20260906.csv'
IPS_FILE = 'Relación_de_IPS_públicas_y_privadas_según_el_nivel_de_atención_y_capacidad_instalada_20260906.csv'

@pytest.mark.data
class TestDataRawAfiliados:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_afiliados_raw):
        self.df = df_afiliados_raw
    
    def test_archivo_existe(self):
        path = os.path.join(DATA_DIR, AFILIADOS_FILE)
        assert os.path.exists(path), f"Archivo no encontrado: {AFILIADOS_FILE}"
    
    def test_archivo_no_vacio(self):
        assert len(self.df) > 0, "El dataset de afiliados está vacío"
    
    def test_columnas_esperadas(self):
        columnas_esperadas = ['CodDepto', 'Departamento', 'CodMunicipio', 
                              'Municipio', 'IDRegimen', 'Año', 'Mes', 'NumPersonas']
        columnas_actuales = list(self.df.columns)
        assert columnas_esperadas == columnas_actuales, \
            f"Columnas esperadas: {columnas_esperadas}\nColumnas actuales: {columnas_actuales}"
    
    def test_no_completamente_vacio(self):
        for col in self.df.columns:
            assert not self.df[col].isna().all(), f"Columna '{col}' está completamente vacía"
    
    def test_registros_minimos(self):
        assert len(self.df) >= 100, \
            f"Se esperan al menos 100 registros, se encontraron {len(self.df)}"
    
    def test Departamento_no_nulos(self):
        nulos = self.df['Departamento'].isna().sum()
        assert nulos == 0, f"Hay {nulos} valores nulos en Departamento"
    
    def test_municipio_no_nulos(self):
        nulos = self.df['Municipio'].isna().sum()
        assert nulos == 0, f"Hay {nulos} valores nulos en Municipio"
    
    def test_regimen_valido(self):
        regimes = self.df['IDRegimen'].dropna().unique()
        regimes_validos = {'S', 'E', 'C'}
        regimes_invalidos = set(regimes) - regimes_validos
        assert len(regimes_invalidos) == 0, \
            f"Régimenes inválidos encontrados: {regimes_invalidos}"
    
    def test_anio_formato(self):
        anios = self.df['Año'].dropna().unique()
        for anio in anios:
            assert anio.isdigit(), f"Año con formato inválido: {anio}"
            assert 2000 <= int(anio) <= 2030, f"Año fuera de rango: {anio}"
    
    def test_mes_rango(self):
        meses = self.df['Mes'].dropna().unique()
        for mes in meses:
            assert mes.isdigit(), f"Mes con formato inválido: {mes}"
            assert 1 <= int(mes) <= 12, f"Mes fuera de rango: {mes}"


@pytest.mark.data
class TestDataRawIPS:
    
    @pytest.fixture(autouse=True)
    def setup(self, df_ips_raw):
        self.df = df_ips_raw
    
    def test_archivo_existe(self):
        path = os.path.join(DATA_DIR, IPS_FILE)
        assert os.path.exists(path), f"Archivo no encontrado: {IPS_FILE}"
    
    def test_archivo_no_vacio(self):
        assert len(self.df) > 0, "El dataset de IPS está vacío"
    
    def test_columnas_esperadas(self):
        columnas_esperadas = ['Departamento', 'Municipio', 'Código prestador', 
                              'Nombre prestador', 'nit IPS ', 'num digito_verificion',
                              'naturaleza', 'num nivel atencion', 'Código sede',
                              'Número sede', 'nom sede IPS', 'Gerente', 'Dirección',
                              'Email', 'Teléfono', 'nom grupo capacidad ',
                              'nom descripcion capacidad ', 'num cantidad capacidad instalada',
                              'Fecha Corte', 'Fuente']
        columnas_actuales = list(self.df.columns)
        assert columnas_esperadas == columnas_actuales, \
            f"Columnas esperadas: {columnas_esperadas}\nColumnas actuales: {columnas_actuales}"
    
    def test_registros_minimos(self):
        assert len(self.df) >= 1000, \
            f"Se esperan al menos 1000 registros, se encontraron {len(self.df)}"
    
    def test_naturaleza_valida(self):
        naturalezas = self.df['naturaleza'].dropna().unique()
        naturalezas_validas = {'Pública', 'Privada'}
        for nat in naturalezas:
            assert nat in naturalezas_validas, f"Naturaleza inválida: {nat}"
    
    def test_nivel_atencion_rango(self):
        niveles = self.df['num nivel atencion'].dropna().unique()
        for nivel in niveles:
            if nivel.isdigit():
                assert 1 <= int(nivel) <= 5, f"Nivel de atención fuera de rango: {nivel}"
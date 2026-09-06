import pytest
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')

AFILIADOS_FILE = 'Número_de_afiliados_por_departamento,_municipio_y_régimen_20260906.csv'
IPS_FILE = 'Relación_de_IPS_públicas_y_privadas_según_el_nivel_de_atención_y_capacidad_instalada_20260906.csv'

@pytest.fixture(scope="session")
def df_afiliados_raw():
    path = os.path.join(DATA_DIR, AFILIADOS_FILE)
    return pd.read_csv(path, dtype=str)

@pytest.fixture(scope="session")
def df_ips_raw():
    path = os.path.join(DATA_DIR, IPS_FILE)
    return pd.read_csv(path, dtype=str)
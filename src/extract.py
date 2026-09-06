import pandas as pd
from .config import DATA_DIR, DATASETS
import logging

logger = logging.getLogger(__name__)

def extract_afiliados() -> pd.DataFrame:
    path = f"{DATA_DIR}/{DATASETS['afiliados']}"
    logger.info(f"Extrayendo afiliados desde: {path}")
    df = pd.read_csv(path, dtype=str)
    df.columns = ['cod_depto', 'departamento', 'cod_municipio', 'municipio',
                   'id_regimen', 'anio', 'mes', 'num_personas']
    logger.info(f"Registros extraídos: {len(df)}")
    return df

def extract_ips() -> pd.DataFrame:
    path = f"{DATA_DIR}/{DATASETS['ips']}"
    logger.info(f"Extrayendo IPS desde: {path}")
    df = pd.read_csv(path, dtype=str)
    df.columns = ['departamento', 'municipio', 'cod_prestador', 'nombre_prestador',
                   'nit', 'digito_verificacion', 'naturaleza', 'nivel_atencion',
                   'cod_sede', 'num_sede', 'nom_sede', 'gerente', 'direccion',
                   'email', 'telefono', 'grupo_capacidad', 'desc_capacidad',
                   'cantidad_capacidad', 'fecha_corte', 'fuente']
    logger.info(f"Registros extraídos: {len(df)}")
    return df

def extract_all() -> dict:
    return {
        'afiliados': extract_afiliados(),
        'ips': extract_ips()
    }
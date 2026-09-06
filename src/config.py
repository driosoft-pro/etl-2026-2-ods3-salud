import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'salud_colombia'),
    'user': os.getenv('DB_USER', 'etl_user'),
    'password': os.getenv('DB_PASSWORD', 'etl_password_2026')
}

DATA_DIR = '/app/data/raw'

DATASETS = {
    'afiliados': 'Número_de_afiliados_por_departamento,_municipio_y_régimen_20260906.csv',
    'ips': 'Relación_de_IPS_públicas_y_privadas_según_el_nivel_de_atención_y_capacidad_instalada_20260906.csv'
}

MESES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}
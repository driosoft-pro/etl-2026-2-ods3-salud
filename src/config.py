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
    'affiliates': 'affiliates_by_department_municipality_regime_20260906.csv',
    'facilities': 'healthcare_facilities_by_level_capacity_20260906.csv'
}

MONTHS = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
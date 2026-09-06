import logging
import sys
from .extract import extract_all
from .transform import (
    clean_affiliates, clean_facilities,
    build_dim_time, build_dim_department, build_dim_municipality,
    build_dim_regime, build_dim_facility, build_dim_capacity_type,
    build_fact_affiliates, build_fact_facility_capacity
)
from .load import load_all

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/etl.log')
    ]
)
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("=" * 60)
    logger.info("ETL PROCESS STARTED - HEALTH COLOMBIA")
    logger.info("=" * 60)
    
    try:
        logger.info("PHASE 1: EXTRACTION")
        raw_data = extract_all()
        
        logger.info("PHASE 2: TRANSFORMATION")
        df_affiliates = clean_affiliates(raw_data['affiliates'])
        df_facilities = clean_facilities(raw_data['facilities'])
        
        logger.info("Building dimensions...")
        dim_time = build_dim_time(df_affiliates, df_facilities)
        dim_department = build_dim_department(df_affiliates, df_facilities)
        dim_municipality = build_dim_municipality(df_affiliates, df_facilities, dim_department)
        dim_regime = build_dim_regime(df_affiliates)
        dim_facility = build_dim_facility(df_facilities, dim_municipality)
        dim_capacity_type = build_dim_capacity_type(df_facilities)
        
        logger.info("Building fact tables...")
        fact_affiliates = build_fact_affiliates(df_affiliates, dim_time, dim_municipality, dim_regime)
        fact_capacity = build_fact_facility_capacity(df_facilities, dim_time, dim_facility, dim_capacity_type)
        
        dimensions = {
            'time': dim_time,
            'department': dim_department,
            'municipality': dim_municipality,
            'regime': dim_regime,
            'facility': dim_facility,
            'capacity_type': dim_capacity_type
        }
        
        facts = {
            'affiliates': fact_affiliates,
            'capacity': fact_capacity
        }
        
        logger.info("PHASE 3: LOADING")
        load_all(dimensions, facts)
        
        logger.info("=" * 60)
        logger.info("ETL PROCESS COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        
        print("\n LOAD SUMMARY:")
        print(f"   dim_time:          {len(dim_time)} records")
        print(f"   dim_department:    {len(dim_department)} records")
        print(f"   dim_municipality:  {len(dim_municipality)} records")
        print(f"   dim_regime:        {len(dim_regime)} records")
        print(f"   dim_facility:      {len(dim_facility)} records")
        print(f"   dim_capacity_type: {len(dim_capacity_type)} records")
        print(f"   fact_affiliates:   {len(fact_affiliates)} records")
        print(f"   fact_capacity:     {len(fact_capacity)} records")
        
    except Exception as e:
        logger.error(f"ETL process error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_etl()
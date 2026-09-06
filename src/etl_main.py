import logging
import sys
from .extract import extract_all
from .transform import (
    clean_afiliados, clean_ips,
    build_dim_tiempo, build_dim_departamento, build_dim_municipio,
    build_dim_regimen, build_dim_ips, build_dim_tipo_capacidad,
    build_fact_afiliados, build_fact_capacidad
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
    logger.info("INICIO DEL PROCESO ETL - SALUD COLOMBIA")
    logger.info("=" * 60)
    
    try:
        logger.info("FASE 1: EXTRACCIÓN")
        raw_data = extract_all()
        
        logger.info("FASE 2: TRANSFORMACIÓN")
        df_afiliados = clean_afiliados(raw_data['afiliados'])
        df_ips = clean_ips(raw_data['ips'])
        
        logger.info("Construyendo dimensiones...")
        dim_tiempo = build_dim_tiempo(df_afiliados, df_ips)
        dim_departamento = build_dim_departamento(df_afiliados, df_ips)
        dim_municipio = build_dim_municipio(df_afiliados, df_ips, dim_departamento)
        dim_regimen = build_dim_regimen(df_afiliados)
        dim_ips = build_dim_ips(df_ips, dim_municipio)
        dim_tipo_capacidad = build_dim_tipo_capacidad(df_ips)
        
        logger.info("Construyendo tablas de hechos...")
        fact_afiliados = build_fact_afiliados(df_afiliados, dim_tiempo, dim_municipio, dim_regimen)
        fact_capacidad = build_fact_capacidad(df_ips, dim_tiempo, dim_ips, dim_tipo_capacidad)
        
        dimensions = {
            'tiempo': dim_tiempo,
            'departamento': dim_departamento,
            'municipio': dim_municipio,
            'regimen': dim_regimen,
            'ips': dim_ips,
            'tipo_capacidad': dim_tipo_capacidad
        }
        
        facts = {
            'afiliados': fact_afiliados,
            'capacidad': fact_capacidad
        }
        
        logger.info("FASE 3: CARGA")
        load_all(dimensions, facts)
        
        logger.info("=" * 60)
        logger.info("PROCESO ETL COMPLETADO EXITOSAMENTE")
        logger.info("=" * 60)
        
        print("\n RESUMEN DE CARGA:")
        print(f"   dim_tiempo:          {len(dim_tiempo)} registros")
        print(f"   dim_departamento:    {len(dim_departamento)} registros")
        print(f"   dim_municipio:       {len(dim_municipio)} registros")
        print(f"   dim_regimen:         {len(dim_regimen)} registros")
        print(f"   dim_ips:             {len(dim_ips)} registros")
        print(f"   dim_tipo_capacidad:  {len(dim_tipo_capacidad)} registros")
        print(f"   fact_afiliados:      {len(fact_afiliados)} registros")
        print(f"   fact_capacidad_ips:  {len(fact_capacidad)} registros")
        
    except Exception as e:
        logger.error(f"Error en el proceso ETL: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_etl()
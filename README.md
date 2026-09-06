# Análisis de Salud en Colombia - Warehouse Dimensional

Proyecto ETL para el análisis de afiliados al sistema de salud y capacidad de IPS en Colombia. Utiliza Docker y PostgreSQL como data warehouse dimensional.

## Integrantes del Equipo

| Nombre | GitHub |
|--------|--------|
| Deyton Riascos Ortiz | [@deyton-riascos](https://github.com/deyton-riascos) |
| Samuel Izquierdo Bonilla | [@samuel-izquierdo](https://github.com/samuel-izquierdo) |
| Daniel David Garcia Restrepo | [@daniel-garcia](https://github.com/daniel-garcia) |
| Mauricio Taborda Gongora | [@mauricio-taborda](https://github.com/mauricio-taborda) |

## Estructura del Proyecto

```
├── data/
│   └── raw/                                    # Datos originales de SISPRO
│       ├── Número_de_afiliados_por_departamento,_municipio_y_régimen_20260906.csv
│       └── Relación_de_IPS_públicas_y_privadas_según_el_nivel_de_atención_y_capacidad_instalada_20260906.csv
├── docs/
│   └── ETL_2026-2_Project_FirstDelivery.pdf
├── sql/
│   └── init.sql                                # Esquema dimensional
├── src/
│   ├── __init__.py
│   ├── config.py                               # Configuración del proyecto
│   ├── extract.py                              # Fase de extracción
│   ├── transform.py                            # Fase de transformación
│   ├── load.py                                 # Fase de carga
│   └── etl_main.py                             # Orquestador principal
├── notebooks/                                  # Jupyter notebooks
├── logs/                                       # Logs del proceso ETL
├── docker-compose.yml                          # Infraestructura Docker
├── Dockerfile                                  # Imagen del proceso ETL
├── requirements.txt                            # Dependencias Python
├── .gitignore
└── README.md
```

## Esquema Dimensional

### Modelo Star

**Tablas de Hechos:**
- `fact_afiliados`: Número de personas afiliadas por municipio, régimen y tiempo
- `fact_capacidad_ips`: Capacidad instalada por IPS y tipo de capacidad

**Dimensiones:**
- `dim_tiempo`: Año, mes, trimestre, semestre
- `dim_departamento`: Código y nombre del departamento
- `dim_municipio`: Código, nombre y departamento
- `dim_regimen`: Código y descripción del régimen (Subsidado, Especial, Contributivo)
- `dim_ips`: Datos de las Instituciones Prestadoras de Servicios
- `dim_tipo_capacidad`: Grupo y descripción de capacidad (CAMAS, CAMILLAS, etc.)

## Infraestructura Docker

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| PostgreSQL | 5432 | Data Warehouse |
| pgAdmin | 5050 | Interfaz web para BD |
| ETL | - | Proceso de transformación |

## Instalación y Ejecución

### Requisitos Previos
- Docker y Docker Compose instalados
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/username/salud-colombia-etl.git
cd salud-colombia-etl

# 2. Levantar la infraestructura
docker-compose up -d

# 3. Verificar que PostgreSQL esté listo
docker logs warehouse_salud

# 4. Ejecutar el proceso ETL
docker-compose run --rm etl

# 5. Acceder a pgAdmin
# Abrir http://localhost:5050
# Email: admin@salud.com
# Password: admin123
```

### Conexión en pgAdmin

1. Registrar nuevo servidor en pgAdmin
2. Host: `postgres`
3. Port: `5432`
4. Database: `salud_colombia`
5. Username: `etl_user`
6. Password: `etl_password_2026`

## Consultas de Ejemplo

```sql
-- Total de afiliados por departamento
SELECT d.nombre, SUM(f.num_personas) as total_afiliados
FROM fact_afiliados f
JOIN dim_municipio m ON f.sk_municipio = m.sk_municipio
JOIN dim_departamento d ON m.sk_departamento = d.sk_departamento
GROUP BY d.nombre
ORDER BY total_afiliados DESC;

-- IPS por tipo de naturaleza
SELECT i.naturaleza, COUNT(*) as total_ips
FROM dim_ips i
GROUP BY i.naturaleza;

-- Capacidad instalada por tipo
SELECT tc.descripcion, SUM(c.cantidad_capacidad) as total_capacidad
FROM fact_capacidad_ips c
JOIN dim_tipo_capacidad tc ON c.sk_tipo_capacidad = tc.sk_tipo_capacidad
GROUP BY tc.descripcion
ORDER BY total_capacidad DESC;
```

## Datos Fuente

- **Afiliados**: SISPRO - Número de afiliados por departamento, municipio y régimen
- **IPS**: REPS - Relación de IPS públicas y privadas según nivel de atención y capacidad instalada

## Licencia

Proyecto académico - Universidad EAFIT
Curso: ETL y Análisis de Datos - 2026-2
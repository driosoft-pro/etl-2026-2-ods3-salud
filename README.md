# Health Analytics Colombia - Dimensional Data Warehouse

ETL project for analyzing healthcare system affiliates and facility capacity in Colombia. Uses Docker and PostgreSQL as a dimensional data warehouse.

## Problem Statement and SDG Alignment

### SDG: Goal 3 — Good Health and Well-being

**Target 3.8:** Achieve universal health coverage, including financial risk protection, access to quality essential health-care services, and access to safe, effective, quality, and affordable essential medicines and vaccines for all.

### Colombian Problem

Structural gap in healthcare coverage and formal enrollment between peripheral regions (Amazonia, Orinoquia, Pacific Coast) and central regions of Colombia, evidenced by the high dependence on the subsidized regime versus the contributory regime.

This project addresses this problem by building a dimensional data warehouse that enables analytical queries to:
- Identify territories with low contributory enrollment for formalization planning
- Track temporal evolution of subsidized regime growth by department
- Compare regime proportions across geographic subregions to map socioeconomic vulnerability
- Detect net drops in contributory affiliation at the departmental level
- Classify municipalities by total coverage quartiles to identify territorial lag

---

## Analytical Requirements Matrix

| ID | Requirement | Description | Priority |
|----|-------------|-------------|----------|
| **R1** | Lowest contributory volume | Identify the 10 municipalities with the lowest volume of contributory regime affiliates in the last reported year to prioritize labor formalization plans | High |
| **R2** | Subsidized growth evolution | Analyze the temporal evolution (year/quarter) of the growth rate of subsidized regime affiliates by department | High |
| **R3** | Regime proportion by subregion | Compare the proportion of subsidized vs. contributory regime by geographic subregion to map socioeconomic vulnerability | High |
| **R4** | Contributory drops | Determine the quarters with the largest net drops in contributory affiliation at the departmental level | High |
| **R5** | Coverage quartiles | Classify municipalities into quartiles based on their total affiliation coverage to detect territorial access lag | High |

---

## Team Members

- **Deyton Riascos Ortiz** — [GitHub](https://github.com/driosoft-pro)
- **Samuel Izquierdo Bonilla** — [GitHub](https://github.com/ZantaCruz)
- **Daniel David Garcia Restrepo** — [GitHub](https://github.com/danielrestrepo13)
- **Mauricio Taborda Gongora** — [GitHub](https://github.com/Taborda004)

## Project Structure

```
├── data/
│   ├── raw/                                    # Original data from SISPRO
│   │   ├── affiliates_by_department_municipality_regime_20260906.csv
│   │   └── healthcare_facilities_by_level_capacity_20260906.csv
│   └── processed/                              # Clean data (generated)
├── docs/
│   └── ETL_2026-2_Project_FirstDelivery.pdf
├── sql/
│   └── init.sql                                # Dimensional schema
├── src/
│   ├── __init__.py
│   ├── config.py                               # Project configuration
│   ├── extract.py                              # Extraction phase
│   ├── transform.py                            # Transformation phase
│   ├── load.py                                 # Load phase
│   └── etl_main.py                             # Main orchestrator
├── tests/
│   ├── __init__.py
│   ├── conftest.py                             # Pytest configuration
│   ├── test_data_raw.py                        # Raw data fixtures
│   ├── test_data_validation.py                 # Raw data validation
│   ├── test_extract.py                         # Extraction tests
│   ├── test_transform.py                       # Transformation tests
│   ├── test_load.py                            # Load tests
│   ├── test_integration.py                     # Integration tests
│   ├── run_tests.py                            # Test runner script
│   └── requirements-tests.txt                  # Test dependencies
├── notebooks/
│   └── 01_data_validation_cleanup.ipynb        # Validation and cleanup
├── logs/                                       # ETL process logs
├── docker-compose.yml                          # Docker infrastructure
├── Dockerfile                                  # ETL process image
├── requirements.txt                            # Python dependencies
├── run_tests.sh                                # Quick test runner
├── .env                                        # Environment variables (not in Git)
├── .env.example                                # Variables template
├── .gitignore
└── README.md
```

## Dimensional Schema

### Fact Table Granularity

> **A row in the affiliates fact table represents the total accumulated affiliates for a specific health regime, in a given municipality, during a specific quarter and year.**

This quarterly granularity enables temporal analysis of enrollment trends (R2, R4) while maintaining the geographic and regime breakdowns needed for territorial comparisons (R1, R3, R5).

### Star Model

``` mermaid
erDiagram
    dim_tiempo ||--o{ fact_afiliados : registra
    dim_regimen ||--o{ fact_afiliados : clasifica
    dim_geografia ||--o{ fact_afiliados : localiza
    dim_geografia ||--o{ dim_municipio : contiene
    dim_ips ||--o{ fact_capacidad : atiende
    dim_tipo_capacidad ||--o{ fact_capacidad : clasifica

    fact_afiliados {
        int id_hecho PK
        int sk_geografia FK
        int sk_tiempo FK
        int sk_regimen FK
        int numero_afiliados
    }

    fact_capacidad {
        int id_capacidad PK
        int sk_tiempo FK
        int sk_ips FK
        int sk_tipo_capacidad FK
        int capacidad_instalada
    }

    dim_tiempo {
        int sk_tiempo PK
        int anio
        int trimestre
        string periodo_codigo
    }

    dim_geografia {
        int sk_geografia PK
        string codigo_dane_municipio
        string municipio
        string codigo_dane_depto
        string departamento
        string region
    }

    dim_municipio {
        int sk_municipio PK
        int sk_geografia FK
        string codigo_dane
        string nombre
    }

    dim_regimen {
        int sk_regimen PK
        string codigo_regimen
        string nombre_regimen
    }

    dim_ips {
        int sk_ips PK
        string codigo_habilitacion
        string nombre_ips
        string naturaleza
        int nivel_atencion
        int sk_municipio FK
    }

    dim_tipo_capacidad {
        int sk_tipo_capacidad PK
        string grupo
        string descripcion
    }
```

**Fact Tables:**
- `fact_afiliates`: Accumulated affiliates per regime, municipality, and quarter/year
- `fact_facility_capacity`: Installed capacity per facility, capacity type, and time

**Dimensions:**
- `dim_tiempo` (Time): Year, quarter, period code (e.g. 2024-Q1)
- `dim_geografia` (Geography): Municipality code/name, department code/name, geographic region (Amazonia, Orinoquia, Pacific, Andina, Caribe, Insular)
- `dim_municipio` (Municipality): Detailed municipality linked to geography
- `dim_regimen` (Regime): Code and description (Contributivo, Subsidiado, Excepción/Especial)
- `dim_ips` (Healthcare Facility): Provider data linked to municipality
- `dim_tipo_capacidad` (Capacity Type): Group and description (CAMAS, SALAS, etc.)

## Docker Infrastructure

| Service | Port | Description | URL |
|---------|------|-------------|-----|
| PostgreSQL | 5432 | Data Warehouse | localhost:5432 |
| pgAdmin | 5050 | Database web interface | http://localhost:5050 |
| ETL | - | Transformation process | - |

---

## Installation and Execution Guide

### Prerequisites

| Software | Minimum Version | Installation |
|----------|-----------------|--------------|
| Git | 2.0+ | `sudo apt install git` |
| Docker | 20.10+ | [docs.docker.com](https://docs.docker.com/engine/install/) |
| Docker Compose | 2.0+ | [docs.docker.com](https://docs.docker.com/compose/install/) |
| Python | 3.8+ | Only for external notebooks |
| Power BI Desktop | Latest | [powerbi.microsoft.com](https://powerbi.microsoft.com/) |

---

### Step 1: Clone the Repository

```bash
# Clone
git clone git@github.com:driosoft-pro/etl-2026-2-ods3-salud.git

# Enter directory
cd etl-2026-2-ods3-salud
```

---

### Step 2: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your preferences (optional)
nano .env
```

**`.env` content:**
```bash
POSTGRES_DB=salud_colombia
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=etl_password_2026
POSTGRES_PORT=5432
DB_URL=postgresql://etl_user:etl_password_2026@localhost:5432/salud_colombia
PGADMIN_DEFAULT_EMAIL=admin@salud.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

---

### Step 3: Start Docker Infrastructure

```bash
# Build images and start services
docker-compose up -d

# Verify containers are running
docker-compose ps

# View PostgreSQL logs (wait for "ready to accept connections")
docker logs -f warehouse_salud
```

**Expected output:**
```
warehouse_salud  | LOG:  database system is ready to accept connections
```

---

### Step 4: Run ETL Process

```bash
# Run complete ETL process
docker-compose run --rm etl
```

**Expected output:**
```
============================================================
ETL PROCESS STARTED - HEALTH COLOMBIA
============================================================
PHASE 1: EXTRACTION
PHASE 2: TRANSFORMATION
PHASE 3: LOADING
============================================================
ETL PROCESS COMPLETED SUCCESSFULLY
============================================================

LOAD SUMMARY:
   dim_time:          XX records
   dim_department:    XX records
   dim_municipality:  XX records
   ...
```

---

### Step 5: Access pgAdmin

1. Open browser: **http://localhost:5050**
2. Login:
   - Email: `admin@salud.com`
   - Password: `admin123`
3. Register server:
   - Right-click "Servers" → "Register" → "Server"
   - **General → Name:** `Health Colombia`
   - **Connection → Tab "Connection":**
     - Host name/address: `postgres`
     - Port: `5432`
     - Maintenance database: `salud_colombia`
     - Username: `etl_user`
     - Password: `etl_password_2026`
   - Click "Save"

---

### Step 6: Run Validation Notebook (Optional)

```bash
# Start Jupyter Notebook
docker-compose run --rm -p 8888:8888 etl jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Open in browser: http://localhost:8888
```

---

## Power BI Connection (Linux)

Power BI Desktop is a Windows application, but can be used on Linux via:

### Option 1: Power BI Service (Recommended for Linux)

1. Open Power BI Service: https://app.powerbi.com
2. Click "Get Data" → "Database" → "PostgreSQL database"
3. Configure connection:
   - **Server:** `localhost:5432`
   - **Database:** `salud_colombia`
4. Enter credentials:
   - Username: `etl_user`
   - Password: `etl_password_2026`
5. Select tables to import

### Option 2: Power BI Desktop via Wine (Linux)

```bash
# Install Wine (Ubuntu/Debian)
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32

# Download Power BI Desktop
wget https://download.microsoft.com/download/8/6/6/866C4D51-A3D0-46CF-8B1D-B3F1AD78B362/PBIDesktopSetup_x64.exe

# Install via Wine
wine PBIDesktopSetup_x64.exe

# Run
wine ~/.wine/drive_c/Program\ Files/Microsoft\ Power\ BI\ Desktop/bin/PBIDesktop.exe
```

### Option 3: Direct Connection via Network Bridge

PostgreSQL in Docker already exposes port 5432 to the host. Power BI can connect directly:

```
Power BI Desktop (Windows)
    ↓ localhost:5432
Docker Container (PostgreSQL)
    ↓ Internal port 5432
Database salud_colombia
```

**Power BI Configuration:**
1. Get Data → PostgreSQL
2. Server: `localhost` or `127.0.0.1`
3. Port: `5432`
4. Database: `salud_colombia`
5. Username: `etl_user`
6. Password: `etl_password_2026`

### Tables Available for Power BI

| Table | Description | Recommended Use |
|-------|-------------|-----------------|
| `v_affiliates_summary` | Consolidated affiliates view | Analysis by department/municipality |
| `v_facility_summary` | Consolidated facility view | Installed capacity analysis |
| `fact_affiliates` | Affiliates facts | Dimensional modeling |
| `fact_facility_capacity` | Capacity facts | Dimensional modeling |
| `dim_time` | Time dimension | Filters by year/month/quarter |
| `dim_department` | Geographic dimension | Filters by department |
| `dim_municipality` | Geographic dimension | Filters by municipality |
| `dim_regime` | Regime dimension | Filters by regime type |
| `dim_facility` | Facility dimension | Analysis by institution |
| `dim_capacity_type` | Capacity dimension | Filters by resource type |

### Power BI Dashboard Design

The dashboard should include the following visualizations to address the analytical requirements:

| Visualization | Type | Purpose | Requirement |
|---------------|------|---------|-------------|
| **Choropleth Map** | Map by department | Color-coded by subsidized/contributive ratio to show regional vulnerability | R3 |
| **Temporal Line Chart** | Lines by quarter | Evolution of quarterly affiliates by regime and department | R2, R4 |
| **KPI Cards** | Card visuals | Total national affiliates, contributory coverage percentage, subsidized/contributive ratio | Overview |
| **Bar Chart** | Horizontal bars | Top 10 / Bottom 10 municipalities by contributory volume | R1 |
| **Quartile Table** | Matrix | Municipalities classified by coverage quartile with color coding | R5 |
| **Bed-to-Affiliate Ratio** | Map or table | Hospitals beds per 1,000 subsidized affiliates by municipality | IPS Analysis |

**Dynamic Filters (Slicers):**
- Year selector
- Department selector
- Regime type toggle (Contributivo / Subsidiado / Todos)
- Geographic region filter (Amazonia, Orinoquia, Pacific, Andina, Caribe, Insular)

---

## Useful Docker Commands

```bash
# View container status
docker-compose ps

# View logs in real time
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean data)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Enter PostgreSQL container
docker exec -it warehouse_salud psql -U etl_user -d salud_colombia

# Database backup
docker exec warehouse_salud pg_dump -U etl_user salud_colombia > backup.sql

# Restore backup
cat backup.sql | docker exec -i warehouse_salud psql -U etl_user -d salud_colombia
```

---

## Test Execution

### Test Structure

```
tests/
├── test_data_validation.py    # Raw data validation
├── test_extract.py           # Extraction tests
├── test_transform.py         # Transformation tests
├── test_load.py              # Load and DB connection tests
└── test_integration.py       # Full integration tests
```

### Run Tests

```bash
# Run all unit tests (no DB required)
./run_tests.sh unit

# Run data validation tests
./run_tests.sh data

# Run integration tests (DB required)
./run_tests.sh integration

# Run ALL tests
./run_tests.sh all
```

### Run with Docker

```bash
# Run tests inside ETL container
docker-compose run --rm etl python -m pytest tests/ -v

# Run only unit tests
docker-compose run --rm etl python -m pytest tests/ -v -m "unit"
```

### Run with pytest Directly

```bash
# Install test dependencies
pip install -r tests/requirements-tests.txt

# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=src --cov-report=html
```

### Test Types

| Type | Marker | Description | Requires DB |
|------|--------|-------------|-------------|
| Unit | `@pytest.mark.unit` | Isolated function tests | No |
| Data | `@pytest.mark.data` | Dataset validation | No |
| Integration | `@pytest.mark.integration` | Database tests | Yes |

---

## Analytical SQL Queries (R1-R5)

### R1: 10 Municipalities with Lowest Contributory Affiliates (Last Year)

```sql
-- Identificar los 10 municipios con menor volumen de afiliados al régimen contributivo
-- en el último año reportado para priorizar planes de formalización laboral
SELECT
    g.municipio,
    g.departamento,
    g.region,
    SUM(f.numero_afiliados) AS total_contributivos
FROM fact_afiliates f
JOIN dim_tiempo t ON f.sk_tiempo = t.sk_tiempo
JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
WHERE r.codigo_regimen = 'C'
  AND t.anio = (SELECT MAX(anio) FROM dim_tiempo)
GROUP BY g.municipio, g.departamento, g.region
HAVING SUM(f.numero_afiliados) > 0
ORDER BY total_contributivos ASC
LIMIT 10;
```

### R2: Subsidized Growth Rate Evolution by Department (Year/Quarter)

```sql
-- Analizar la evolución temporal (año/trimestre) de la tasa de crecimiento
-- de afiliados al régimen subsidiado por departamento
WITH subsidizados AS (
    SELECT
        g.departamento,
        t.anio,
        t.trimestre,
        t.periodo_codigo,
        SUM(f.numero_afiliados) AS total_subsidizados
    FROM fact_afiliates f
    JOIN dim_tiempo t ON f.sk_tiempo = t.sk_tiempo
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
    WHERE r.codigo_regimen = 'S'
    GROUP BY g.departamento, t.anio, t.trimestre, t.periodo_codigo
),
con_crecimiento AS (
    SELECT
        departamento,
        anio,
        trimestre,
        periodo_codigo,
        total_subsidizados,
        LAG(total_subsidizados) OVER (
            PARTITION BY departamento ORDER BY anio, trimestre
        ) AS total_anterior
    FROM subsidizados
)
SELECT
    departamento,
    anio,
    trimestre,
    periodo_codigo,
    total_subsidizados,
    total_anterior,
    CASE
        WHEN total_anterior > 0 THEN
            ROUND(((total_subsidizados - total_anterior)::NUMERIC / total_anterior) * 100, 2)
        ELSE NULL
    END AS tasa_crecimiento_pct
FROM con_crecimiento
ORDER BY departamento, anio, trimestre;
```

### R3: Subsidized vs Contributory Proportion by Geographic Subregion

```sql
-- Comparar la proporción entre régimen subsidiado vs. contributivo
-- por subregión geográfica para mapear vulnerabilidad socioeconómica
SELECT
    g.region,
    SUM(CASE WHEN r.codigo_regimen = 'S' THEN f.numero_afiliados ELSE 0 END) AS total_subsidiado,
    SUM(CASE WHEN r.codigo_regimen = 'C' THEN f.numero_afiliados ELSE 0 END) AS total_contributivo,
    SUM(f.numero_afiliados) AS total_general,
    ROUND(
        SUM(CASE WHEN r.codigo_regimen = 'S' THEN f.numero_afiliados ELSE 0 END)::NUMERIC /
        NULLIF(SUM(CASE WHEN r.codigo_regimen = 'C' THEN f.numero_afiliados ELSE 0 END), 0),
        2
    ) AS ratio_subsidiado_contributivo,
    ROUND(
        SUM(CASE WHEN r.codigo_regimen = 'S' THEN f.numero_afiliados ELSE 0 END)::NUMERIC /
        NULLIF(SUM(f.numero_afiliados), 0) * 100,
        2
    ) AS pct_subsidiado
FROM fact_afiliates f
JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
GROUP BY g.region
ORDER BY pct_subsidiado DESC;
```

### R4: Quarters with Largest Net Drops in Contributory Affiliation

```sql
-- Determinar los trimestres con mayores caídas netas de afiliación
-- contributiva a nivel departamental
WITH contributivos AS (
    SELECT
        g.departamento,
        t.anio,
        t.trimestre,
        t.periodo_codigo,
        SUM(f.numero_afiliados) AS total_contributivo
    FROM fact_afiliates f
    JOIN dim_tiempo t ON f.sk_tiempo = t.sk_tiempo
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
    WHERE r.codigo_regimen = 'C'
    GROUP BY g.departamento, t.anio, t.trimestre, t.periodo_codigo
),
con_variacion AS (
    SELECT
        departamento,
        anio,
        trimestre,
        periodo_codigo,
        total_contributivo,
        LAG(total_contributivo) OVER (
            PARTITION BY departamento ORDER BY anio, trimestre
        ) AS total_anterior,
        total_contributivo - LAG(total_contributivo) OVER (
            PARTITION BY departamento ORDER BY anio, trimestre
        ) AS variacion_neta
    FROM contributivos
)
SELECT
    departamento,
    anio,
    trimestre,
    periodo_codigo,
    total_contributivo,
    total_anterior,
    variacion_neta
FROM con_variacion
WHERE variacion_neta < 0
ORDER BY variacion_neta ASC
LIMIT 20;
```

### R5: Municipalities Classified by Coverage Quartiles

```sql
-- Clasificar los municipios en cuartiles según su cobertura de afiliación total
-- para detectar rezago en acceso territorial
WITH cobertura AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        g.region,
        SUM(f.numero_afiliados) AS total_afiliados
    FROM fact_afiliates f
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento, g.region
),
con_cuartiles AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY total_afiliados) AS cuartil
    FROM cobertura
)
SELECT
    codigo_dane_municipio,
    municipio,
    departamento,
    region,
    total_afiliados,
    cuartil,
    CASE cuartil
        WHEN 1 THEN 'Muy bajo rezago'
        WHEN 2 THEN 'Bajo rezago'
        WHEN 3 THEN 'Moderado'
        WHEN 4 THEN 'Alta cobertura'
    END AS clasificacion_cobertura
FROM con_cuartiles
ORDER BY cuartil, total_afiliados;
```

### IPS-Affiliate Cross Analysis: Hospital Beds per Subsidized Affiliate

```sql
-- Número de camas hospitalarias por cada 1.000 afiliados al régimen subsidiado
-- para detectar "desiertos de salud" (municipios con alta población asegurada
-- pero sin infraestructura suficiente)
WITH afiliados_subsidiado AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        SUM(f.numero_afiliados) AS total_subsidiado
    FROM fact_afiliates f
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
    WHERE r.codigo_regimen = 'S'
    GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento
),
camas AS (
    SELECT
        m.code AS codigo_dane_municipio,
        SUM(c.capacity_amount) AS total_camas
    FROM fact_facility_capacity fc
    JOIN dim_facility i ON fc.sk_facility = i.sk_facility
    JOIN dim_municipio m ON i.sk_municipality = m.sk_municipality
    JOIN dim_capacity_type ct ON fc.sk_capacity_type = ct.sk_capacity_type
    WHERE ct.group = 'CAMAS'
    GROUP BY m.code
)
SELECT
    a.municipio,
    a.departamento,
    a.total_subsidiado,
    COALESCE(c.total_camas, 0) AS total_camas,
    ROUND(
        COALESCE(c.total_camas, 0)::NUMERIC / NULLIF(a.total_subsidiado, 0) * 1000,
        2
    ) AS camas_por_1000_subsidiados,
    CASE
        WHEN COALESCE(c.total_camas, 0) = 0 THEN 'Desierto de salud'
        WHEN COALESCE(c.total_camas, 0)::NUMERIC / NULLIF(a.total_subsidiado, 0) * 1000 < 1.0 THEN 'Infraestructura crítica'
        WHEN COALESCE(c.total_camas, 0)::NUMERIC / NULLIF(a.total_subsidiado, 0) * 1000 < 2.0 THEN 'Infraestructura insuficiente'
        ELSE 'Infraestructura adecuada'
    END AS evaluacion_infraestructura
FROM afiliados_subsidiado a
LEFT JOIN camas c ON a.codigo_dane_municipio = c.codigo_dane_municipio
ORDER BY camas_por_1000_subsidiados ASC;
```

### Public vs Private Provider Ratio by Contributory Predominance

```sql
-- Ratio de prestadores públicos vs. privados según predominio de cotizantes contributivos
SELECT
    g.departamento,
    SUM(CASE WHEN i.nature = 'Publica' THEN 1 ELSE 0 END) AS prestadores_publicos,
    SUM(CASE WHEN i.nature = 'Privada' THEN 1 ELSE 0 END) AS prestadores_privados,
    ROUND(
        SUM(CASE WHEN i.nature = 'Publica' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(SUM(CASE WHEN i.nature = 'Privada' THEN 1 ELSE 0 END), 0),
        2
    ) AS ratio_publico_privado
FROM dim_facility i
JOIN dim_municipality m ON i.sk_municipality = m.sk_municipality
JOIN dim_department d ON m.sk_department = d.sk_department
JOIN dim_geografia g ON g.codigo_dane_depto = d.code
GROUP BY g.departamento
ORDER BY ratio_publico_privado DESC;
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| PostgreSQL won't start | Check port 5432 isn't in use: `sudo lsof -i :5432` |
| Permission denied on volumes | Run: `sudo chown -R $USER:$USER ./data ./logs` |
| ETL container fails | Check logs: `docker-compose logs etl` |
| Power BI won't connect | Verify PostgreSQL is running: `docker-compose ps` |
| No data in tables | Run ETL: `docker-compose run --rm etl` |
| Jupyter won't start | Check port: `sudo lsof -i :8888` |

---

## Data Sources

- **Affiliates**: SISPRO - Number of affiliates by department, municipality, and regime (Contributivo, Subsidiado, Excepción/Especial). Contains department codes, municipality codes, regime ID, year, month, and number of persons.
- **Facilities (REPS)**: Ministry of Health - Public and private healthcare facilities (IPS) by care level and installed capacity. Contains provider code, provider name, NIT, nature (public/private), care level (1-5), capacity type (beds, rooms), installed capacity, and cutoff date.

### Cross-Reference: IPS and Affiliates

Both datasets can be joined by `codigo_dane_municipio` (DANE municipality code) to answer:

| Metric | Description |
|--------|-------------|
| Hospital beds per 1,000 subsidized affiliates | Infrastructure adequacy for subsidized population |
| Public vs private provider ratio by contributory predominance | Provider mix alignment with economic activity |
| Health desert detection | Municipalities with high insured population but no medium/high complexity facilities |

## License

Academic project - Universidad Autónoma de Occidente
Course: ETL - 2026-2

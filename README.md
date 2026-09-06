# Health Analytics Colombia - Dimensional Data Warehouse

ETL project for analyzing healthcare system affiliates and facility capacity in Colombia. Uses Docker and PostgreSQL as a dimensional data warehouse.

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

### Star Model

``` mermaid
erDiagram
    dim_tiempo ||--o{ fact_afiliados : registra
    dim_regimen ||--o{ fact_afiliados : clasifica
    dim_municipio ||--o{ fact_afiliados : localiza
    dim_departamento ||--o{ fact_afiliados : agrupa
    dim_departamento ||--o{ dim_municipio : contiene
    dim_ips ||--o{ fact_afiliados : atiende
    dim_ips ||--o{ dim_tipo_capacidad : clasifica_por

    fact_afiliados {
        int fact_sk PK
        int tiempo_sk FK
        int departamento_sk FK
        int municipio_sk FK
        int regimen_sk FK
        int ips_sk FK
        int numero_afiliados
    }

    dim_tiempo {
        int tiempo_sk PK
        int anio
        int trimestre
    }

    dim_departamento {
        int departamento_sk PK
        string cod_dane_depto
        string departamento
    }

    dim_municipio {
        int municipio_sk PK
        int departamento_sk FK
        string cod_dane_mpio
        string municipio
    }

    dim_regimen {
        int regimen_sk PK
        string tipo_regimen
    }

    dim_ips {
        int ips_sk PK
        string codigo_habilitacion
        string nombre_ips
        int tipo_capacidad_sk FK
    }

    dim_tipo_capacidad {
        int tipo_capacidad_sk PK
        string nivel_complejidad
        string naturaleza_juridica
    }
```

**Fact Tables:**
- `fact_affiliates`: Number of affiliated persons by municipality, regime, and time
- `fact_facility_capacity`: Installed capacity by facility and capacity type

**Dimensions:**
- `dim_time`: Year, month, quarter, semester
- `dim_department`: Code and department name
- `dim_municipality`: Code, name, and department
- `dim_regime`: Code and regime description (Subsidized, Special, Contributory)
- `dim_facility`: Healthcare facility (IPS) data
- `dim_capacity_type`: Group and capacity description (BEDS, STRETCHERS, etc.)

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

## Example Queries

```sql
-- Total affiliates by department
SELECT d.name, SUM(f.num_personas) as total_affiliates
FROM fact_affiliates f
JOIN dim_municipality m ON f.sk_municipality = m.sk_municipality
JOIN dim_department d ON m.sk_department = d.sk_department
GROUP BY d.name
ORDER BY total_affiliates DESC;

-- Facilities by nature type
SELECT i.nature, COUNT(*) as total_facilities
FROM dim_facility i
GROUP BY i.nature;

-- Installed capacity by type
SELECT ct.description, SUM(c.capacity_amount) as total_capacity
FROM fact_facility_capacity c
JOIN dim_capacity_type ct ON c.sk_capacity_type = ct.sk_capacity_type
GROUP BY ct.description
ORDER BY total_capacity DESC;

-- Affiliates by regime and year
SELECT t.year, r.description, SUM(f.num_personas) as total
FROM fact_affiliates f
JOIN dim_time t ON f.sk_time = t.sk_time
JOIN dim_regime r ON f.sk_regime = r.sk_regime
GROUP BY t.year, r.description
ORDER BY t.year, r.description;

-- Top 10 municipalities with most affiliates
SELECT m.name, d.name as department, SUM(f.num_personas) as total
FROM fact_affiliates f
JOIN dim_municipality m ON f.sk_municipality = m.sk_municipality
JOIN dim_department d ON m.sk_department = d.sk_department
GROUP BY m.name, d.name
ORDER BY total DESC
LIMIT 10;
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

- **Affiliates**: SISPRO - Number of affiliates by department, municipality, and regime
- **Facilities**: REPS - Public and private healthcare facilities by care level and installed capacity

## License

Academic project - Universidad EAFIT
Course: ETL and Data Analysis - 2026-2
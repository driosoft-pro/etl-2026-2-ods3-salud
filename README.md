# Health Analytics Colombia - Dimensional Data Warehouse

ETL project for analyzing healthcare system affiliates and facility capacity in Colombia. Uses Docker/Podman and PostgreSQL as a dimensional data warehouse.

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
├── sql/
│   └── init.sql                                # Dimensional schema
├── src/
│   ├── __init__.py
│   ├── config.py                               # Project configuration
│   ├── extract.py                              # Extraction phase
│   ├── transform.py                            # Transformation phase
│   ├── validate.py                             # Validation phase
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
│   └── run_tests.py                            # Test runner script
├── notebooks/
│   └── 01_data_validation_cleanup.ipynb        # Validation and cleanup
├── logs/                                       # ETL process logs
├── docker-compose.yml                          # Docker/Podman infrastructure
├── Dockerfile                                  # ETL process image
├── requirements.txt                            # Python dependencies
├── run_tests.sh                                # Quick test runner (Linux/macOS)
├── run_tests.bat                               # Quick test runner (Windows)
├── .env                                        # Environment variables (not in Git)
├── .env.example                                # Variables template
├── .gitignore
└── README.md
```

## Dimensional Schema

### Fact Table Granularity

> **A row in `fact_affiliates` represents the total accumulated affiliates for a specific health regime, in a given municipality, during a specific quarter and year.**

> **A row in `fact_facility_capacity` represents the installed capacity (beds, rooms) for a specific healthcare facility and capacity type, at a point-in-time snapshot.**

### Why Two Fact Tables?

The project uses **two fact tables** because they measure fundamentally different business processes with different granularities and additive properties:

| Aspect | `fact_affiliates` | `fact_facility_capacity` |
|--------|-------------------|--------------------------|
| **Business process** | Health insurance enrollment | Hospital infrastructure capacity |
| **Grain** | Municipality + Regime + Quarter | Facility + Capacity Type + Snapshot |
| **Additivity** | Additive across time (can sum quarters) | Non-additive (snapshot, not accumulable) |
| **Measures** | `numero_afiliados` (people) | `capacity_amount` (beds/rooms) |
| **Temporal behavior** | Changes monthly (enrollment flux) | Static snapshot (infrastructure changes slowly) |
| **Analytical use** | R1-R5: enrollment trends, regime comparison | Cross-analysis: beds per 1,000 affiliates |

### Temporal Quarantine

The two source datasets have **different temporal coverage**:

- **Affiliates (SISPRO)**: Snapshot from **April 2022** (Q2 2022)
- **Facilities (REPS)**: Snapshot from **November 2022** (Q4 2022)

Since the data covers different months within the same year, direct temporal comparisons between affiliates and facilities are **not valid**. The ETL implements a **quarantine approach**:

1. `fact_affiliates` stores data for Q2 2022 (April)
2. `fact_facility_capacity` stores data for Q4 2022 (November)
3. Cross-dataset analytical queries (beds per affiliate) use **both snapshots** with an explicit note that they represent different points in time
4. Temporal trend analysis (R2, R4) is limited to `fact_affiliates` only

### Star Model

``` mermaid
erDiagram
    dim_tiempo ||--o{ fact_afiliados : registra
    dim_regimen ||--o{ fact_afiliados : clasifica
    dim_geografia ||--o{ fact_afiliados : localiza
    dim_geografia ||--o{ dim_municipio : contiene
    dim_tiempo ||--o{ fact_capacidad : registra
    dim_ips ||--o{ fact_capacidad : atiende
    dim_tipo_capacidad ||--o{ fact_capacidad : clasifica

    fact_afiliados {
        int sk_affiliate PK
        int sk_geografia FK
        int sk_tiempo FK
        int sk_regimen FK
        int numero_afiliados
    }

    fact_capacidad {
        int sk_capacity PK
        int sk_tiempo FK
        int sk_facility FK
        int sk_capacity_type FK
        int capacity_amount
    }

    dim_tiempo {
        int sk_time PK
        int year
        int quarter
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
        int sk_municipality PK
        string code
        string name
        int sk_department FK
    }

    dim_regimen {
        int sk_regime PK
        string code
        string description
    }

    dim_ips {
        int sk_facility PK
        string provider_code
        string name
        string nature
        int care_level
        int sk_municipality FK
    }

    dim_tipo_capacidad {
        int sk_capacity_type PK
        string group
        string description
    }
```

**Dimensions:**
- `dim_time` (Time): Year, quarter, semester, period code (e.g. 2022-Q2)
- `dim_geografia` (Geography): Municipality code/name, department code/name, geographic region (Amazonia, Orinoquia, Pacifico, Andina, Caribe, Insular)
- `dim_department` / `dim_municipality`: Normalized department and municipality for facility path
- `dim_regime` (Regime): Code and description (Contributivo, Subsidiado, Especial, Individual)
- `dim_facility` (Healthcare Facility / IPS): Provider data linked to municipality
- `dim_capacity_type` (Capacity Type): Group and description (CAMAS, SALAS, etc.)

### Text Normalization

All department and municipality names are normalized to prevent duplicates across datasets:
1. **Accent stripping**: `Boyacá` → `BOYACA`
2. **Case unification**: `Atlántico` → `ATLANTICO`
3. **Name harmonization**: `Valle del cauca` → `VALLE DEL CAUCA`
4. **Invalid data filtering**: `NO APLICA` department rows are removed
5. **DANE codes**: Standardized from affiliate data (33 departments + Bogotá D.C.)

## Docker Infrastructure

| Service | Port | Description | URL |
|---------|------|-------------|-----|
| PostgreSQL | 5432 | Data Warehouse | localhost:5432 |
| pgAdmin | 5050 | Database web interface | http://localhost:5050 |
| ETL | - | Transformation process | - |

---

## Installation and Execution Guide

### Prerequisites

| Software | Minimum Version | Notes |
|----------|-----------------|-------|
| Git | 2.0+ | Required |
| Docker **or** Podman | Docker 20.10+ / Podman 4.0+ | Install one; both work identically |
| Docker Compose **or** Podman Compose | Compose 2.0+ / podman-compose | Included with Docker Desktop |
| Python | 3.11+ | Only for running tests locally outside containers |
| Power BI Desktop | Latest | Optional, for visualization (Windows only) |

> **Docker vs Podman:** All commands below work with both. On Windows, Docker Desktop is the simplest option. Podman can replace Docker 1:1 — just install `podman-compose` (`pip install podman-compose`) and use `podman-compose` in place of `docker-compose`.

---

### Step 1: Clone the Repository

```bash
git clone git@github.com:driosoft-pro/etl-2026-2-ods3-salud.git
cd etl-2026-2-ods3-salud
```

---

### Step 2: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your preferred credentials (optional — defaults work out of the box):

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

### Step 3: Start Infrastructure

#### Windows (PowerShell) — Docker

```powershell
docker compose up -d
docker compose ps
docker logs -f warehouse_salud
```

#### Windows (PowerShell) — Podman

```powershell
podman-compose up -d
podman-compose ps
podman logs -f warehouse_salud
```

#### Linux/macOS — Docker

```bash
docker compose up -d
docker compose ps
docker logs -f warehouse_salud
```

#### Linux/macOS — Podman

```bash
podman-compose up -d
podman-compose ps
podman logs -f warehouse_salud
```

> **Note:** On NixOS, use `nix develop` first to get docker-compose in your PATH.

Wait for PostgreSQL to be ready:
```
warehouse_salud  | LOG:  database system is ready to accept connections
```

---

### Step 4: Run ETL Process

#### Windows (PowerShell) — Docker

```powershell
docker compose run --rm etl
```

#### Windows (PowerShell) — Podman

```powershell
podman-compose run --rm etl
```

#### Linux/macOS — Docker

```bash
docker compose run --rm etl
```

#### Linux/macOS — Podman

```bash
podman-compose run --rm etl
```

**Expected output:**
```
============================================================
ETL PROCESS STARTED - HEALTH COLOMBIA
============================================================
PHASE 1: EXTRACTION
PHASE 2: TRANSFORMATION
PHASE 2.5: VALIDATION
PHASE 3: LOADING
============================================================
ETL PROCESS COMPLETED SUCCESSFULLY
============================================================

 LOAD SUMMARY:
    dim_time:          X records
    dim_geografia:     X records
    dim_department:    X records
    dim_municipality:  X records
    dim_regime:        X records
    dim_facility:      X records
    dim_capacity_type: X records
    fact_affiliates:   X records (quarterly)
    fact_capacity:     X records
    validations:       X errors
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

### Step 6: Clean Up / Restart

#### Windows (PowerShell) — Docker

```powershell
# Stop all services
docker compose down

# Stop and remove volumes (clean data, forces full ETL re-run)
docker compose down -v

# Rebuild images (after code changes)
docker compose build --no-cache
```

#### Windows (PowerShell) — Podman

```powershell
podman-compose down
podman-compose down -v
podman-compose build --no-cache
```

#### Linux/macOS — Docker

```bash
docker compose down
docker compose down -v
docker compose build --no-cache
```

#### Linux/macOS — Podman

```bash
podman-compose down
podman-compose down -v
podman-compose build --no-cache
```

**Full reset (recommended after pulling new changes):**
```bash
# Docker
docker compose down -v && docker compose build --no-cache && docker compose up -d && docker compose run --rm etl

# Podman
podman-compose down -v && podman-compose build --no-cache && podman-compose up -d && podman-compose run --rm etl
```

---

## Test Execution

### Run Tests Locally (Outside Containers)

#### Linux/macOS

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

#### Windows (PowerShell)

```powershell
# Run all unit tests
.\run_tests.bat unit

# Run ALL tests
.\run_tests.bat all
```

### Run Tests Inside Containers

```bash
# Docker
docker compose run --rm etl python -m pytest tests/ -v

# Podman
podman-compose run --rm etl python -m pytest tests/ -v
```

### Run Tests with pytest Directly

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Test Types

| Type | Marker | Description | Requires DB |
|------|--------|-------------|-------------|
| Unit | `@pytest.mark.unit` | Isolated function tests | No |
| Data | `@pytest.mark.data` | Dataset validation | No |
| Integration | `@pytest.mark.integration` | Database tests | Yes |

---

## Useful Container Commands

```bash
# View container status
docker compose ps          # or: podman-compose ps

# View logs in real time
docker compose logs -f      # or: podman-compose logs -f

# Enter PostgreSQL container
docker exec -it warehouse_salud psql -U etl_user -d salud_colombia

# Database backup
docker exec warehouse_salud pg_dump -U etl_user salud_colombia > backup.sql

# Restore backup
cat backup.sql | docker exec -i warehouse_salud psql -U etl_user -d salud_colombia
```

---

## Analytical SQL Queries (R1-R5)

### R1: 10 Municipalities with Lowest Contributory Affiliates (Last Year)

```sql
SELECT
    g.municipio,
    g.departamento,
    g.region,
    SUM(f.numero_afiliados) AS total_contributivos
FROM fact_affiliates f
JOIN dim_time t ON f.sk_time = t.sk_time
JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
JOIN dim_regime r ON f.sk_regime = r.sk_regime
WHERE r.code = 'C'
  AND t.year = (SELECT MAX(year) FROM dim_time)
GROUP BY g.municipio, g.departamento, g.region
HAVING SUM(f.numero_afiliados) > 0
ORDER BY total_contributivos ASC
LIMIT 10;
```

### R2: Subsidized Growth Rate Evolution by Department (Year/Quarter)

```sql
WITH subsidizados AS (
    SELECT
        g.departamento,
        t.year,
        t.quarter,
        t.periodo_codigo,
        SUM(f.numero_afiliados) AS total_subsidizados
    FROM fact_affiliates f
    JOIN dim_time t ON f.sk_time = t.sk_time
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regime r ON f.sk_regime = r.sk_regime
    WHERE r.code = 'S'
    GROUP BY g.departamento, t.year, t.quarter, t.periodo_codigo
),
con_crecimiento AS (
    SELECT
        departamento, year, quarter, periodo_codigo, total_subsidizados,
        LAG(total_subsidizados) OVER (
            PARTITION BY departamento ORDER BY year, quarter
        ) AS total_anterior
    FROM subsidizados
)
SELECT
    departamento, year, quarter, periodo_codigo,
    total_subsidizados, total_anterior,
    CASE
        WHEN total_anterior > 0 THEN
            ROUND(((total_subsidizados - total_anterior)::NUMERIC / total_anterior) * 100, 2)
        ELSE NULL
    END AS tasa_crecimiento_pct
FROM con_crecimiento
ORDER BY departamento, year, quarter;
```

### R3: Subsidized vs Contributory Proportion by Geographic Subregion

```sql
SELECT
    g.region,
    SUM(CASE WHEN r.code = 'S' THEN f.numero_afiliados ELSE 0 END) AS total_subsidiado,
    SUM(CASE WHEN r.code = 'C' THEN f.numero_afiliados ELSE 0 END) AS total_contributivo,
    SUM(f.numero_afiliados) AS total_general,
    ROUND(
        SUM(CASE WHEN r.code = 'S' THEN f.numero_afiliados ELSE 0 END)::NUMERIC /
        NULLIF(SUM(CASE WHEN r.code = 'C' THEN f.numero_afiliados ELSE 0 END), 0),
        2
    ) AS ratio_subsidiado_contributivo,
    ROUND(
        SUM(CASE WHEN r.code = 'S' THEN f.numero_afiliados ELSE 0 END)::NUMERIC /
        NULLIF(SUM(f.numero_afiliados), 0) * 100,
        2
    ) AS pct_subsidiado
FROM fact_affiliates f
JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
JOIN dim_regime r ON f.sk_regime = r.sk_regime
GROUP BY g.region
ORDER BY pct_subsidiado DESC;
```

### R4: Quarters with Largest Net Drops in Contributory Affiliation

```sql
WITH contributivos AS (
    SELECT
        g.departamento,
        t.year,
        t.quarter,
        t.periodo_codigo,
        SUM(f.numero_afiliados) AS total_contributivo
    FROM fact_affiliates f
    JOIN dim_time t ON f.sk_time = t.sk_time
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regime r ON f.sk_regime = r.sk_regime
    WHERE r.code = 'C'
    GROUP BY g.departamento, t.year, t.quarter, t.periodo_codigo
),
con_variacion AS (
    SELECT
        departamento, year, quarter, periodo_codigo, total_contributivo,
        LAG(total_contributivo) OVER (
            PARTITION BY departamento ORDER BY year, quarter
        ) AS total_anterior,
        total_contributivo - LAG(total_contributivo) OVER (
            PARTITION BY departamento ORDER BY year, quarter
        ) AS variacion_neta
    FROM contributivos
)
SELECT departamento, year, quarter, periodo_codigo,
       total_contributivo, total_anterior, variacion_neta
FROM con_variacion
WHERE variacion_neta < 0
ORDER BY variacion_neta ASC
LIMIT 20;
```

### R5: Municipalities Classified by Coverage Quartiles

```sql
WITH cobertura AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        g.region,
        SUM(f.numero_afiliados) AS total_afiliados
    FROM fact_affiliates f
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento, g.region
),
con_cuartiles AS (
    SELECT *,
        NTILE(4) OVER (ORDER BY total_afiliados) AS cuartil
    FROM cobertura
)
SELECT
    codigo_dane_municipio, municipio, departamento, region,
    total_afiliados, cuartil,
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
WITH afiliados_subsidiado AS (
    SELECT
        g.codigo_dane_municipio,
        g.municipio,
        g.departamento,
        SUM(f.numero_afiliados) AS total_subsidiado
    FROM fact_affiliates f
    JOIN dim_geografia g ON f.sk_geografia = g.sk_geografia
    JOIN dim_regime r ON f.sk_regime = r.sk_regime
    WHERE r.code = 'S'
    GROUP BY g.codigo_dane_municipio, g.municipio, g.departamento
),
camas AS (
    SELECT
        m.code AS codigo_dane_municipio,
        SUM(c.capacity_amount) AS total_camas
    FROM fact_facility_capacity c
    JOIN dim_facility i ON c.sk_facility = i.sk_facility
    JOIN dim_municipality m ON i.sk_municipality = m.sk_municipality
    JOIN dim_capacity_type ct ON c.sk_capacity_type = ct.sk_capacity_type
    WHERE ct."group" = 'CAMAS'
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
        WHEN COALESCE(c.total_camas, 0)::NUMERIC / NULLIF(a.total_subsidiado, 0) * 1000 < 1.0 THEN 'Infraestructura critica'
        WHEN COALESCE(c.total_camas, 0)::NUMERIC / NULLIF(a.total_subsidiado, 0) * 1000 < 2.0 THEN 'Infraestructura insuficiente'
        ELSE 'Infraestructura adecuada'
    END AS evaluacion_infraestructura
FROM afiliados_subsidiado a
LEFT JOIN camas c ON a.codigo_dane_municipio = c.codigo_dane_municipio
ORDER BY camas_por_1000_subsidiados ASC;
```

### Public vs Private Provider Ratio by Department

```sql
SELECT
    d.name AS department,
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
GROUP BY d.name
ORDER BY ratio_publico_privado DESC;
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| PostgreSQL won't start | Check port 5432 isn't in use: `sudo lsof -i :5432` (Linux) or `netstat -ano \| findstr :5432` (Windows) |
| Permission denied on volumes | Linux: `sudo chown -R $USER:$USER ./data ./logs` |
| ETL container fails | Check logs: `docker compose logs etl` (or `podman-compose logs etl`) |
| `missing services [etlclear]` warning | Harmless podman-compose warning — can be ignored safely |
| No data in tables | Run ETL: `docker compose run --rm etl` (or `podman-compose run --rm etl`) |
| `pg_isready` fails | Wait longer — PostgreSQL may still be initializing on first run |
| Power BI won't connect | Verify PostgreSQL is running: `docker compose ps` |

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

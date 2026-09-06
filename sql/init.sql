-- =====================================================
-- DIMENSIONAL SCHEMA - HEALTH COLOMBIA
-- =====================================================

-- =====================================================
-- DIMENSIONS
-- =====================================================

-- Time Dimension
CREATE TABLE dim_time (
    sk_time SERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    full_date DATE NOT NULL,
    UNIQUE(year, month)
);

-- Department Dimension
CREATE TABLE dim_department (
    sk_department SERIAL PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL
);

-- Municipality Dimension
CREATE TABLE dim_municipality (
    sk_municipality SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    sk_department INTEGER NOT NULL REFERENCES dim_department(sk_department)
);

-- Regime Dimension
CREATE TABLE dim_regime (
    sk_regime SERIAL PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE,
    description VARCHAR(100) NOT NULL
);

-- Facility Dimension (Healthcare Institution)
CREATE TABLE dim_facility (
    sk_facility SERIAL PRIMARY KEY,
    provider_code VARCHAR(20) NOT NULL,
    name VARCHAR(300) NOT NULL,
    nit VARCHAR(20),
    nature VARCHAR(20),
    care_level INTEGER,
    manager VARCHAR(200),
    address VARCHAR(300),
    email VARCHAR(200),
    phone VARCHAR(20),
    sk_municipality INTEGER NOT NULL REFERENCES dim_municipality(sk_municipality),
    UNIQUE(provider_code, sk_municipality)
);

-- Capacity Type Dimension
CREATE TABLE dim_capacity_type (
    sk_capacity_type SERIAL PRIMARY KEY,
    "group" VARCHAR(50) NOT NULL,
    description VARCHAR(100) NOT NULL,
    UNIQUE("group", description)
);

-- =====================================================
-- FACT TABLES
-- =====================================================

-- Fact: Affiliates by municipality, regime, and time
CREATE TABLE fact_affiliates (
    sk_affiliate SERIAL PRIMARY KEY,
    sk_time INTEGER NOT NULL REFERENCES dim_time(sk_time),
    sk_municipality INTEGER NOT NULL REFERENCES dim_municipality(sk_municipality),
    sk_regime INTEGER NOT NULL REFERENCES dim_regime(sk_regime),
    num_persons BIGINT NOT NULL,
    UNIQUE(sk_time, sk_municipality, sk_regime)
);

-- Fact: Facility capacity by facility and time
CREATE TABLE fact_facility_capacity (
    sk_capacity SERIAL PRIMARY KEY,
    sk_time INTEGER NOT NULL REFERENCES dim_time(sk_time),
    sk_facility INTEGER NOT NULL REFERENCES dim_facility(sk_facility),
    sk_capacity_type INTEGER NOT NULL REFERENCES dim_capacity_type(sk_capacity_type),
    capacity_amount INTEGER NOT NULL,
    UNIQUE(sk_time, sk_facility, sk_capacity_type)
);

-- =====================================================
-- INDEXES FOR OPTIMIZATION
-- =====================================================

CREATE INDEX idx_fact_affiliates_time ON fact_affiliates(sk_time);
CREATE INDEX idx_fact_affiliates_municipality ON fact_affiliates(sk_municipality);
CREATE INDEX idx_fact_affiliates_regime ON fact_affiliates(sk_regime);

CREATE INDEX idx_fact_capacity_time ON fact_facility_capacity(sk_time);
CREATE INDEX idx_fact_capacity_facility ON fact_facility_capacity(sk_facility);
CREATE INDEX idx_fact_capacity_type ON fact_facility_capacity(sk_capacity_type);

CREATE INDEX idx_municipality_department ON dim_municipality(sk_department);
CREATE INDEX idx_facility_municipality ON dim_facility(sk_municipality);

-- =====================================================
-- SUMMARY VIEWS
-- =====================================================

CREATE VIEW v_affiliates_summary AS
SELECT 
    d.name AS department,
    m.name AS municipality,
    r.description AS regime,
    t.year,
    t.month,
    t.month_name,
    f.num_persons
FROM fact_affiliates f
JOIN dim_time t ON f.sk_time = t.sk_time
JOIN dim_municipality m ON f.sk_municipality = m.sk_municipality
JOIN dim_department d ON m.sk_department = d.sk_department
JOIN dim_regime r ON f.sk_regime = r.sk_regime;

CREATE VIEW v_facility_summary AS
SELECT 
    d.name AS department,
    m.name AS municipality,
    i.name AS facility,
    i.nature,
    ct."group" AS capacity_group,
    ct.description AS capacity_type,
    t.year,
    c.capacity_amount
FROM fact_facility_capacity c
JOIN dim_time t ON c.sk_time = t.sk_time
JOIN dim_facility i ON c.sk_facility = i.sk_facility
JOIN dim_municipality m ON i.sk_municipality = m.sk_municipality
JOIN dim_department d ON m.sk_department = d.sk_department
JOIN dim_capacity_type ct ON c.sk_capacity_type = ct.sk_capacity_type;
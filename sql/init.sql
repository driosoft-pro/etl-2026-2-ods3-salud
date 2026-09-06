-- =====================================================
-- ESQUEMA DIMENSIONAL - SALUD COLOMBIA
-- =====================================================

-- =====================================================
-- DIMENSIONES
-- =====================================================

-- Dimensión Tiempo
CREATE TABLE dim_tiempo (
    sk_tiempo SERIAL PRIMARY KEY,
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    trimestre INTEGER NOT NULL,
    semestre INTEGER NOT NULL,
    fecha_completa DATE NOT NULL,
    UNIQUE(anio, mes)
);

-- Dimensión Departamento
CREATE TABLE dim_departamento (
    sk_departamento SERIAL PRIMARY KEY,
    codigo VARCHAR(5) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL
);

-- Dimensión Municipio
CREATE TABLE dim_municipio (
    sk_municipio SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    sk_departamento INTEGER NOT NULL REFERENCES dim_departamento(sk_departamento)
);

-- Dimensión Régimen
CREATE TABLE dim_regimen (
    sk_regimen SERIAL PRIMARY KEY,
    codigo VARCHAR(5) NOT NULL UNIQUE,
    descripcion VARCHAR(100) NOT NULL
);

-- Dimensión IPS (Institución Prestadora de Servicios)
CREATE TABLE dim_ips (
    sk_ips SERIAL PRIMARY KEY,
    codigo_prestador VARCHAR(20) NOT NULL,
    nombre VARCHAR(300) NOT NULL,
    nit VARCHAR(20),
    naturaleza VARCHAR(20),
    nivel_atencion INTEGER,
    gerente VARCHAR(200),
    direccion VARCHAR(300),
    email VARCHAR(200),
    telefono VARCHAR(20),
    sk_municipio INTEGER NOT NULL REFERENCES dim_municipio(sk_municipio),
    UNIQUE(codigo_prestador, sk_municipio)
);

-- Dimensión Tipo Capacidad
CREATE TABLE dim_tipo_capacidad (
    sk_tipo_capacidad SERIAL PRIMARY KEY,
    grupo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    UNIQUE(grupo, descripcion)
);

-- =====================================================
-- TABLAS DE HECHOS
-- =====================================================

-- Hecho: Afiliados por municipio, régimen y tiempo
CREATE TABLE fact_afiliados (
    sk_afiliado SERIAL PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dim_tiempo(sk_tiempo),
    sk_municipio INTEGER NOT NULL REFERENCES dim_municipio(sk_municipio),
    sk_regimen INTEGER NOT NULL REFERENCES dim_regimen(sk_regimen),
    num_personas BIGINT NOT NULL,
    UNIQUE(sk_tiempo, sk_municipio, sk_regimen)
);

-- Hecho: Capacidad instalada por IPS y tiempo
CREATE TABLE fact_capacidad_ips (
    sk_capacidad SERIAL PRIMARY KEY,
    sk_tiempo INTEGER NOT NULL REFERENCES dim_tiempo(sk_tiempo),
    sk_ips INTEGER NOT NULL REFERENCES dim_ips(sk_ips),
    sk_tipo_capacidad INTEGER NOT NULL REFERENCES dim_tipo_capacidad(sk_tipo_capacidad),
    cantidad_capacidad INTEGER NOT NULL,
    UNIQUE(sk_tiempo, sk_ips, sk_tipo_capacidad)
);

-- =====================================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- =====================================================

CREATE INDEX idx_fact_afiliados_tiempo ON fact_afiliados(sk_tiempo);
CREATE INDEX idx_fact_afiliados_municipio ON fact_afiliados(sk_municipio);
CREATE INDEX idx_fact_afiliados_regimen ON fact_afiliados(sk_regimen);

CREATE INDEX idx_fact_capacidad_tiempo ON fact_capacidad_ips(sk_tiempo);
CREATE INDEX idx_fact_capacidad_ips ON fact_capacidad_ips(sk_ips);
CREATE INDEX idx_fact_capacidad_tipo ON fact_capacidad_ips(sk_tipo_capacidad);

CREATE INDEX idx_municipio_departamento ON dim_municipio(sk_departamento);
CREATE INDEX idx_ips_municipio ON dim_ips(sk_municipio);

-- =====================================================
-- VISTA RESUMEN
-- =====================================================

CREATE VIEW v_resumen_afiliados AS
SELECT 
    d.nombre AS departamento,
    m.nombre AS municipio,
    r.descripcion AS regimen,
    t.anio,
    t.mes,
    t.nombre_mes,
    f.num_personas
FROM fact_afiliados f
JOIN dim_tiempo t ON f.sk_tiempo = t.sk_tiempo
JOIN dim_municipio m ON f.sk_municipio = m.sk_municipio
JOIN dim_departamento d ON m.sk_departamento = d.sk_departamento
JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen;

CREATE VIEW v_resumen_capacidad AS
SELECT 
    d.nombre AS departamento,
    m.nombre AS municipio,
    i.nombre AS ips,
    i.naturaleza,
    tc.grupo AS tipo_grupo,
    tc.descripcion AS tipo_capacidad,
    t.anio,
    c.cantidad_capacidad
FROM fact_capacidad_ips c
JOIN dim_tiempo t ON c.sk_tiempo = t.sk_tiempo
JOIN dim_ips i ON c.sk_ips = i.sk_ips
JOIN dim_municipio m ON i.sk_municipio = m.sk_municipio
JOIN dim_departamento d ON m.sk_departamento = d.sk_departamento
JOIN dim_tipo_capacidad tc ON c.sk_tipo_capacidad = tc.sk_tipo_capacidad;
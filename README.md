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
│   ├── raw/                                    # Datos originales de SISPRO
│   │   ├── Número_de_afiliados_por_departamento,_municipio_y_régimen_20260906.csv
│   │   └── Relación_de_IPS_públicas_y_privadas_según_el_nivel_de_atención_y_capacidad_instalada_20260906.csv
│   └── processed/                              # Datos limpios (generados)
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
├── notebooks/
│   └── 01_validacion_limpieza_datos.ipynb      # Validación y limpieza
├── logs/                                       # Logs del proceso ETL
├── docker-compose.yml                          # Infraestructura Docker
├── Dockerfile                                  # Imagen del proceso ETL
├── requirements.txt                            # Dependencias Python
├── .env                                        # Variables de entorno (no subir a Git)
├── .env.example                                # Plantilla de variables
├── .gitignore
└── README.md
```

## Esquema Dimensional

### Modelo Star

```
                    ┌─────────────────┐
                    │   dim_tiempo    │
                    └────────┬────────┘
                             │
┌─────────────────┐    ┌─────┴─────┐    ┌─────────────────┐
│ dim_departamento├────┤fact_afiliados├────┤   dim_regimen   │
└────────┬────────┘    └─────┬─────┘    └─────────────────┘
         │                   │
┌────────┴────────┐          │          ┌─────────────────┐
│  dim_municipio  ├──────────┴──────────┤    dim_ips      │
└─────────────────┘                     └────────┬────────┘
                                                 │
                                        ┌────────┴────────┐
                                        │dim_tipo_capacidad│
                                        └─────────────────┘
```

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

| Servicio | Puerto | Descripción | URL |
|----------|--------|-------------|-----|
| PostgreSQL | 5432 | Data Warehouse | localhost:5432 |
| pgAdmin | 5050 | Interfaz web para BD | http://localhost:5050 |
| ETL | - | Proceso de transformación | - |

---

## Guía de Instalación y Ejecución

### Requisitos Previos

| Software | Versión Mínima | Instalación |
|----------|----------------|-------------|
| Git | 2.0+ | `sudo apt install git` |
| Docker | 20.10+ | [docs.docker.com](https://docs.docker.com/engine/install/) |
| Docker Compose | 2.0+ | [docs.docker.com](https://docs.docker.com/compose/install/) |
| Python | 3.8+ | Solo para notebooks externos |
| Power BI Desktop | Última | [powerbi.microsoft.com](https://powerbi.microsoft.com/) |

---

### Paso 1: Clonar el Repositorio

```bash
# Clonar
git clone https://github.com/username/salud-colombia-etl.git

# Entrar al directorio
cd salud-colombia-etl
```

---

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus preferencias (opcional)
nano .env
```

**Contenido del `.env`:**
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

### Paso 3: Levantar Infraestructura Docker

```bash
# Construir imágenes y levantar servicios
docker-compose up -d

# Verificar que los contenedores estén corriendo
docker-compose ps

# Ver logs de PostgreSQL (esperar "ready to accept connections")
docker logs -f warehouse_salud
```

**Salida esperada:**
```
warehouse_salud  | LOG:  database system is ready to accept connections
```

---

### Paso 4: Ejecutar el Proceso ETL

```bash
# Ejecutar el proceso ETL completo
docker-compose run --rm etl
```

**Salida esperada:**
```
============================================================
INICIO DEL PROCESO ETL - SALUD COLOMBIA
============================================================
FASE 1: EXTRACCIÓN
FASE 2: TRANSFORMACIÓN
FASE 3: CARGA
============================================================
PROCESO ETL COMPLETADO EXITOSAMENTE
============================================================

RESUMEN DE CARGA:
   dim_tiempo:          XX registros
   dim_departamento:    XX registros
   dim_municipio:       XX registros
   ...
```

---

### Paso 5: Acceder a pgAdmin

1. Abrir navegador: **http://localhost:5050**
2. Iniciar sesión:
   - Email: `admin@salud.com`
   - Password: `admin123`
3. Registrar servidor:
   - Click derecho en "Servers" → "Register" → "Server"
   - **General → Name:** `Salud Colombia`
   - **Connection → Tab "Connection":**
     - Host name/address: `postgres`
     - Port: `5432`
     - Maintenance database: `salud_colombia`
     - Username: `etl_user`
     - Password: `etl_password_2026`
   - Click "Save"

---

### Paso 6: Ejecutar Notebook de Validación (Opcional)

```bash
# Levantar Jupyter Notebook
docker-compose run --rm -p 8888:8888 etl jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# Abrir en navegador: http://localhost:8888
```

---

## Conexión con Power BI (Linux)

Power BI Desktop es una aplicación de Windows, pero se puede usar en Linux mediante:

### Opción 1: Power BI Service (Recomendada para Linux)

1. Abrir Power BI Service: https://app.powerbi.com
2. Click en "Get Data" → "Database" → "PostgreSQL database"
3. Configurar conexión:
   - **Server:** `localhost:5432`
   - **Database:** `salud_colombia`
4. Ingresar credenciales:
   - Username: `etl_user`
   - Password: `etl_password_2026`
5. Seleccionar tablas a importar

### Opción 2: Power BI Desktop via Wine (Linux)

```bash
# Instalar Wine (Ubuntu/Debian)
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install wine64 wine32

# Descargar Power BI Desktop
wget https://download.microsoft.com/download/8/6/6/866C4D51-A3D0-46CF-8B1D-B3F1AD78B362/PBIDesktopSetup_x64.exe

# Instalar via Wine
wine PBIDesktopSetup_x64.exe

# Ejecutar
wine ~/.wine/drive_c/Program\ Files/Microsoft\ Power\ BI\ Desktop/bin/PBIDesktop.exe
```

### Opción 3: Conexión Directa via Puente de Red

PostgreSQL en Docker ya expone el puerto 5432 al host. Power BI puede conectarse directamente:

```
Power BI Desktop (Windows)
    ↓ localhost:5432
Docker Container (PostgreSQL)
    ↓ Puerto 5432 interno
Base de Datos salud_colombia
```

**Configuración en Power BI:**
1. Get Data → PostgreSQL
2. Server: `localhost` o `127.0.0.1`
3. Port: `5432`
4. Database: `salud_colombia`
5. Username: `etl_user`
6. Password: `etl_password_2026`

### Tablas Disponibles para Power BI

| Tabla | Descripción | Uso Recomendado |
|-------|-------------|-----------------|
| `v_resumen_afiliados` | Vista consolidada de afiliados | Análisis por departamento/municipio |
| `v_resumen_capacidad` | Vista consolidada de IPS | Análisis de capacidad instalada |
| `fact_afiliados` | Hechos de afiliados | Modelado dimensional |
| `fact_capacidad_ips` | Hechos de capacidad | Modelado dimensional |
| `dim_tiempo` | Dimensión temporal | Filtros por año/mes/trimestre |
| `dim_departamento` | Dimensión geográfica | Filtros por departamento |
| `dim_municipio` | Dimensión geográfica | Filtros por municipio |
| `dim_regimen` | Dimensión de régimen | Filtros por tipo de régimen |
| `dim_ips` | Dimensión de IPS | Análisis por institución |
| `dim_tipo_capacidad` | Dimensión de capacidad | Filtros por tipo de recurso |

---

## Comandos Útiles Docker

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (limpiar datos)
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Entrar al contenedor de PostgreSQL
docker exec -it warehouse_salud psql -U etl_user -d salud_colombia

# Backup de la base de datos
docker exec warehouse_salud pg_dump -U etl_user salud_colombia > backup.sql

# Restaurar backup
cat backup.sql | docker exec -i warehouse_salud psql -U etl_user -d salud_colombia
```

---

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

-- Afiliados por régimen y año
SELECT t.anio, r.descripcion, SUM(f.num_personas) as total
FROM fact_afiliados f
JOIN dim_tiempo t ON f.sk_tiempo = t.sk_tiempo
JOIN dim_regimen r ON f.sk_regimen = r.sk_regimen
GROUP BY t.anio, r.descripcion
ORDER BY t.anio, r.descripcion;

-- Top 10 municipios con más afiliados
SELECT m.nombre, d.nombre as departamento, SUM(f.num_personas) as total
FROM fact_afiliados f
JOIN dim_municipio m ON f.sk_municipio = m.sk_municipio
JOIN dim_departamento d ON m.sk_departamento = d.sk_departamento
GROUP BY m.nombre, d.nombre
ORDER BY total DESC
LIMIT 10;
```

---

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| PostgreSQL no inicia | Verificar que el puerto 5432 no esté en uso: `sudo lsof -i :5432` |
| Permission denied en volumes | Ejecutar: `sudo chown -R $USER:$USER ./data ./logs` |
| Contenedor ETL falla | Verificar logs: `docker-compose logs etl` |
| Power BI no conecta | Verificar que PostgreSQL esté corriendo: `docker-compose ps` |
| No hay datos en tablas | Ejecutar ETL: `docker-compose run --rm etl` |
| Jupyter no inicia | Verificar puerto: `sudo lsof -i :8888` |

---

## Datos Fuente

- **Afiliados**: SISPRO - Número de afiliados por departamento, municipio y régimen
- **IPS**: REPS - Relación de IPS públicas y privadas según nivel de atención y capacidad instalada

## Licencia

Proyecto académico - Universidad EAFIT
Curso: ETL y Análisis de Datos - 2026-2
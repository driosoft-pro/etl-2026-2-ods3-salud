# Análisis de Afiliados al Sistema de Salud en Colombia

Proyecto de análisis de datos sobre el número de afiliados por departamento, municipio y régimen de contribución en el sistema de salud colombiano.

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
│   ├── raw/                    # Datos originales sin procesar
│   │   └── Numero_afiliados.csv
│   └── processed/              # Datos procesados y transformados
├── notebooks/                  # Jupyter notebooks para análisis
├── src/                        # Código fuente de Python
│   ├── __init__.py
│   ├── extract.py              # Funciones de extracción
│   ├── transform.py            # Funciones de transformación
│   └── load.py                 # Funciones de carga
├── docs/                       # Documentación del proyecto
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                  # Archivos a ignorar por Git
└── README.md                   # Este archivo
```

## Datos

El dataset contiene información sobre afiliados al sistema de salud colombiano con las siguientes columnas:

- **CodDepto**: Código del departamento
- **Departamento**: Nombre del departamento
- **CodMunicipio**: Código del municipio
- **Municipio**: Nombre del municipio
- **IDRegimen**: Régimen de afiliación (S=Subsidiado, E=Contributivo, C=Contributivo)
- **Año**: Año de registro
- **Mes**: Mes de registro
- **NumPersonas**: Número de personas afiliadas

## Requisitos

- Python 3.8+
- pandas
- numpy
- jupyter

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/username/etl-project.git
cd etl-project

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

Los notebooks de análisis se encuentran en la carpeta `notebooks/`. Ejecutar en orden:

1. `01_exploracion_datos.ipynb` - Exploración inicial del dataset
2. `02_limpieza_transformacion.ipynb` - Limpieza y transformación
3. `03_analisis.ipynb` - Análisis estadístico
4. `04_visualizacion.ipynb` - Visualización de resultados

## Licencia

Proyecto académico - Universidad EAFIT
Curso: ETL y Análisis de Datos - 2026-2
# Data Lake + Forecasting + Dashboard (MLOps local con Docker)

Este proyecto es una arquitectura local basada en herramientas open source y Docker para construir un **Data Lake local**, realizar **modelos de forecasting** y desplegar un **dashboard interactivo**. Está orientado a escenarios comerciales como análisis SELL IN / SELL OUT y toma de decisiones predictivas.

## Arquitectura y tecnologías utilizadas

- **MinIO**: almacenamiento de datos tipo S3 (Data Lake local)
- **Apache Spark**: procesamiento de datos y modelos de ML
- **Prophet (Facebook)**: modelos de forecasting de series temporales
- **Streamlit**: visualización interactiva
- **Airflow**: orquestación de pipelines
- **Docker**: contenedores para todas las herramientas
- **Jupyter Notebooks**: desarrollo y pruebas de los pasos
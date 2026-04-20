# Predicción de Fallo Cardíaco - Proyecto MLOps End-to-End

[![CI](https://github.com/ninocvl/Mini-Proyecto-Prediccion-Fallo-Cardiaco/actions/workflows/ci.yml/badge.svg)](https://github.com/ninocvl/Mini-Proyecto-Prediccion-Fallo-Cardiaco/actions/workflows/ci.yml)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5.svg?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7.svg)](https://render.com)

## 📋 Descripción del Proyecto

Este proyecto implementa un flujo completo de **MLOps** para la predicción de riesgo de fallo cardíaco. Utilizando el dataset **Heart Failure Prediction** de Kaggle, se ha desarrollado, entrenado y desplegado un modelo de clasificación binaria (Random Forest) siguiendo las mejores prácticas de la industria.

El proyecto abarca desde el análisis exploratorio de datos (EDA) y el entrenamiento seguro con Pipelines de Scikit-learn, hasta el despliegue en producción con **FastAPI**, **Docker**, **Kubernetes**, **CI/CD con GitHub Actions** y **monitoreo de deriva de datos con Evidently**.

### 🌐 Demo en Vivo

| Componente | URL | Descripción |
|:---|:---|:---|
| **Frontend (Gradio)** | [heart-frontend-gnfl.onrender.com](https://heart-frontend-gnfl.onrender.com) | Interfaz interactiva para probar el modelo |
| **API (FastAPI)** | [heart-api-y63c.onrender.com/docs](https://heart-api-y63c.onrender.com/docs) | Documentación Swagger de la API REST |
| **API Endpoint** | [heart-api-y63c.onrender.com/predict](https://heart-api-y63c.onrender.com/predict) | Endpoint POST para predicciones |

> ⏳ **Nota sobre el plan gratuito de Render:** La primera predicción puede tardar entre 30 y 60 segundos debido al "cold start". Las siguientes son instantáneas.


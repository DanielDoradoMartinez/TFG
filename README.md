# 🎓 Predicción y explicación del éxito en proyectos de crowdfunding

**Autor:** Daniel Dorado Martínez  
**Tutorizado por:** Jacinto Mata Vázquez y Victoria Pachón Álvarez  
**Universidad de Huelva – ETSI**  
**Año:** 2025  

---

## 🧠 Descripción del proyecto

Este Trabajo Fin de Grado desarrolla un sistema automatizado para **predecir el éxito de proyectos de crowdfunding** en la plataforma [Goteo.org](https://www.goteo.org), **analizando únicamente los textos** redactados por los promotores.

El modelo se basa en **técnicas de aprendizaje profundo y modelos de lenguaje en español** (BETO y RoBERTa-base-bne), aplicando estrategias de **ensemble jerárquico**, **underbagging** y **métodos de interpretabilidad** (Integrated Gradients con Captum).

El objetivo final es identificar patrones lingüísticos que influyan en el éxito o fracaso de las campañas y aportar herramientas de apoyo para la redacción de proyectos de carácter social.

---

## 🧩 Objetivos

- Desarrollar un sistema de clasificación binaria para predecir el éxito de campañas.  
- Evaluar modelos preentrenados de lenguaje (BETO y RoBERTa-base-bne).  
- Implementar estrategias de **balanceo de clases** mediante underbagging.  
- Optimizar hiperparámetros con **Optuna**.  
- Integrar resultados con técnicas de **ensemble**.  
- Incorporar análisis de interpretabilidad mediante **Integrated Gradients**.  

---

## 📁 Estructura del repositorio

| Archivo / Carpeta | Descripción |
|--------------------|-------------|
| `Extraccion_Goteo.py` | Script para extraer los datos de proyectos desde la plataforma Goteo. |
| `Procesamiento_Dataset.ipynb` | Limpieza, normalización y preprocesamiento del dataset textual. |
| `Entrenamiento y Visualizacion Ensembles.ipynb` | Entrenamiento de modelos BETO y RoBERTa, y visualización de resultados. |
| `Interpretabilidad.ipynb` | Análisis de interpretabilidad con Integrated Gradients y Captum. |
| `goteo_proyectos_detalles.csv` | Datos originales extraídos de Goteo. |
| `trans_def.csv` | Conjunto de transformaciones aplicadas durante el procesamiento. |
| `Demo1.py`, `Demo2.py` | Ejemplos de uso o scripts de prueba. |

---

## ⚙️ Tecnologías utilizadas

- **Lenguaje:** Python 3.x  
- **Frameworks:** PyTorch, Transformers (Hugging Face)  
- **Librerías:** pandas, numpy, scikit-learn, Optuna, Captum, matplotlib  
- **Modelos:**  
  - [BETO (BERT para español)](https://huggingface.co/dccuchile/bert-base-spanish-wwm-uncased)  
  - [RoBERTa-base-bne (BSC)](https://huggingface.co/PlanTL-GOB-ES/roberta-base-bne)



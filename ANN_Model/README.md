# ANN Model for Ventilation KPI Prediction  
Maintainer: **Dinesh Kommisetti**

---

## 📌 Overview
This folder contains the machine learning pipeline for predicting ventilation quality using a lightweight Artificial Neural Network (ANN). The model is trained on four environmental features:

- Temperature  
- Humidity  
- CO₂ concentration  
- Airflow  

The labels (0, 1, 2) correspond to **Poor**, **Moderate**, and **Good** ventilation KPIs.

The final model achieves **97.6% accuracy** on a balanced dataset (1500 samples).

---

## 📊 Dataset
The dataset is stored as: ventilation_kpi_balanced.csv

Distribution:
- Class 0: 500 samples  
- Class 1: 500 samples  
- Class 2: 500 samples  

---

## 🧠 Model Architecture
Input (4 features) 
Dense(32, ReLU) 
Dense(16, ReLU) 
Dense(8, ReLU) 
Dense(3, Softmax)
Total parameters: < 10,000 → Suitable for TinyML & microcontroller inference.

---

## 📈 Training & Evaluation
Training configuration:

- Optimizer: Adam  
- Loss: SparseCategoricalCrossentropy  
- Epochs: 50  
- Validation split: 20%  

Results:

| Model | Accuracy |
|-------|----------|
| Keras | 97.6% |
| TFLite | 97.6% |

Latency: **0.0073 ms per sample** (TFLite)

---

## 🔄 TFLite Conversion
Exports:
vent_kpi_ann_float.tflite vent_kpi_scaler.pkl
vent_kpi_ann.h5

These are ready for embedded inference (ESP32 deployment in future phase).

---

## ▶ How to Run

```python
pip install tensorflow scikit-learn numpy pandas

# Load model and scaler
import tensorflow as tf
import pickle

model = tf.keras.models.load_model("vent_kpi_ann.h5")
scaler = pickle.load(open("vent_kpi_scaler.pkl", "rb"))

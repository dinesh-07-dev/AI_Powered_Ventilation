# AI-Powered Smart Ventilation Monitoring System 
### Machine Learning + Embedded Systems + Rust Mini-RTOS  
Maintained by: **Dinesh Kommisetti**

---

## 📌 Project Overview
This repository contains two core components of a smart ventilation monitoring solution:

1. **ANN Model for Ventilation KPI Prediction**  
   A lightweight neural network trained on environmental sensor data (Temperature, Humidity, CO₂, Airflow) to classify ventilation conditions into three KPI categories (Poor, Moderate, Good).  
   The model achieves **97.6% accuracy** and is optimized using **TensorFlow Lite** for embedded deployment.

2. **Mini RTOS Simulation in Rust**  
   A lightweight embedded kernel simulation implementing:
   - Task scheduling  
   - Inter-task communication (IPC)  
   - Round-robin scheduler  
   - Tick-based timing  

Together, these demonstrate an end-to-end AI + Embedded Systems engineering workflow.

---

## 📁 Repository Structure

```text
AI_Powered_Ventilation/
├── ann_model/
│   ├── README.md
│   ├── vent_kpi_scaler.pkl
│   ├── vent_kpi_ann.h5
│   ├── vent_kpi_ann_float.tflite
│   └── training_notebook.ipynb
│
├── mini_rtos_sim/
│   ├── README.md
│   └── src/
│       ├── main.rs
│       └── rtos/
│           ├── task.rs
│           ├── scheduler.rs
│           └── ipc.rs
│
└── README.md


---

## 🚀 Technologies Used

- TensorFlow / Keras  
- TensorFlow Lite  
- StandardScaler (scikit-learn)  
- Rust Programming Language  
- Embedded systems fundamentals  
- GitHub Codespaces / Colab  

---

## 📌 High-Level Workflow

1. Collect & preprocess environmental dataset  
2. Train ANN model → evaluate → export TFLite version  
3. Develop mini RTOS simulation for embedded task scheduling  
4. Prepare for ESP32 deployment (future work)

---

## 🙋 Maintainer  
**Dinesh Kommisetti**  
GitHub: [dinesh-07-dev](https://github.com/dinesh-07-dev)

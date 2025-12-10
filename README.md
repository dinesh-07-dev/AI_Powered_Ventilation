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

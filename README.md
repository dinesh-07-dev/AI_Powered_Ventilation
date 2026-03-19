# AI-Powered Smart Ventilation Monitoring System 
### Machine Learning + Embedded Systems + ESP32 AQI Monitor  
Maintained by: **Dinesh Kommisetti**

---

## 📌 Project Overview
This repository contains three integrated components of a smart ventilation monitoring solution:

1. **ANN Model for Ventilation KPI Prediction**  
   A lightweight neural network trained on environmental sensor data (Temperature, Humidity, CO₂, Airflow) to classify ventilation conditions into three KPI categories (Poor, Moderate, Good).  
   The model achieves **97.6% accuracy** and is optimized using **TensorFlow Lite** for embedded deployment.

2. **Mini RTOS Simulation in Rust**  
   A lightweight embedded kernel simulation implementing:
   - Task scheduling  
   - Inter-task communication (IPC)  
   - Round-robin scheduler  
   - Tick-based timing  

3. **ESP32 AQI Ventilation Monitor** *(new — complete hardware + software system)*  
   A budget-friendly, real-time air quality monitor using ESP32-WROOM-32 with three sensors, outputting AQI values over USB-Serial to a Python desktop GUI.

Together, these demonstrate an end-to-end AI + Embedded Systems engineering workflow.

---

## 📁 Repository Structure

```text
AI_Powered_Ventilation/
├── ANN_Model/
│   ├── README.md
│   ├── vent_kpi_scaler.pkl
│   ├── vent_kpi_ann.h5
│   ├── vent_kpi_ann_float.tflite
│   └── notebooks/
│       └── train_and_export.ipynb
│
├── Mini_RTOS_Simulation/
│   └── core_scheduler/
│       ├── Cargo.toml
│       └── src/
│           ├── main.rs
│           └── rtos/
│               ├── task.rs
│               ├── scheduler.rs
│               └── ipc.rs
│
├── esp32_firmware/                  ← NEW
│   └── aqi_monitor/
│       └── aqi_monitor.ino          ← Arduino sketch for ESP32
│
├── python_gui/                      ← NEW
│   ├── aqi_monitor_gui.py           ← Desktop GUI (tkinter + matplotlib)
│   └── requirements.txt
│
├── docs/                            ← NEW
│   ├── circuit_diagram.md           ← Wiring diagram + ASCII schematic
│   ├── pin_configuration.md         ← Full pin-by-pin reference
│   ├── assembly_instructions.md     ← Step-by-step build guide
│   └── budget_breakdown.md          ← Cost breakdown (~$25–55 total)
│
└── README.md
```

---

## 🔌 ESP32 AQI Monitor — Quick Start

### Hardware
| Sensor | Interface | ESP32 Pins |
|--------|-----------|------------|
| Plantower PMS5003 (PM2.5) | UART 9600 | GPIO16 (RX), GPIO17 (TX) |
| Winsen MH-Z19B (CO₂) | UART 9600 | GPIO32 (RX), GPIO33 (TX) |
| DHT22 (Temp/Humidity) | 1-Wire | GPIO23 + 10kΩ pull-up |

See [`docs/circuit_diagram.md`](docs/circuit_diagram.md) and [`docs/pin_configuration.md`](docs/pin_configuration.md) for full wiring details.

### Firmware
1. Open `esp32_firmware/aqi_monitor/aqi_monitor.ino` in Arduino IDE.
2. Install **DHT sensor library** by Adafruit via Library Manager.
3. Select board: **ESP32 Dev Module**, then upload.

### Python GUI
```bash
pip install pyserial matplotlib
python python_gui/aqi_monitor_gui.py          # auto-detects COM port
python python_gui/aqi_monitor_gui.py --port COM3   # or specify manually
```

The GUI shows a live colour-coded AQI gauge, sparkline charts, and logs all readings to a CSV file automatically.

### Serial Output Format (9600 baud)
```
timestamp_ms,pm1_0,pm2_5,pm10,co2_ppm,temp_c,humidity_pct,aqi,category
3000,3,8,15,621,24.5,58.0,55.2,Moderate
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [`docs/circuit_diagram.md`](docs/circuit_diagram.md) | ASCII circuit diagram + breadboard layout |
| [`docs/pin_configuration.md`](docs/pin_configuration.md) | Complete pin-by-pin wiring reference |
| [`docs/assembly_instructions.md`](docs/assembly_instructions.md) | Step-by-step build and flash guide |
| [`docs/budget_breakdown.md`](docs/budget_breakdown.md) | Cost estimates ($25–55) |

---

## 🚀 Technologies Used

- TensorFlow / Keras  
- TensorFlow Lite  
- StandardScaler (scikit-learn)  
- Rust Programming Language  
- Arduino C++ / ESP32  
- Python (tkinter, matplotlib, pyserial)  
- Embedded systems fundamentals  
- GitHub Codespaces / Colab  

---

## 📌 High-Level Workflow

1. Collect & preprocess environmental dataset  
2. Train ANN model → evaluate → export TFLite version  
3. Develop mini RTOS simulation for embedded task scheduling  
4. **Build ESP32 sensor node** → flash firmware → read sensors over Serial  
5. **Run Python GUI** → visualise AQI in real time → log to CSV  

---

## 🙋 Maintainer  
**Dinesh Kommisetti**  
GitHub: [dinesh-07-dev](https://github.com/dinesh-07-dev)

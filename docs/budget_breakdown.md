# Budget Breakdown — ESP32 AQI Ventilation Monitor

## Already Owned

| Item | Notes |
|------|-------|
| ESP32-WROOM-32 dev board | Already have |
| USB Micro-B cable | Already have |
| Computer (PC / Mac / Linux) | Already have |

---

## Components to Purchase

Prices are approximate retail (Amazon / AliExpress / local electronics store) as of early 2025. Prices vary by region.

| # | Component | Specification | Approx. Price (USD) | Where to Buy |
|---|-----------|---------------|:-------------------:|:-------------|
| 1 | Plantower PMS5003 | PM1.0/PM2.5/PM10 UART | $14–18 | Amazon, AliExpress, Adafruit |
| 2 | Winsen MH-Z19B | CO₂ 0–5000 ppm UART | $18–22 | Amazon, AliExpress |
| 3 | DHT22 (AM2302) | Temp −40–80 °C, Humidity 0–100% | $3–5 | Amazon, AliExpress, SparkFun |
| 4 | Half-size breadboard | 400 tie points | $2–4 | Amazon, AliExpress |
| 5 | Jumper wire kit | 65-piece M-M assorted | $3–5 | Amazon |
| 6 | 10 kΩ resistor | 1/4W (comes in pack of 100 usually) | $1–2 | Amazon, local shop |

### Total Estimated Cost

| Scenario | Cost |
|----------|------|
| AliExpress (cheapest, 3–4 week delivery) | **~$25–35** |
| Amazon (faster, higher price) | **~$45–55** |
| Local electronics store | **~$50–65** |

> **Note**: PMS5003 and MH-Z19B are the dominant costs. A DHT11 (~$1) can substitute for DHT22 but has lower accuracy (±2 °C vs ±0.5 °C; no sub-decimal humidity).

---

## Optional / Nice-to-Have (not required)

| Item | Use | Price |
|------|-----|-------|
| PMS5003 breakout board | Converts JST-ZH to 0.1" headers | $2–4 |
| Full-size breadboard | More room for future sensors | $4–6 |
| 3.3V to 5V level shifter | Protects ESP32 if sensor TX exceeds 3.3V (not needed for these sensors) | $1–3 |
| Enclosure/project box | Tidy installation | $3–8 |

---

## Free Software

| Software | Cost | Link |
|----------|------|------|
| Arduino IDE 2.x | Free | https://arduino.cc |
| ESP32 board support (Espressif) | Free | via Arduino Boards Manager |
| Python 3.x | Free | https://python.org |
| pyserial | Free (pip) | `pip install pyserial` |
| matplotlib | Free (pip) | `pip install matplotlib` |

---

## Summary

| Category | Cost |
|----------|------|
| Hardware (new purchases) | **$25–55** |
| Software | **$0** |
| **Total** | **$25–55** |

This is one of the most cost-effective AQI monitoring setups available — commercial AQI monitors with equivalent sensors typically cost $150–500.

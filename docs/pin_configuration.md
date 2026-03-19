# Pin Configuration Guide — ESP32 AQI Monitor

## ESP32-WROOM-32 Pinout Reference

```
                ┌─────────────────────────────┐
           3V3 ─┤ 3.3 V          5V / Vin ├─ 5V
           GND ─┤ GND                GND  ├─ GND
           IO15 ─┤ GPIO15           GPIO13 ├─ IO13
            IO2 ─┤ GPIO2            GPIO12 ├─ IO12
            IO4 ─┤ GPIO4            GPIO14 ├─ IO14
            IO5 ─┤ GPIO5            GPIO27 ├─ IO27
           IO18 ─┤ GPIO18           GPIO26 ├─ IO26
           IO19 ─┤ GPIO19           GPIO25 ├─ IO25
           IO21 ─┤ GPIO21  ESP32   GPIO33 ├─◄IO33  ← CO2 TX2ESP
            RX0 ─┤ GPIO3           GPIO32 ├─◄IO32  ← CO2 RX2ESP
            TX0 ─┤ GPIO1           GPIO35 ├─ IO35  (input only)
           IO22 ─┤ GPIO22          GPIO34 ├─ IO34  (input only)
           IO23 ─┤ GPIO23 ◄──DHT22  GPIO39 ├─ IO39  (input only)
                 └─────────────────────────────┘

                ┌─────────────────────────────┐
           IO16 ─┤ GPIO16 ◄──PMS5003 TX        │  (RX2)
           IO17 ─┤ GPIO17 ──►PMS5003 RX        │  (TX2)
                 └─────────────────────────────┘
           (Shown on bottom row of dev board)
```

---

## Complete Pin Assignment Table

### PMS5003 — Particulate Matter Sensor (PM1.0 / PM2.5 / PM10)

| PMS5003 Pin | PMS5003 Label | ESP32 Pin | ESP32 Label | Wire Colour (suggested) |
|:-----------:|:--------------|:---------:|:------------|:------------------------|
| 1 | VCC | 5V / Vin | 5 V power | **Red** |
| 2 | GND | GND | Ground | **Black** |
| 3 | SET | 3.3 V | Always HIGH = continuous mode | Orange |
| 4 | RX | GPIO17 | TX2 (UART2) | Yellow |
| 5 | TX | GPIO16 | RX2 (UART2) | Green |
| 6 | RESET | — | Leave unconnected | — |

> ℹ️  The PMS5003 uses a JST-ZH 1.5 mm 8-pin connector. If using a breakout board, the pins above are labelled on it.

---

### MH-Z19B — CO₂ Sensor

| MH-Z19B Pin | MH-Z19B Label | ESP32 Pin | ESP32 Label | Wire Colour (suggested) |
|:-----------:|:--------------|:---------:|:------------|:------------------------|
| 1 | Vin | 5V / Vin | 5 V power | **Red** |
| 2 | GND | GND | Ground | **Black** |
| 3 | TX | GPIO32 | RX1 (UART1 remapped) | Green |
| 4 | RX | GPIO33 | TX1 (UART1 remapped) | Yellow |
| 5 | PWM | — | Leave unconnected | — |
| 6 | AOT | — | Leave unconnected | — |

> ℹ️  The MH-Z19B has a 6-pin header on one end. Only 4 pins (Vin, GND, TX, RX) are used here.

---

### DHT22 — Temperature & Humidity Sensor

| DHT22 Pin | DHT22 Label | ESP32 Pin | ESP32 Label | Note |
|:---------:|:------------|:---------:|:------------|:-----|
| 1 | VCC | 3.3 V | 3.3 V rail | **Red** |
| 2 | DATA | GPIO23 | GPIO23 | + 10 kΩ pull-up to 3.3 V |
| 3 | NC | — | — | Leave unconnected |
| 4 | GND | GND | Ground | **Black** |

> ⚠️  **Critical**: Place a 10 kΩ resistor between DHT22 DATA (pin 2) and the 3.3 V rail. Without it the sensor will give intermittent or no readings.

---

## Power Budget

| Component | Voltage | Typical Current | Peak Current |
|-----------|---------|----------------|-------------|
| ESP32-WROOM-32 | 3.3 V | 80 mA | 240 mA (WiFi TX) |
| PMS5003 | 5 V | 100 mA | 150 mA (fan startup) |
| MH-Z19B | 5 V | 20 mA | 150 mA (heating) |
| DHT22 | 3.3 V | 1.5 mA | 2.5 mA |
| **Total** | **USB 5V** | **~200 mA** | **~540 mA** |

A standard USB 2.0 port provides up to 500 mA and USB 3.0 provides up to 900 mA — either is sufficient.

---

## Quick-Reference Wiring Summary

```
ESP32 Vin  (5V)  ──►  PMS5003 VCC  +  MH-Z19B Vin
ESP32 3.3V       ──►  DHT22 VCC  +  PMS5003 SET  +  10kΩ resistor top
ESP32 GND        ──►  All GNDs (PMS5003, MH-Z19B, DHT22)

ESP32 GPIO16     ◄──  PMS5003 TX   (UART2 RX)
ESP32 GPIO17     ──►  PMS5003 RX   (UART2 TX)
ESP32 GPIO32     ◄──  MH-Z19B TX   (UART1 RX remapped)
ESP32 GPIO33     ──►  MH-Z19B RX   (UART1 TX remapped)
ESP32 GPIO23     ◄──  DHT22 DATA   (+ 10kΩ to 3.3V)
```

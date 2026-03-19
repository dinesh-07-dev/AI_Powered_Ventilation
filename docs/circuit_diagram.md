# Circuit Diagram — ESP32 AQI Ventilation Monitor

## Component Overview

| # | Component | Interface | ESP32 Pins |
|---|-----------|-----------|------------|
| 1 | ESP32-WROOM-32 | — | — |
| 2 | PMS5003 (PM2.5) | UART (9600) | GPIO16 (RX), GPIO17 (TX) |
| 3 | MH-Z19B (CO₂) | UART (9600) | GPIO32 (RX), GPIO33 (TX) |
| 4 | DHT22 (Temp/Hum) | 1-Wire | GPIO23 |
| 5 | 10 kΩ resistor | pull-up | DHT22 DATA ↔ 3.3 V |
| 6 | USB-A to Micro-USB | Power + Serial | USB (5 V) |

---

## ASCII Circuit Diagram

```
                           ┌─────────────────────────────────┐
                           │        ESP32-WROOM-32            │
                           │                                  │
      PMS5003              │  GPIO16 (RX2) ←─────── TX       │
   ┌──────────┐            │  GPIO17 (TX2) ──────→  RX       │◄── 5 V (Vin)
   │ VCC  ────┼────── 5V   │                                  │◄── GND
   │ GND  ────┼────── GND  │                                  │
   │ TX   ────┼──────────→ │  GPIO16                          │
   │ RX   ────┼──────────← │  GPIO17                          │
   │ SET  ────┼────── 3.3V │  (leave SET HIGH for continuous) │
   │ RESET────┼────── NC   │                                  │
   └──────────┘            │  GPIO32 (RX1) ←─────── TX       │
                           │  GPIO33 (TX1) ──────→  RX       │
      MH-Z19B              │                                  │
   ┌──────────┐            │                                  │
   │ Vin  ────┼────── 5V   │                                  │
   │ GND  ────┼────── GND  │                                  │
   │ TX   ────┼──────────→ │  GPIO32                          │
   │ RX   ────┼──────────← │  GPIO33                          │
   └──────────┘            │                                  │
                           │  GPIO23 ←── DATA (+ 10kΩ → 3.3V)│
      DHT22                │  3.3V  ──────────────────────┐   │
   ┌──────────┐            │  GND   ──────────────────┐   │   │
   │ VCC  ────┼────── 3.3V │                           │   │   │
   │ DATA ────┼──────────→ │  GPIO23                   │   │   │
   │ NC   ────┼────── NC   │                          ─┼───┼─  │
   │ GND  ────┼────── GND  │                       10kΩ│   │   │
   └──────────┘            │                          ─┴───┘   │
                           │                                  │
     USB Cable             │  USB (micro)                     │
   ┌──────────┐            │  ├── 5 V power                   │
   │  PC/Mac  ├────────────┼──┤                               │
   │          │            │  └── Serial data (9600 baud)     │
   └──────────┘            └─────────────────────────────────┘

                      [10kΩ pull-up: DHT22 DATA pin to 3.3V rail]
```

---

## Breadboard Wiring Diagram (Top View)

```
Power Rails on breadboard:
  Red  rail  (+) → 3.3V from ESP32 "3V3" pin
  Blue rail  (+) → 5V  from ESP32 "5V" / "Vin" pin
  Black rail (−) → GND from ESP32 "GND" pin

Component placements (column letters are breadboard columns):

  ESP32-WROOM-32     : straddle centre gap, pins A1–A19 (left), B1–B19 (right)
  PMS5003 breakout   : rows 25–30, left side
  MH-Z19B            : rows 32–38, left side
  DHT22              : rows 40–43, left side
  10kΩ resistor      : row 41 (between DHT DATA column and 3.3V rail)
```

---

## Schematic Notes

1. **PMS5003 power**: Must be 5 V; its TX output is 3.3 V compatible — safe to connect to ESP32 GPIO directly.
2. **MH-Z19B power**: Requires 5 V on Vin; TX output is 3.3 V compatible.
3. **DHT22 pull-up**: A 10 kΩ resistor between the DATA pin and 3.3 V is mandatory for reliable communication.
4. **ESP32 UART remapping**: `Serial1` is remapped in code to GPIO32/33; `Serial2` uses its hardware default GPIO16/17.
5. **USB power**: The ESP32 dev board's 5 V (Vin) pin supplies 5 V when powered by USB — use that rail for PMS5003 and MH-Z19B.
6. **No external power supply needed** — the USB cable powers everything.

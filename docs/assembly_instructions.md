# Step-by-Step Assembly Instructions

## Tools & Materials Needed

- ESP32-WROOM-32 development board
- Plantower PMS5003 sensor (with cable or breakout)
- Winsen MH-Z19B CO₂ sensor
- DHT22 temperature/humidity sensor
- Half-size (or full-size) breadboard
- Jumper wires (male-to-male, at least 15)
- 1× 10 kΩ resistor
- USB Micro-B cable (data-capable, not charge-only)
- Computer with Arduino IDE

---

## Step 1 — Install Software

### 1.1 Arduino IDE
1. Download **Arduino IDE 2.x** from https://arduino.cc/en/software
2. Open Arduino IDE → **File → Preferences**
3. Add to *Additional boards manager URLs*:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Open **Tools → Board → Boards Manager**, search `esp32`, install **esp32 by Espressif Systems** (v2.x).

### 1.2 Libraries
Open **Tools → Manage Libraries** and install:
- **DHT sensor library** by Adafruit *(installs Adafruit Unified Sensor automatically)*

No other libraries are needed — PMS5003 and MH-Z19B are read with `HardwareSerial`.

### 1.3 Python (for the desktop GUI)
```bash
pip install pyserial matplotlib
```

---

## Step 2 — Identify Your Components

### PMS5003
- White rectangular sensor, ~38 × 35 × 12 mm
- Has a small fan — you can hear it spin
- Connector: JST-ZH 1.5 mm, 7-pin (use included cable or breakout adapter)
- Labelled pins: VCC, GND, SET, RX, TX, RESET, (NC)

### MH-Z19B
- Green PCB, ~33 × 55 mm
- Sensor window on one end; 6-pin header on the other
- Labelled: Vin, GND, TX, RX, PWM, AOT

### DHT22 (AM2302)
- Small white rectangular sensor, 4 pins (1 unused)
- Pins left-to-right: VCC, DATA, NC, GND

---

## Step 3 — Place Components on Breadboard

```
 Breadboard layout (rough placement):
 ─────────────────────────────────────────────────────────────
  Row  1–19 : ESP32 dev board (straddles centre gap)
  Row 22–27 : PMS5003 breakout board or wire ends
  Row 29–34 : MH-Z19B (header end facing outward)
  Row 36–39 : DHT22
  Row 41    : 10 kΩ resistor (one end col 'd', other end '+' rail)
 ─────────────────────────────────────────────────────────────
```

1. Seat the **ESP32** across the centre gap of the breadboard.
   - Its USB port should face one end of the breadboard for easy access.
2. Place the **DHT22** with pin 1 (VCC) at row 36.
3. Place the **MH-Z19B** header at rows 29–34.
4. Connect the **PMS5003** via its cable — strip or terminate at rows 22–27, or use a breakout adapter.

---

## Step 4 — Power Rails

Set up the breadboard power rails before connecting sensors:

| Rail | Voltage | Source |
|------|---------|--------|
| Red (+) rail, left section | **3.3 V** | ESP32 pin `3V3` |
| Blue (+) rail, right section | **5 V** | ESP32 pin `5V` / `Vin` |
| Black (−) rail, both sides | **GND** | ESP32 pin `GND` |

Wire instructions:
1. **ESP32 `3V3`** → red (+) rail (use a jumper wire)
2. **ESP32 `5V`** (labeled `Vin` on some boards) → blue (+) rail
3. **ESP32 `GND`** → black (−) rail
4. Bridge the two GND rails with a short jumper wire

---

## Step 5 — Connect DHT22

| DHT22 | Connect to |
|-------|-----------|
| Pin 1 (VCC) | Red 3.3 V rail |
| Pin 2 (DATA) | ESP32 GPIO23 |
| Pin 3 (NC) | Leave unconnected |
| Pin 4 (GND) | Black GND rail |

**Pull-up resistor (mandatory):**
- Insert a **10 kΩ resistor** from DHT22 DATA (same row) to the 3.3 V rail.

✅ Test: The DHT22 LED (if present) should glow faintly when powered.

---

## Step 6 — Connect MH-Z19B

| MH-Z19B | Connect to |
|---------|-----------|
| Vin | Blue 5 V rail |
| GND | Black GND rail |
| TX | ESP32 GPIO32 |
| RX | ESP32 GPIO33 |
| PWM | Leave unconnected |
| AOT | Leave unconnected |

✅ The sensor warms up in ~3 minutes; readings stabilise after 1–3 minutes of operation.

---

## Step 7 — Connect PMS5003

The PMS5003 cable colours may vary by manufacturer — check labels on the sensor/breakout:

| PMS5003 Label | Connect to |
|--------------|-----------|
| VCC | Blue 5 V rail |
| GND | Black GND rail |
| SET | Red 3.3 V rail (pin HIGH = continuous mode) |
| TX | ESP32 GPIO16 |
| RX | ESP32 GPIO17 |
| RESET | Leave unconnected |

✅ The fan inside should spin immediately when 5 V is applied.

---

## Step 8 — Double-Check All Connections

Before connecting USB, verify:

- [ ] ESP32 `3V3` → 3.3 V rail
- [ ] ESP32 `5V` → 5 V rail
- [ ] ESP32 `GND` → GND rail (both rails bridged)
- [ ] DHT22: VCC→3.3V, DATA→GPIO23, GND→GND, 10kΩ pull-up fitted
- [ ] MH-Z19B: Vin→5V, GND→GND, TX→GPIO32, RX→GPIO33
- [ ] PMS5003: VCC→5V, GND→GND, SET→3.3V, TX→GPIO16, RX→GPIO17
- [ ] No bare wire ends touching metal

---

## Step 9 — Flash the Firmware

1. Connect ESP32 to your computer via USB Micro-B cable.
2. Open Arduino IDE.
3. Open `esp32_firmware/aqi_monitor/aqi_monitor.ino`.
4. Set board: **Tools → Board → esp32 → ESP32 Dev Module**.
5. Set upload speed: **Tools → Upload Speed → 921600**.
6. Select port: **Tools → Port → COMx** (Windows) or `/dev/ttyUSBx` (Linux/macOS).
7. Click **Upload** (▶).

> If upload fails with "Connecting…" message: hold the BOOT button on the ESP32 while clicking Upload, release after "Connecting…" appears.

---

## Step 10 — Verify Serial Output

1. Open **Tools → Serial Monitor** in Arduino IDE.
2. Set baud rate to **9600**.
3. You should see:
   ```
   timestamp_ms,pm1_0,pm2_5,pm10,co2_ppm,temp_c,humidity_pct,aqi,category
   3000,3,8,15,621,24.5,58.0,55.2,Moderate
   8000,2,7,14,615,24.5,58.1,51.0,Moderate
   ```
4. Sensor values should update every 5 seconds.

---

## Step 11 — Launch the Python GUI

```bash
# Install dependencies once
pip install pyserial matplotlib

# Run the GUI (auto-detects COM port)
cd python_gui
python aqi_monitor_gui.py

# Or specify your port explicitly
python aqi_monitor_gui.py --port COM3          # Windows
python aqi_monitor_gui.py --port /dev/ttyUSB0  # Linux
python aqi_monitor_gui.py --port /dev/cu.usbserial-0001  # macOS
```

The GUI window opens and shows:
- A colour-coded **AQI gauge** (green → red → purple)
- Live **sparkline charts** for PM2.5, CO₂, Temperature, Humidity
- Scrolling **data table**
- Automatic **CSV log** saved to `aqi_log_YYYYMMDD.csv` in the current folder

---

## Troubleshooting

| Symptom | Possible Cause | Fix |
|---------|---------------|-----|
| Serial Monitor shows nothing | Wrong baud rate | Set to 9600 in Serial Monitor |
| `0,0,0` for PM readings | PMS5003 not connected | Check GPIO16/17 wiring |
| CO₂ always 400 | MH-Z19B not responding | Check GPIO32/33, verify 5V on Vin |
| DHT reads NaN / 0 | Missing pull-up resistor | Add 10 kΩ between DATA and 3.3V |
| GUI shows "Serial Error" | Wrong port / ESP32 not connected | Check USB cable and port in Device Manager / `ls /dev/tty*` |
| Upload fails | Board not in bootloader mode | Hold BOOT button during upload |
| GUI port not found | No USB-serial driver | Install CP210x or CH340 driver |

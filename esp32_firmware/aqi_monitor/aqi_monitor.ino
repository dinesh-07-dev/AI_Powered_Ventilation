/*
 * AQI Ventilation Monitor — ESP32-WROOM-32
 * =========================================
 * Sensors:
 *   PMS5003  (PM2.5)     → Serial2 : GPIO16 (RX2) / GPIO17 (TX2)
 *   MH-Z19B  (CO2)       → Serial1 : GPIO32 (RX1) / GPIO33 (TX1)
 *   DHT22    (Temp/Hum)  → GPIO23
 *
 * Output: CSV lines over USB-Serial at 9600 baud
 * Format: timestamp_ms,pm1_0,pm2_5,pm10,co2_ppm,temp_c,humidity_pct,aqi,category
 *
 * Board: "ESP32 Dev Module" in Arduino IDE
 * Required libraries:
 *   - DHT sensor library by Adafruit  (Tools → Manage Libraries)
 *   - Adafruit Unified Sensor          (dependency of DHT library)
 */

#include <DHT.h>

// ──────────────────────────────────────────────
// Pin definitions
// ──────────────────────────────────────────────
#define DHT_PIN        23
#define DHT_TYPE       DHT22

// PMS5003 uses Serial2 (default pins on ESP32: RX2=16, TX2=17)
#define PMS_RX_PIN     16
#define PMS_TX_PIN     17
#define PMS_BAUD       9600

// MH-Z19B uses Serial1 remapped to GPIO32/33
#define CO2_RX_PIN     32
#define CO2_TX_PIN     33
#define CO2_BAUD       9600

// ──────────────────────────────────────────────
// Sensor objects
// ──────────────────────────────────────────────
DHT dht(DHT_PIN, DHT_TYPE);

HardwareSerial pmsSerial(2);   // UART2 for PMS5003
HardwareSerial co2Serial(1);   // UART1 for MH-Z19B

// ──────────────────────────────────────────────
// Reading interval (milliseconds)
// ──────────────────────────────────────────────
#define READ_INTERVAL_MS  5000UL

// ──────────────────────────────────────────────
// Data structures
// ──────────────────────────────────────────────
struct PMSData {
  uint16_t pm1_0;
  uint16_t pm2_5;
  uint16_t pm10;
  bool     valid;
};

struct SensorReading {
  unsigned long timestamp_ms;
  uint16_t pm1_0;
  uint16_t pm2_5;
  uint16_t pm10;
  uint16_t co2_ppm;
  float    temperature;
  float    humidity;
  float    aqi;
  char     category[20];
};

// ──────────────────────────────────────────────
// PMS5003 parser
// The PMS5003 sends 32-byte frames at 9600 baud.
// Frame structure (bytes):
//   0x42 0x4D (start), 2B length, 12× uint16 data, 2B checksum
// ──────────────────────────────────────────────
PMSData readPMS5003() {
  PMSData result = {0, 0, 0, false};

  // Flush stale data; use a short 200 ms pause (non-blocking loop) so the
  // sensor can push at least one fresh packet before we start parsing.
  while (pmsSerial.available()) pmsSerial.read();
  unsigned long flushEnd = millis() + 200;
  while (millis() < flushEnd) yield();  // yield to RTOS / watchdog

  uint8_t buf[32];
  unsigned long t0 = millis();

  // Wait for start bytes 0x42 0x4D
  while (millis() - t0 < 2000) {
    if (pmsSerial.available() >= 2) {
      if (pmsSerial.peek() == 0x42) {
        pmsSerial.read();  // consume 0x42
        if (pmsSerial.peek() == 0x4D) {
          buf[0] = 0x42;
          buf[1] = pmsSerial.read();  // 0x4D
          break;
        }
      } else {
        pmsSerial.read();  // discard byte
      }
    }
  }

  // Read remaining 30 bytes
  unsigned long t1 = millis();
  uint8_t received = 2;
  while (received < 32 && (millis() - t1 < 1000)) {
    if (pmsSerial.available()) {
      buf[received++] = pmsSerial.read();
    }
  }

  if (received < 32) return result;  // incomplete frame

  // Verify checksum (sum of bytes 0..29 == bytes 30..31 as uint16 big-endian)
  uint16_t checksum = 0;
  for (int i = 0; i < 30; i++) checksum += buf[i];
  uint16_t frame_check = ((uint16_t)buf[30] << 8) | buf[31];
  if (checksum != frame_check) return result;

  // Parse atmospheric concentrations (bytes 10–15 = CF=1, bytes 4–9 = standard)
  // Using "atmospheric" values: PM1.0@buf[10,11], PM2.5@buf[12,13], PM10@buf[14,15]
  result.pm1_0  = ((uint16_t)buf[10] << 8) | buf[11];
  result.pm2_5  = ((uint16_t)buf[12] << 8) | buf[13];
  result.pm10   = ((uint16_t)buf[14] << 8) | buf[15];
  result.valid  = true;
  return result;
}

// ──────────────────────────────────────────────
// MH-Z19B CO2 reader (UART command protocol)
// Send 9-byte command, receive 9-byte response
// ──────────────────────────────────────────────
uint16_t readMHZ19B() {
  uint8_t cmd[9] = {0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
  uint8_t response[9];

  while (co2Serial.available()) co2Serial.read();  // flush

  co2Serial.write(cmd, 9);
  delay(100);  // sensor response time

  if (co2Serial.available() < 9) return 0;  // no response

  for (int i = 0; i < 9; i++) response[i] = co2Serial.read();

  // Validate: response[0] == 0xFF, response[1] == 0x86
  if (response[0] != 0xFF || response[1] != 0x86) return 0;

  // Verify checksum: sum of bytes 1..7, negate, +1 (mod 256) == byte 8
  uint8_t crc = 0;
  for (int i = 1; i < 8; i++) crc += response[i];
  crc = (~crc) + 1;
  if (crc != response[8]) return 0;

  return ((uint16_t)response[2] << 8) | response[3];
}

// ──────────────────────────────────────────────
// AQI calculation (US EPA breakpoints for PM2.5)
// Returns AQI value (0–500+)
// ──────────────────────────────────────────────
float calculatePM25AQI(float concentration) {
  // US EPA PM2.5 AQI linear interpolation breakpoints
  // c_lo / c_hi : PM2.5 concentration range in µg/m³ (24-hour average approximation)
  // i_lo / i_hi : corresponding AQI index range for each band
  // Bands: Good | Moderate | Unhealthy for Sensitive | Unhealthy | Very Unhealthy | Hazardous (lo) | Hazardous (hi)
  const float c_lo[] = {  0.0, 12.1, 35.5,  55.5, 150.5, 250.5, 350.5};
  const float c_hi[] = { 12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4};
  const float i_lo[] = {    0,   51,  101,   151,   201,   301,   401};
  const float i_hi[] = {   50,  100,  150,   200,   300,   400,   500};
  const int   n = 7;

  if (concentration < 0)     concentration = 0;
  if (concentration > 500.4) return 500.0;

  for (int i = 0; i < n; i++) {
    if (concentration >= c_lo[i] && concentration <= c_hi[i]) {
      return ((i_hi[i] - i_lo[i]) / (c_hi[i] - c_lo[i]))
             * (concentration - c_lo[i]) + i_lo[i];
    }
  }
  return 500.0;
}

float calculateCO2AQI(uint16_t co2_ppm) {
  // Simplified CO2 contribution to indoor AQI
  if (co2_ppm <= 600)   return 0.0;
  if (co2_ppm <= 1000)  return ((float)(co2_ppm - 600) / 400.0f) * 50.0f;
  if (co2_ppm <= 1500)  return 50.0f + ((float)(co2_ppm - 1000) / 500.0f) * 50.0f;
  if (co2_ppm <= 2000)  return 100.0f + ((float)(co2_ppm - 1500) / 500.0f) * 100.0f;
  return 200.0f;
}

float calculateAQI(uint16_t pm2_5, uint16_t co2_ppm) {
  float pm_aqi  = calculatePM25AQI((float)pm2_5);
  float co2_aqi = calculateCO2AQI(co2_ppm);
  // Dominant pollutant determines overall AQI
  return max(pm_aqi, co2_aqi);
}

void aqiCategory(float aqi, char* buf) {
  if      (aqi <= 50)  strcpy(buf, "Good");
  else if (aqi <= 100) strcpy(buf, "Moderate");
  else if (aqi <= 150) strcpy(buf, "Unhealthy_Sensitive");
  else if (aqi <= 200) strcpy(buf, "Unhealthy");
  else if (aqi <= 300) strcpy(buf, "Very_Unhealthy");
  else                 strcpy(buf, "Hazardous");
}

// ──────────────────────────────────────────────
// Setup
// ──────────────────────────────────────────────
void setup() {
  Serial.begin(9600);   // USB-Serial to PC
  delay(500);

  // PMS5003 on Serial2
  pmsSerial.begin(PMS_BAUD, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);

  // MH-Z19B on Serial1
  co2Serial.begin(CO2_BAUD, SERIAL_8N1, CO2_RX_PIN, CO2_TX_PIN);

  // DHT22
  dht.begin();

  delay(3000);  // Allow sensors to stabilise after power-on

  // Print CSV header
  Serial.println(F("timestamp_ms,pm1_0,pm2_5,pm10,co2_ppm,temp_c,humidity_pct,aqi,category"));
}

// ──────────────────────────────────────────────
// Main loop
// ──────────────────────────────────────────────
void loop() {
  static unsigned long lastRead = 0;

  if (millis() - lastRead < READ_INTERVAL_MS) return;
  lastRead = millis();

  SensorReading r;
  r.timestamp_ms = millis();

  // ── Read PMS5003 ──
  PMSData pms = readPMS5003();
  if (pms.valid) {
    r.pm1_0 = pms.pm1_0;
    r.pm2_5 = pms.pm2_5;
    r.pm10  = pms.pm10;
  } else {
    // Use last valid or fallback
    r.pm1_0 = r.pm2_5 = r.pm10 = 0;
  }

  // ── Read MH-Z19B ──
  r.co2_ppm = readMHZ19B();
  if (r.co2_ppm == 0) r.co2_ppm = 400;  // fallback to ambient CO2

  // ── Read DHT22 ──
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  r.humidity    = isnan(h) ? 0.0f : h;
  r.temperature = isnan(t) ? 0.0f : t;

  // ── Calculate AQI ──
  r.aqi = calculateAQI(r.pm2_5, r.co2_ppm);
  aqiCategory(r.aqi, r.category);

  // ── Emit CSV line ──
  Serial.print(r.timestamp_ms);   Serial.print(',');
  Serial.print(r.pm1_0);          Serial.print(',');
  Serial.print(r.pm2_5);          Serial.print(',');
  Serial.print(r.pm10);           Serial.print(',');
  Serial.print(r.co2_ppm);        Serial.print(',');
  Serial.print(r.temperature, 1); Serial.print(',');
  Serial.print(r.humidity, 1);    Serial.print(',');
  Serial.print(r.aqi, 1);         Serial.print(',');
  Serial.println(r.category);
}

/*
 * ESP32 "ocean buoy" sensor node
 * --------------------------------
 * Real-hardware replacement for sensor_node.py. Sends the same compact JSON
 * telemetry over Wi-Fi/UDP to the edge gateway, so nothing downstream changes:
 *
 *   {"node":"BUOY_HW_01","seq":42,"time":"","t_sent":0,"wind":18.5,"temp":29.1,
 *    "pressure":1006.3,"kind":"sensor","reconstructed":false}
 *
 * Hardware (see hardware/README.md for wiring and prices):
 *   - ESP32 DevKit V1
 *   - BMP280 (or BME280) temperature + pressure sensor on I2C (SDA=21, SCL=22)
 *   - Wind: EITHER a 10k potentiometer on GPIO34 ("wind knob" for demos)
 *           OR a hall-effect cup anemometer (A3144 + magnet) on GPIO27
 *   - Alert LED on GPIO2 (on-board LED) and an active buzzer on GPIO25
 *   - BOOT button (GPIO0, already on the board) toggles "storm mode", which
 *     ramps the pressure down and the wind up so you can demo a cyclone
 *     indoors.
 *
 * Features mirroring the software prototype:
 *   - sequence numbers (the server detects gaps and reconstructs them)
 *   - optional artificial packet loss (LOSS_PERCENT) on top of real Wi-Fi loss
 *   - a NON_ESSENTIAL housekeeping packet (battery, RSSI) every 5 readings
 *   - listens on UDP 9004 for the gateway's alert message and switches the
 *     LED/buzzer on during a cyclone alert (closes the QoS feedback loop).
 *
 * Libraries (Arduino Library Manager): "Adafruit BMP280 Library"
 * Board: "ESP32 Dev Module" (esp32 by Espressif Systems)
 */
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

// ------------------------------------------------------------- configure me
const char *WIFI_SSID     = "YOUR_WIFI_OR_HOTSPOT";
const char *WIFI_PASSWORD = "YOUR_PASSWORD";
const char *GATEWAY_IP    = "192.168.1.50";   // laptop / Raspberry Pi running edge_gateway.py
const uint16_t GATEWAY_PORT = 9001;           // SENSOR_TO_GATEWAY_PORT
const uint16_t ALERT_PORT   = 9004;           // NODE_ALERT_PORT
const char *NODE_ID       = "BUOY_HW_01";     // unique per board

const float ALTITUDE_M      = 216.0;  // your altitude: converts station pressure to sea-level pressure
const uint32_t INTERVAL_MS  = 1000;   // one reading per second
const int LOSS_PERCENT      = 0;      // extra simulated packet loss (0-100) for demos
const int HOUSEKEEPING_EVERY = 5;

#define WIND_POT 1                    // 1 = potentiometer on GPIO34, 0 = hall anemometer on GPIO27
const int PIN_WIND_POT  = 34;
const int PIN_ANEMO     = 27;
const float KMH_PER_HZ  = 2.4;        // anemometer calibration (2.4 km/h per pulse/s is typical)
const int PIN_LED       = 2;
const int PIN_BUZZER    = 25;
const int PIN_BOOT      = 0;
const int PIN_BATTERY   = 35;         // optional: battery via 100k/100k divider (reads 0 if unused)
// --------------------------------------------------------------------------

Adafruit_BMP280 bmp;
WiFiUDP udp;       // telemetry out
WiFiUDP alertUdp;  // alerts in
bool bmpOk = false;
uint32_t seq = 0, hkSeq = 0;
bool stormMode = false;
float stormLevel = 0.0;     // 0..1 ramps while storm mode is on
bool alertActive = false;
volatile uint32_t anemoPulses = 0;

void IRAM_ATTR onAnemoPulse() { anemoPulses++; }

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("Connecting to %s", WIFI_SSID);
  for (int i = 0; i < 60 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
  }
  Serial.printf("\nWi-Fi %s, IP %s\n", WiFi.status() == WL_CONNECTED ? "connected" : "FAILED",
                WiFi.localIP().toString().c_str());
}

float readWindKmh(float dtSeconds) {
#if WIND_POT
  (void)dtSeconds;
  return analogRead(PIN_WIND_POT) / 4095.0 * 120.0;  // knob: 0-120 km/h
#else
  noInterrupts();
  uint32_t pulses = anemoPulses;
  anemoPulses = 0;
  interrupts();
  return pulses / dtSeconds * KMH_PER_HZ;
#endif
}

void sendJson(const char *json) {
  udp.beginPacket(GATEWAY_IP, GATEWAY_PORT);
  udp.write((const uint8_t *)json, strlen(json));
  udp.endPacket();
}

void checkAlerts() {
  int len = alertUdp.parsePacket();
  if (len <= 0) return;
  char buf[128];
  len = alertUdp.read(buf, sizeof(buf) - 1);
  buf[len > 0 ? len : 0] = '\0';
  // Gateway sends {"type":"alert","alert":true,"risk":87.5}
  alertActive = strstr(buf, "\"alert\":true") != nullptr;
  Serial.printf("Gateway alert message: %s -> alert %s\n", buf, alertActive ? "ON" : "off");
}

void driveAlertOutputs() {
  bool blink = (millis() / 250) % 2;
  digitalWrite(PIN_LED, alertActive ? blink : LOW);
  digitalWrite(PIN_BUZZER, alertActive && blink && (millis() / 2000) % 2 ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_BOOT, INPUT_PULLUP);
#if !WIND_POT
  pinMode(PIN_ANEMO, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ANEMO), onAnemoPulse, FALLING);
#endif
  Wire.begin(21, 22);
  bmpOk = bmp.begin(0x76) || bmp.begin(0x77);
  Serial.println(bmpOk ? "BMP280 found" : "BMP280 NOT found - check wiring (sending simulated temp/pressure)");
  connectWiFi();
  alertUdp.begin(ALERT_PORT);
  randomSeed(esp_random());
}

void loop() {
  static uint32_t lastSend = 0, lastButton = 0;
  static bool lastBtn = HIGH;

  checkAlerts();
  driveAlertOutputs();

  bool btn = digitalRead(PIN_BOOT);
  if (btn == LOW && lastBtn == HIGH && millis() - lastButton > 300) {
    stormMode = !stormMode;
    lastButton = millis();
    Serial.printf("Storm mode %s\n", stormMode ? "ON" : "off");
  }
  lastBtn = btn;

  if (millis() - lastSend < INTERVAL_MS) return;
  float dt = (millis() - lastSend) / 1000.0;
  lastSend = millis();
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  stormLevel = stormMode ? min(1.0f, stormLevel + 0.03f) : max(0.0f, stormLevel - 0.05f);

  float temp = bmpOk ? bmp.readTemperature() : 28.0 + random(-10, 10) / 100.0;
  float station = bmpOk ? bmp.readPressure() / 100.0 : 1008.0;
  float seaLevel = station / pow(1.0 - ALTITUDE_M / 44330.0, 5.255);
  float wind = readWindKmh(dt);

  // Storm mode: emulate an approaching cyclone on top of the real readings.
  seaLevel -= 35.0 * stormLevel;
  wind += 70.0 * stormLevel;
  temp -= 2.0 * stormLevel;

  seq++;
  char json[256];
  snprintf(json, sizeof(json),
           "{\"node\":\"%s\",\"seq\":%lu,\"time\":\"\",\"t_sent\":0,\"wind\":%.2f,\"temp\":%.2f,"
           "\"pressure\":%.2f,\"kind\":\"sensor\",\"reconstructed\":false}",
           NODE_ID, (unsigned long)seq, wind, temp, seaLevel);

  if (random(100) < LOSS_PERCENT) {
    Serial.printf("seq=%lu LOST (simulated)\n", (unsigned long)seq);
  } else {
    sendJson(json);
    Serial.println(json);
  }

  if (seq % HOUSEKEEPING_EVERY == 0) {
    hkSeq++;
    float battery = analogRead(PIN_BATTERY) / 4095.0 * 3.3 * 2.0;
    snprintf(json, sizeof(json),
             "{\"node\":\"%s\",\"seq\":%lu,\"time\":\"\",\"kind\":\"housekeeping\",\"battery_v\":%.2f,\"rssi\":%d}",
             NODE_ID, (unsigned long)hkSeq, battery, (int)WiFi.RSSI());
    sendJson(json);
  }
}

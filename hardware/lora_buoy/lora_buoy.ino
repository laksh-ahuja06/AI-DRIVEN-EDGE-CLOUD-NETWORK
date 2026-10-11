/*
 * ESP32 + LoRa (SX1278 "Ra-02", 433 MHz) buoy node  -- OPTIONAL UPGRADE
 * ----------------------------------------------------------------------
 * A genuinely constrained, lossy radio link instead of Wi-Fi. LoRa airtime is
 * precious, so the payload is a compact CSV line (~30 bytes) instead of JSON:
 *
 *     B07,42,18.50,29.10,1006.30
 *     node,seq,wind,temp,pressure
 *
 * The receiving ESP32 (lora_receiver.ino) prints each packet on USB serial and
 * hardware/serial_bridge.py turns it back into the JSON telemetry format and
 * forwards it to edge_gateway.py.
 *
 * Wiring SX1278 Ra-02 -> ESP32: NSS=5, SCK=18, MISO=19, MOSI=23, RST=14, DIO0=26,
 * 3.3V, GND (never 5V!). Always attach the antenna before powering the module.
 * BMP280 on I2C SDA=21, SCL=22. Potentiometer ("wind knob") on GPIO34.
 * BOOT button toggles storm mode, as in esp32_buoy.ino.
 *
 * Libraries: "LoRa" by Sandeep Mistry, "Adafruit BMP280 Library".
 * Check the LoRa frequency allowed in your country (India: 865-867 MHz licence-free;
 * 433 MHz modules are common in labs - confirm with your faculty).
 */
#include <SPI.h>
#include <LoRa.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

const char *NODE_ID = "B07";             // keep it short: every byte costs airtime
const long LORA_FREQ = 433E6;            // 433E6 / 865E6 / 868E6 depending on your module
const int SPREADING_FACTOR = 9;          // 7 (fast) .. 12 (long range, slow)
const float ALTITUDE_M = 216.0;
const uint32_t INTERVAL_MS = 2000;

const int PIN_NSS = 5, PIN_RST = 14, PIN_DIO0 = 26;
const int PIN_WIND_POT = 34, PIN_BOOT = 0;

Adafruit_BMP280 bmp;
bool bmpOk = false, stormMode = false;
float stormLevel = 0.0;
uint32_t seq = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BOOT, INPUT_PULLUP);
  Wire.begin(21, 22);
  bmpOk = bmp.begin(0x76) || bmp.begin(0x77);
  LoRa.setPins(PIN_NSS, PIN_RST, PIN_DIO0);
  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("LoRa init failed - check wiring");
    while (true) delay(1000);
  }
  LoRa.setSpreadingFactor(SPREADING_FACTOR);
  LoRa.setSignalBandwidth(125E3);
  LoRa.enableCrc();
  Serial.println("LoRa buoy ready");
}

void loop() {
  static uint32_t lastSend = 0;
  static bool lastBtn = HIGH;
  bool btn = digitalRead(PIN_BOOT);
  if (btn == LOW && lastBtn == HIGH) {
    stormMode = !stormMode;
    Serial.printf("Storm mode %s\n", stormMode ? "ON" : "off");
    delay(200);
  }
  lastBtn = btn;
  if (millis() - lastSend < INTERVAL_MS) return;
  lastSend = millis();

  stormLevel = stormMode ? min(1.0f, stormLevel + 0.05f) : max(0.0f, stormLevel - 0.08f);
  float temp = bmpOk ? bmp.readTemperature() : 28.0;
  float station = bmpOk ? bmp.readPressure() / 100.0 : 1008.0;
  float pressure = station / pow(1.0 - ALTITUDE_M / 44330.0, 5.255) - 35.0 * stormLevel;
  float wind = analogRead(PIN_WIND_POT) / 4095.0 * 120.0 + 70.0 * stormLevel;

  char line[64];
  snprintf(line, sizeof(line), "%s,%lu,%.2f,%.2f,%.2f", NODE_ID, (unsigned long)++seq, wind, temp, pressure);
  LoRa.beginPacket();
  LoRa.print(line);
  LoRa.endPacket();
  Serial.println(line);
}

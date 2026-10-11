/*
 * ESP32 + LoRa receiver at the edge gateway  -- OPTIONAL UPGRADE
 * ----------------------------------------------------------------
 * Receives the compact CSV packets from lora_buoy.ino and prints one line per
 * packet on USB serial, with the radio signal quality appended:
 *
 *     B07,42,18.50,29.10,1006.30,-87,7.25
 *     node,seq,wind,temp,pressure,rssi_dBm,snr_dB
 *
 * Plug this board into the laptop / Raspberry Pi running the gateway and run:
 *     python hardware/serial_bridge.py --port /dev/ttyUSB0      (COM3 on Windows)
 *
 * Same wiring and LoRa settings as lora_buoy.ino (they must match).
 */
#include <SPI.h>
#include <LoRa.h>

const long LORA_FREQ = 433E6;
const int SPREADING_FACTOR = 9;
const int PIN_NSS = 5, PIN_RST = 14, PIN_DIO0 = 26;

void setup() {
  Serial.begin(115200);
  LoRa.setPins(PIN_NSS, PIN_RST, PIN_DIO0);
  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("# LoRa init failed - check wiring");
    while (true) delay(1000);
  }
  LoRa.setSpreadingFactor(SPREADING_FACTOR);
  LoRa.setSignalBandwidth(125E3);
  LoRa.enableCrc();
  Serial.println("# LoRa receiver ready");
}

void loop() {
  int size = LoRa.parsePacket();
  if (size == 0) return;
  String line;
  while (LoRa.available()) line += (char)LoRa.read();
  Serial.printf("%s,%d,%.2f\n", line.c_str(), LoRa.packetRssi(), LoRa.packetSnr());
}

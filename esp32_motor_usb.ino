// ESP32 motor over USB. Laptop sends '1' -> motor spins, '0' -> motor stops.
// No Wi-Fi, no libraries. Board: "ESP32 Dev Module". Serial Monitor/baud: 115200.
const int IN1 = 26;   // -> driver IN1
const int IN2 = 27;   // -> driver IN2
const int LED = 2;    // on-board LED mirrors the motor

void setMotor(bool on) {
  digitalWrite(IN1, on ? HIGH : LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(LED, on ? HIGH : LOW);
  Serial.println(on ? "MOTOR ON (CRITICAL)" : "MOTOR OFF (NORMAL)");
}

void setup() {
  Serial.begin(115200);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT); pinMode(LED, OUTPUT);
  setMotor(false);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '1') setMotor(true);
    else if (c == '0') setMotor(false);
  }
}

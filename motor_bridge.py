"""Watches logs/gateway.log; CRITICAL packet -> '1' (motor spins), alert cleared -> '0' (motor stops).
Usage:  pip install pyserial
        python motor_bridge.py --port COM3          (Linux/Mac: /dev/ttyUSB0)
        python motor_bridge.py --port COM3 --test   (type 1 / 0 to test the motor without the gateway)
Run from the project folder, AFTER python run_demo.py has started.
"""
import argparse, os, time
import serial

ap = argparse.ArgumentParser()
ap.add_argument("--port", required=True)
ap.add_argument("--log", default="logs/gateway.log")
ap.add_argument("--test", action="store_true")
a = ap.parse_args()

esp = serial.Serial(a.port, 115200, timeout=0.1)
time.sleep(2)  # ESP32 resets when the port opens

if a.test:
    while True:
        k = input("type 1 (spin) or 0 (stop): ").strip()
        if k in ("0", "1"):
            esp.write(k.encode())

while not os.path.exists(a.log):
    print("waiting for", a.log); time.sleep(1)

state = None
def set_state(on, why):
    global state
    if on != state:
        state = on
        esp.write(b"1" if on else b"0")
        print(("MOTOR ON  <- " if on else "MOTOR OFF <- ") + why)

with open(a.log, errors="ignore") as f:
    f.seek(0, os.SEEK_END)          # only react to NEW lines
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.05); continue
        if " CRITICAL " in line or "alert ACTIVE" in line:
            set_state(True, line.strip()[:90])
        elif "alert cleared" in line:
            set_state(False, "alert cleared (back to NORMAL)")

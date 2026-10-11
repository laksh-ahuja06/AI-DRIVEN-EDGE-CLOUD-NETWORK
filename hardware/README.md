# Hardware guide (college-friendly)

The software already simulates every node. For the hardware part you **replace the
simulated buoys/radars with real ESP32 sensor nodes**. They send the same JSON
packets over Wi-Fi/UDP, so the gateway, the QoS, the LSTM recovery and the dashboard
work unchanged. The satellite ground station stays in software: real multispectral
imagery would need a real ground station.

```
 [ESP32 "buoy" #1]--Wi-Fi/UDP--+                                    
 [ESP32 "buoy" #2]--Wi-Fi/UDP--+--> Edge gateway  --UDP--> Central server --> Dashboard
 [satellite_station.py]--------+    (laptop or        (laptop)              (browser)
 [simulated sensors, optional]-+     Raspberry Pi)
        ^                                 |
        +---- alert (UDP 9004): LED + buzzer on the buoy switch on during a cyclone alert
```

What you can show with this: **real sensing** (temperature/pressure from a BMP280, wind
from a knob or a DIY anemometer), a **real lossy wireless link** (Wi-Fi, or LoRa as an
upgrade), **edge prioritisation** of critical packets, **gap reconstruction** of the
packets that really got lost, and a **feedback loop**: the gateway's alert lights the LED
and sounds the buzzer on the buoy.

---

## 1. Shopping list

Approximate Indian prices (Robu.in / Amazon / local electronics market, 2025–26). Check
your college lab first: most of this is usually already there.

### Tier 1: minimum build (recommended), about ₹1,600–2,200 for two nodes

| Item | Qty | Approx. ₹ (each) | Notes |
|---|---|---|---|
| ESP32 DevKit V1 (30-pin, ESP-WROOM-32) | 2 | 350–450 | One per "buoy"/"radar" node |
| BMP280 module (I²C, 3.3 V) | 2 | 100–150 | Temperature + pressure. BME280 (₹300–450) also works and adds humidity |
| 10 kΩ potentiometer | 2 | 10–20 | "Wind knob" for indoor demos |
| Active buzzer (3.3–5 V) | 2 | 15–25 | Cyclone alert sound |
| BC547 / 2N2222 NPN transistor + 1 kΩ resistor | 2 | 5 | Drives the buzzer (do not power a buzzer straight from a GPIO) |
| LED + 220 Ω resistor (optional) | 2 | 5 | The on-board LED (GPIO2) already works |
| Breadboard (830 points) | 2 | 80–120 | |
| Jumper wires (M-M, M-F) | 1 set | 60–100 | |
| Micro-USB data cable | 2 | 80 | Must be a data cable, not charge-only |
| Power bank | 1–2 | (own) | Lets the "buoy" run away from the laptop |

The laptop runs the gateway, the server and the dashboard. A **phone hotspot** is the
easiest Wi-Fi network (see Troubleshooting).

### Tier 2: real wind sensor, about ₹50–150 extra per node

Pick one:
- **Reed switch + small magnet** (₹20–40). Simplest: two wires, no power needed.
- **A3144 hall sensor + neodymium magnet** (₹30–60).

Build the rotor from 3 cups (ping-pong ball halves or plastic spoons) glued to a
**fidget spinner** or a CD on a bearing. Fix the magnet to the rotor and the sensor
beside it, giving one pulse per revolution. Calibrate `KMH_PER_HZ` with a table fan and
a phone anemometer app, or by holding it out of a car/bike window at a known speed.

### Tier 3: optional upgrades

| Upgrade | Extra cost | What it adds |
|---|---|---|
| Raspberry Pi 3/4 as the edge gateway | borrow from lab (₹4,500+ new) | A physically separate edge tier: the Pi runs `edge_gateway.py`, the laptop runs the server |
| 2× LoRa SX1278 Ra-02 + antennas (+1 extra ESP32) | ₹800–1,100 | A genuinely low-bandwidth, lossy radio link instead of Wi-Fi (sketches included) |
| 6 V solar panel + TP4056 charger + 18650 cell & holder | ₹450–600 | Self-powered "buoy" |
| Plastic bottle / PVC pipe enclosure | ~₹50 | Float the node in a bucket of water for a photo-ready "buoy" demo |
| 0.96" SSD1306 OLED | ₹150–200 | Show readings and alert state on the node itself |

---

## 2. Wiring (Tier 1 node)

```
BMP280            ESP32
  VCC  ---------- 3V3        (never 5 V)
  GND  ---------- GND
  SCL  ---------- GPIO22
  SDA  ---------- GPIO21

10k potentiometer (wind knob)
  outer pin ----- 3V3
  outer pin ----- GND
  middle pin ---- GPIO34     (input-only ADC pin)

Buzzer via NPN transistor
  GPIO25 --[1 kΩ]-- transistor base
  transistor emitter -- GND
  transistor collector -- buzzer (-)
  buzzer (+) ----------- 5V/VIN

Alert LED: the on-board blue LED on GPIO2 (or LED + 220 Ω from GPIO2 to GND)
Storm-mode button: the BOOT button already on the board (GPIO0)
```

**Wind sensor instead of the knob:** set `#define WIND_POT 0` in the sketch.
- Reed switch: one leg to GPIO27, the other to GND (the sketch enables the internal pull-up).
- A3144: VCC to VIN (5 V), GND to GND, OUT to GPIO27. The open-collector output is pulled
  up to 3.3 V internally, so it is safe for the ESP32.

**Battery voltage (optional):** two 100 kΩ resistors as a divider from the battery to
GPIO35. Without it, `battery_v` simply reports 0.

---

## 3. Flash the ESP32

1. Install the **Arduino IDE 2.x**.
2. *File → Preferences → Additional boards manager URLs:*
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
3. *Tools → Board → Boards Manager*: install **esp32 by Espressif Systems**.
4. *Tools → Manage Libraries*: install **Adafruit BMP280 Library** (accept its
   dependencies). For LoRa, also install **LoRa** by Sandeep Mistry.
5. Open `hardware/esp32_buoy/esp32_buoy.ino` and edit the top section:
   - `WIFI_SSID`, `WIFI_PASSWORD`
   - `GATEWAY_IP`: the IP of the laptop/Pi running `edge_gateway.py` (`ipconfig` on
     Windows, `ip a` or `hostname -I` on Linux/Pi)
   - `NODE_ID`: unique per board, e.g. `BUOY_HW_01`, `RADAR_HW_01`
   - `ALTITUDE_M`: your campus altitude (Vellore ≈ 216 m, Chennai ≈ 6 m). This converts
     station pressure to sea-level pressure. **Without it, an inland campus reads
     ~988 hPa and every packet looks like a cyclone.**
6. *Tools → Board → ESP32 Dev Module*, pick the COM port, then **Upload**. If it hangs
   at "Connecting...", hold BOOT for a moment.
7. Open the Serial Monitor at **115200 baud**: you should see one JSON line per second.

The sketches were syntax-checked but could not be compiled against the real ESP32 core
in the environment they were written in. If the IDE reports an error, it will most
likely be a library-version difference, usually a one-line fix.

---

## 4. Run the system with the hardware

On the laptop (same Wi-Fi/hotspot as the ESP32s):

```bash
pip install -r requirements.txt
python run_demo.py --no-sensors          # server + gateway only; ESP32 nodes are the sensors
# or
python run_demo.py                       # hardware nodes AND simulated buoys + satellite together
```

Open http://127.0.0.1:8000. Each ESP32 appears as a row and chart (`BUOY_HW_01`, ...).

Allow UDP ports **9001** (sensors to gateway) and **9004** (alerts to nodes) through the
laptop firewall. Windows asks the first time Python listens on the network: click
*Allow* for private networks.

**Raspberry Pi as the edge gateway (Tier 3):**
```bash
# on the Pi
SERVER_HOST=<laptop-ip> python3 edge_gateway.py
# on the laptop
GATEWAY_HOST=<pi-ip> uvicorn central_server:app --host 0.0.0.0 --port 8000
```
Set `GATEWAY_IP` in the sketch to the Pi's IP.

**LoRa link (Tier 3):** flash `lora_buoy.ino` on the buoy and `lora_receiver.ino` on a
second ESP32 plugged into the gateway machine by USB, then run
`pip install pyserial` and `python hardware/serial_bridge.py --port COM3`
(`/dev/ttyUSB0` on Linux/Pi). LoRa wiring is in the sketch header. Attach the antenna
before powering the module, and use the LoRa frequency your faculty approves.

---

## 5. Demo script for the review (about 5 minutes)

1. **Normal monitoring.** The dashboard shows live readings from the real BMP280 and the
   wind knob/anemometer. Traffic is `NORMAL`, risk is low.
2. **Cyclone detected at the edge.** Turn the wind knob past 60 km/h, or press **BOOT**
   (storm mode ramps pressure down by up to 35 hPa and wind up). The gateway marks the
   packets `CRITICAL`, and the hybrid ML policy often flags them a few readings
   *before* the thresholds are crossed, because pressure is falling fast. The gateway
   enters alert mode and keeps reserving bandwidth for critical traffic.
3. **Feedback loop.** The alert travels back to the buoy: the **LED blinks and the buzzer
   beeps**. The fused risk on the dashboard crosses 60 and the alert banner turns red.
4. **Packet loss and recovery.** Set `LOSS_PERCENT 20` in the sketch, or put the ESP32 in
   a steel tiffin box / walk it to the edge of Wi-Fi range for real loss. Lost sequence
   numbers show up on the dashboard as **yellow dots**: gaps repaired by the LSTM. Hollow
   dots are real-time forecasts published while a packet is overdue.
5. **Bandwidth.** The satellite panel shows 2 MB frames reduced to about 1 KB at the
   edge (≈99.95 % saved).
6. **Numbers.** Show `results/REPORT.md` (produced by `python evaluate.py`): QoS latency,
   reconstruction error and classifier lead time.

---

## 6. Troubleshooting

| Symptom | Fix |
|---|---|
| ESP32 connects to Wi-Fi but nothing reaches the gateway | College Wi-Fi often isolates clients from each other. Use a **phone hotspot** for laptop + ESP32s. Check `GATEWAY_IP` and the firewall (UDP 9001). |
| `BMP280 NOT found` | SDA/SCL swapped, or address 0x77 vs 0x76 (the sketch tries both). Run an I²C scanner sketch. |
| Every packet is CRITICAL | `ALTITUDE_M` not set (inland pressure < 990 hPa), or the knob is turned up. |
| Gateway logs `dropped invalid packet` | The JSON was malformed or a value is outside physical ranges (e.g. pressure 0 because the sensor is missing). |
| No LED/buzzer on alert | The gateway learns a node's IP from its packets, so the node must have sent at least one. Check UDP 9004 is allowed. |
| Upload fails / port not visible | Use a data USB cable; install the CP210x or CH340 USB driver. |

## Safety

- BMP280, LoRa modules and ESP32 GPIOs are **3.3 V only**.
- Never power a LoRa module without its antenna.
- Li-ion (18650) cells: use a protected cell and a TP4056 module with protection. Do
  not short or puncture them.
- Keep electronics in a sealed bottle if you float a "buoy" in water.

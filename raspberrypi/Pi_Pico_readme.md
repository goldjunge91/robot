Plattform: 4× DC-Motoren mit Hall-Quadraturencoder (A/B), 2× TB6612 (je 2 Kanäle)

Zusätzliche Aktoren: 2× ESC (50 Hz) + 1× Continuous-Servo (Gear)

Controller: Raspberry Pi Pico (Steuerung/Encoder), Raspberry Pi 4B (High-Level)
Versorgung: 4S-Li-Ion → Buck-Wandler (s. unten)
Komponenten

Akkupack: 4S Li-Ion (14.8 V nominal, 16.8 V voll)

Motoren: 4× 12 V 520-Getriebemotor mit Hall-AB-Encoder (3.3 V)

Motortreiber: 2× TB6612FNG (je 2 Kanäle)

ESCs: 2× 30/40 A, linear BEC 5 V/3 A → nur Signal/GND verwenden, 5 V nicht einspeisen

Servo: INJORA INJS022-360 (4.8–6.0 V, 360° CR)

Controller: 1× Raspberry Pi Pico, 1× Raspberry Pi 4B

Buck-Wandler:

MP1584 #1 → ~12.0 V → TB6612 #1 (VM)

MP1584 #2 → ~12.0 V → TB6612 #2 (VM)

MP1584 #3 → 6.0 V → Servo (optional; 6 V = mehr Drehmoment)

UBEC 5 V/5 A → Raspberry Pi 4B und Pico VSYS (5 V)

Schutz & Puffer:

P6KE18A (18 V TVS) auf 4S-Akkuschiene (Ring an +Akku)

Elkos 470–1000 µF an jedem TB6612-VM, 0.1 µF nahe VM/VCC

100 nF direkt über den Motorklemmen, Sicherungen 5–10 A je Motor

Kleinkram: Breadboards/Leitungen, evtl. 10 k Pull-ups für Encoder (intern reicht meist)

Pin-Mapping (Pico RP2040, final)

Kurz und präzise: konkretes Pin‑Mapping (Pico RP2040) + Verkabelungshinweise für

- 4 × DC‑Motoren über 2 × TB6612 (je 2 Kanäle) mit je 1 Quadraturencoder
- 2 × ESC (50 Hz) + 1 × Continuous‑Servo (Gear)  
Die vorhandene MicroPyth.py nutzt ESC1=GP14, ESC2=GP15, GEAR=GP16 — das bleibt so.

Wichtiges vorab (Kurz):

- Motor‑Versorgung (VM) an TB6612 direkt 12 V (Batterie/Netzteil). GND immer gemeinsam verbinden (Pico, TB6612, Batterie, ESC).
- TB6612 Vcc (Logik): 3.3 V vom Pico → STBY HIGH. TB6612 akzeptiert 3.3 V Logik praktisch, bei Problemen Level‑Shifter verwenden.
- Motor‑PWM für TB6612: 2 kHz–20 kHz empfohlen (z. B. 2 kHz). ESC/Servo → 50 Hz.
- Encoder VCC → 3.3 V, A/B → Pico GPIO mit Pull‑ups (entweder interne oder 10k extern).
- STBY beider TB6612 miteinander verbinden und an Pico GP0.

Pinmap (empfohlen, auf Pico):

````python
# Pinmap (RP2040 / Pico)
# TB6612: zwei Chips, jeder steuert 2 Motoren (A/B). STBY shared -> GP0
PINMAP = {
  # TB6612 Standby (beide Treiber an denselben Pin)
  "TB_STBY" : 0,    # GP0 -> HIGH

  # Motor Front-Left  (TB1 Channel A)
  "M_FL_IN1": 18,   # DIR (geändert)
  "M_FL_IN2": 19,   # DIR (geändert)
  "M_FL_PWM": 2,    # PWM (20 kHz)

  # Motor Front-Right (TB1 Channel B)
  "M_FR_IN1": 17,   # DIR
  "M_FR_IN2": 20,   # DIR
  "M_FR_PWM": 3,    # PWM (20 kHz)

  # Motor Rear-Left   (TB2 Channel A)
  "M_RL_IN1": 21,   # DIR
  "M_RL_IN2": 22,   # DIR
  "M_RL_PWM": 4,    # PWM (20 kHz)

  # Motor Rear-Right  (TB2 Channel B)
  "M_RR_IN1": 26,   # DIR  (ADC-Pin, als Digital ok)
  "M_RR_IN2": 27,   # DIR  (ADC-Pin, als Digital ok)
  "M_RR_PWM": 5,    # PWM (20 kHz)

  # Encoder (A/B je Motor)
  "ENC_FL_A": 8,  "ENC_FL_B": 9,
  "ENC_FR_A": 10, "ENC_FR_B": 11,
  "ENC_RL_A": 12, "ENC_RL_B": 13,
  "ENC_RR_A": 6,  "ENC_RR_B": 7,   # verlegt, weil 18/19 jetzt FL-DIR sind

  # ESCs + CR-Servo (50 Hz)
  "ESC1": 14,      # GP14
  "ESC2": 15,      # GP15
  "GEAR": 16       # GP16
}

````

Frequenzen / Software
Motor-PWM: 2–20 kHz (mit TB6612 gern 20 kHz → leise)
ESC/Servo: 50 Hz, 1000–2000 µs (Servo ggf. 500–2500 µs)
Encoder-ISR: leichtgewichtig (A-Rising IRQ, B im Handler lesen) oder PIO-Quadratur
Kurz‑Wiring / Anschlussliste

- Strom:
  - Batterie/Netzteil +12 V -> TB6612 VM pins (alle TBs)
  - Batterie GND -> TB6612 GNDs, Pico GND, ESC GNDs (gemeinsame Masse!)
  - Pico 3.3 V -> TB6612 VCC (Logik), Encoder VCC, Pull‑ups falls extern
  - MP1584 Buck(s) wenn du aus 12 V 5/3.3 V erzeugst (je nach Setup)
TB6612 #1 (Front-Räder)
PWMA → GP2, AIN1 → GP6, AIN2 → GP7 → Motor FL (AO1/AO2)
PWMB → GP3, BIN1 → GP17, BIN2 → GP20 → Motor FR (BO1/BO2)
STBY → GP0 (HIGH),
VCC → 3V3(OUT)
VM → ~12 V (MP1584)
GND → GND
TB6612 #2 (Rear-Räder)
PWMA → GP4, AIN1 → GP21, AIN2 → GP22 → Motor RL (AO1/AO2)
PWMB → GP5, BIN1 → GP26, BIN2 → GP27 → Motor RR (BO1/BO2)
STBY → GP0 (HIGH)
VCC → 3V3(OUT)
VM → ~12 V (MP1584)
GND → GND

Encoder: +3.3 V vom Pico, GND gemeinsam.
ESC/Servo: Signale an GP14/15/16, 5 V für ESC-Logik (falls OPTO) & Servo aus deinem UBEC/MP1584, roten BEC-Draht der ESCs nicht in die 5-V-Rail einspeisen.

Slices sind damit getrennt, die Frequenzen beeinflussen sich nicht.
Einfaches ASCII‑Schaltbild (vereinfachte Übersicht)

````text
[Battery +12V] ----+--------------------> TB6612 VM (both boards)
                   |
                   +--> ESC power +
[Battery GND] --------------------+--> TB6612 GNDs
                                  +--> Pico GND
                                  +--> ESC GNDs
                                  +--> Encoder GNDs
[Pico 3V3] --> TB6612 VCC (logic)
           --> Encoder VCC
Pico GP0 (HIGH) -> TB6612 STBY (tie both STBY pins together if 2 chips)
Motor FL: Pico GP2 (IN1) , GP7 (IN2) , GP2 (PWM) -> TB6612 CH_A inputs
Motor FR: Pico GP17 (IN1) , GP20 (IN2) , GP3 (PWM) -> TB6612 CH_B inputs
Motor RL: Pico GP21(IN1) ,GP22(IN2) ,GP4(PWM) -> TB6612 #2 CH_A
Motor RR: Pico G P26(IN1) ,GP27(IN2) ,GP5(PWM) -> TB6612 #2 CH_B
Enc FL: Pico GP8/GP9  (A/B)
Enc FR: Pico GP10/GP11
Enc RL: Pico GP12/GP13
Enc RR: Pico GP18/GP19
ESC1 sig -> GP14
ESC2 sig -> GP15
Gear servo -> GP16
````

```py
# Raspberry Pi Pico (RP2040) - MicroPython 
# 2 ESCs + 1 CR-Servo (Zahnrad) per Terminal steuern
# 4 Motors with encoder 

from machine import Pin, PWM
import utime
import sys
import micropython
micropython.alloc_emergency_exception_buf(256)

# ======= Konfiguration =======

M_PWM_PINS = [2, 3, 4, 5]  # ENA/ENB beider L298N

ESC1_PIN = 14
ESC2_PIN = 15
GEAR_PIN = 16

PWM_FREQ = 50            # 50 Hz für Servos/ESCs
MIN_US = 1000
CENTER_US = 1500
MAX_US = 2000

# Zahnrad-Servo (CR) – Startwerte (kalibrierbar)

one_rev_ms = 900         # geschätzte Dauer für 1 Umdrehung
gear_speed_percent = 60  # Geschwindigkeit beim Drehen (0..100)

PINMAP = {
    # TB6612 Standby (beide Treiber an denselben Pin)
    "TB_STBY": 0,  # GP0 -> HIGH
    # Motor Front-Left  (TB1 Channel A)
    "M_FL_IN1": 18,  # DIR (geändert)
    "M_FL_IN2": 19,  # DIR (geändert)
    "M_FL_PWM": 2,  # PWM (20 kHz)
    # Motor Front-Right (TB1 Channel B)
    "M_FR_IN1": 17,  # DIR
    "M_FR_IN2": 20,  # DIR
    "M_FR_PWM": 3,  # PWM (20 kHz)
    # Motor Rear-Left   (TB2 Channel A)
    "M_RL_IN1": 21,  # DIR
    "M_RL_IN2": 22,  # DIR
    "M_RL_PWM": 4,  # PWM (20 kHz)
    # Motor Rear-Right  (TB2 Channel B)
    "M_RR_IN1": 26,  # DIR  (ADC-Pin, als Digital ok)
    "M_RR_IN2": 27,  # DIR  (ADC-Pin, als Digital ok)
    "M_RR_PWM": 5,  # PWM (20 kHz)
    # Encoder (A/B je Motor)
    "ENC_FL_A": 8,
    "ENC_FL_B": 9,
    "ENC_FR_A": 10,
    "ENC_FR_B": 11,
    "ENC_RL_A": 12,
    "ENC_RL_B": 13,
    "ENC_RR_A": 6,
    "ENC_RR_B": 7,  # verlegt, weil 18/19 jetzt FL-DIR sind
    # ESCs + CR-Servo (50 Hz)
    "ESC1": 14,  # GP14
    "ESC2": 15,  # GP15
    "GEAR": 16,  # GP16
}

# Beispiel für 4 Motoren

ENC = [
    {"A": Pin(6, Pin.IN, Pin.PULLUP), "B": Pin(7, Pin.IN, Pin.PULLUP), "cnt": 0},  # FL
    {"A": Pin(8, Pin.IN, Pin.PULLUP), "B": Pin(9, Pin.IN, Pin.PULLUP), "cnt": 0},  # FR
    {"A": Pin(0, Pin.IN, Pin.PULLUP), "B": Pin(1, Pin.IN, Pin.PULLUP), "cnt": 0},  # RL
    {
        "A": Pin(22, Pin.IN, Pin.PULLUP),
        "B": Pin(26, Pin.IN, Pin.PULLUP),
        "cnt": 0,
    },  # RR
]
def _mk_isr(idx):
    def isr(pin):
        e = ENC[idx]
        # bei A-Rising: B lesen -> Richtung
        if e["B"].value() == 0:
            e["cnt"] += 1
        else:
            e["cnt"] -= 1

    return isr

for i in range(4):
    ENC[i]["A"].irq(trigger=Pin.IRQ_RISING, handler=_mk_isr(i))

# Richtungspins (siehe Mapping oben)

M_DIR = [
    (Pin(10, Pin.OUT), Pin(11, Pin.OUT)),  # FL IN1/IN2
    (Pin(12, Pin.OUT), Pin(13, Pin.OUT)),  # FR
    (Pin(18, Pin.OUT), Pin(19, Pin.OUT)),  # RL
    (Pin(20, Pin.OUT), Pin(21, Pin.OUT)),  # RR
]

M_pwms = []
for p in M_PWM_PINS:
    pwm = PWM(Pin(p, Pin.OUT))
    pwm.freq(20000)            # 20 kHz (leise)
    pwm.duty_u16(0)            # aus
    M_pwms.append(pwm)

def motor_set(i, speed_pct):  # i=0..3, speed -100..+100
    speed_pct = max(-100, min(100, int(speed_pct)))
    fwd = speed_pct >= 0
    a, b = M_DIR[i]
    a.value(1 if fwd else 0)
    b.value(0 if fwd else 1)
    duty = int(65535 * abs(speed_pct) / 100)
    M_pwms[i].duty_u16(duty)

def motors_stop():
    for i in range(4):
        motor_set(i, 0)

# ======= Hilfsfunktionen =======

def us_to_duty(us, freq=PWM_FREQ):
    # duty_u16 = 65535 *(us / Period)
    # Period (us) = 1_000_000 / freq
    duty = int(65535* us * freq / 1_000_000)
    # Clamp sicherheitshalber
    if duty < 0: duty = 0
    if duty > 65535: duty = 65535
    return duty

def mecanum(vx, vy, wz):
    fl =  vx - vy - wz
    fr =  vx + vy + wz
    rl =  vx + vy - wz
    rr =  vx - vy + wz
    m  = max(1.0, max(abs(fl), abs(fr), abs(rl), abs(rr)))
    vals = [int(100*fl/m), int(100*fr/m), int(100*rl/m), int(100*rr/m)]
    for i,v in enumerate(vals): motor_set(i, v)

class ServoLike:
    """Generische PWM-Steuerung für Servo/ESC."""
    def __init__(self, pin, freq=PWM_FREQ, min_us=MIN_US, max_us=MAX_US, center_us=CENTER_US):
        self.pwm = PWM(Pin(pin, Pin.OUT))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us
        self.center_us = center_us
        # Start sicher
        self.pulse_us(self.center_us)

    def pulse_us(self, us):
        us = max(self.min_us, min(self.max_us, int(us)))
        self.pwm.duty_u16(us_to_duty(us))

    # Für ESCs: 0..100% → 1000..2000 µs
    def throttle_percent(self, p):
        p = max(0, min(100, int(p)))
        us = self.min_us + (self.max_us - self.min_us) * p // 100
        self.pulse_us(us)

    # Für Continuous-Servo: -100..100%, 0 = Stop
    def speed_percent(self, p):
        p = max(-100, min(100, int(p)))
        span = (self.max_us - self.min_us) // 2  # ±500 µs
        us = self.center_us + int(span * (p / 100.0))
        self.pulse_us(us)

    def stop(self):
        self.pulse_us(self.center_us)

    def deinit(self):
        try:
            self.stop()
            self.pwm.deinit()
        except:
            pass

# ======= Geräte anlegen =======

esc1 = ServoLike(ESC1_PIN)
esc2 = ServoLike(ESC2_PIN)
gear = ServoLike(GEAR_PIN)

# ESCs sicher initial auf Minimum

esc1.throttle_percent(0)
esc2.throttle_percent(0)
gear.stop()

# ======= Funktionen =======

def arm_escs(seconds=3):
    print(f"[INFO] ESCs armen ({seconds}s) mit Minimum-Gas …")
    esc1.throttle_percent(0)
    esc2.throttle_percent(0)
    utime.sleep(seconds)
    print("[OK] Arming abgeschlossen.")

def set_esc(esc_id, percent):
    if esc_id == 1:
        esc1.throttle_percent(percent)
    elif esc_id == 2:
        esc2.throttle_percent(percent)

def set_both(percent):
    esc1.throttle_percent(percent)
    esc2.throttle_percent(percent)

def gear_one_rotation(cw=True):
    global gear_speed_percent, one_rev_ms
    spd = gear_speed_percent if cw else -gear_speed_percent
    gear.speed_percent(spd)
    utime.sleep_ms(one_rev_ms)
    gear.stop()
    print(f"[OK] Zahnrad: 1 Umdrehung {'CW' if cw else 'CCW'}.")

def print_help():
    print("""
Befehle:
  arm                      - ESCs armen (3s Min-Gas)
  esc1 <0-100>             - ESC1 auf Prozent
  esc2 <0-100>             - ESC2 auf Prozent
  both <0-100>             - beide ESCs gleich setzen
  stop                     - beide ESCs auf 0% und Zahnrad stop
  gear                     - Zahnrad 1 Umdrehung im Uhrzeigersinn
  gearccw                  - Zahnrad 1 Umdrehung gegen Uhrzeigersinn
  setrev <ms>              - Dauer für 1 Umdrehung kalibrieren (z.B. 880)
  gearspeed <0-100>        - Drehgeschwindigkeit für Zahnrad setzen
  pulse <dev> <us>         - Rohpuls senden: dev=esc1|esc2|gear, us=1000..2000
  help                     - diese Hilfe
  quit                     - beendet Programm sauber
""")

print("=== Pico Servo/ESC Terminal ===")
print_help()

# ======= Hauptloop =======

try:
    while True:
        try:
            line = input("cmd> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()

        try:
            if cmd == "help":
                print_help()

            elif cmd == "arm":
                arm_escs(3)

            elif cmd == "esc1" and len(parts) >= 2:
                set_esc(1, int(float(parts[1])))

            elif cmd == "esc2" and len(parts) >= 2:
                set_esc(2, int(float(parts[1])))

            elif cmd == "both" and len(parts) >= 2:
                set_both(int(float(parts[1])))

            elif cmd == "stop":
                set_both(0)
                gear.stop()
                print("[OK] Alles gestoppt.")

            elif cmd == "gear":
                gear_one_rotation(True)

            elif cmd == "gearccw":
                gear_one_rotation(False)

            elif cmd == "setrev" and len(parts) >= 2:
                one_rev_ms = max(100, int(float(parts[1])))
                print(f"[OK] one_rev_ms = {one_rev_ms} ms")

            elif cmd == "gearspeed" and len(parts) >= 2:
                gear_speed_percent = max(0, min(100, int(float(parts[1]))))
                print(f"[OK] gear_speed_percent = {gear_speed_percent}%")

            elif cmd == "pulse" and len(parts) >= 3:
                dev = parts[1].lower()
                us = max(MIN_US, min(MAX_US, int(float(parts[2]))))
                if dev == "esc1":
                    esc1.pulse_us(us)
                elif dev == "esc2":
                    esc2.pulse_us(us)
                elif dev == "gear":
                    gear.pulse_us(us)
                else:
                    print("[ERR] Unbekanntes Gerät (esc1|esc2|gear).")
                print(f"[OK] {dev} ← {us} µs")

            elif cmd in ("quit", "exit"):
                break

            else:
                print("[ERR] Unbekannter Befehl. 'help' für Übersicht.")
        except Exception as e:
            print("[ERR]", e)

finally:
    # Alles sicher stoppen
    try:
        set_both(0)
        gear.stop()
    except:
        pass
    esc1.deinit()
    esc2.deinit()
    gear.deinit()
    print("\n[INFO] Beendet. Outputs sicher gestoppt.")
```
# Raspberry Pi Pico (RP2040) - MicroPython
# 2 ESCs + 1 CR-Servo (Zahnrad) per Terminal steuern
# Pins (anpassen): ESC1=GP14, ESC2=GP15, GEAR=GP16

from machine import Pin, PWM
import utime, sys

# ======= Konfiguration =======
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

# ======= Hilfsfunktionen =======
def us_to_duty(us, freq=PWM_FREQ):
    # duty_u16 = 65535 * (us / Period)
    # Period (us) = 1_000_000 / freq
    duty = int(65535 * us * freq / 1_000_000)
    # Clamp sicherheitshalber
    if duty < 0: duty = 0
    if duty > 65535: duty = 65535
    return duty

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

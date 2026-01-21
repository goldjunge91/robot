# Raspberry Pi Pico (RP2040) - MicroPython
# 2 ESCs + 1 CR-Servo (Zahnrad) per Terminal steuern
# 4 Motors with encoder

from machine import Pin, PWM
import utime
import sys
import micropython

micropython.alloc_emergency_exception_buf(256)

# IRQ helper: expect real IRQ control on target hardware.
# Prefer micropython.disable_irq/enable_irq, fall back to machine.disable_irq/enable_irq.
try:
    _disable_irq = micropython.disable_irq
    _enable_irq = micropython.enable_irq
except AttributeError:
    import machine as _machine

    try:
        _disable_irq = _machine.disable_irq
        _enable_irq = _machine.enable_irq
    except AttributeError:
        raise RuntimeError(
            "IRQ control not available: require micropython.disable_irq or machine.disable_irq on target hardware"
        )

# ======= Fixed Pin Map =======
PINMAP = {
    # TB6612 Standby (beide Treiber an denselben Pin)
    "TB_STBY": 28,  # GP0 -> HIGH
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

# ======= Configuration derived from PINMAP =======
M_PWM_PINS = [
    PINMAP["M_FL_PWM"],
    PINMAP["M_FR_PWM"],
    PINMAP["M_RL_PWM"],
    PINMAP["M_RR_PWM"],
]

ESC1_PIN = PINMAP["ESC1"]
ESC2_PIN = PINMAP["ESC2"]
GEAR_PIN = PINMAP["GEAR"]

PWM_FREQ = 50  # 50 Hz für Servos/ESCs
MIN_US = 1000
CENTER_US = 1500
MAX_US = 2000
MOTOR_PWM_FREQ = 10000  # 10 kHz recommended compromise (was 20000)

# Zahnrad-Servo (CR) – Startwerte (kalibrierbar)
one_rev_ms = 2200  # geschätzte Dauer für 1 Umdrehung
# Initial speed settings (range 0‑100)
gear_speed_percent = 60  # Speed for gear rotation (0..100)
default_speed = 50  # Default speed for WASD commands (0..100)

# Beispiel für 4 Motoren - fixed indexing to match motor order: FL, FR, RL, RR
ENC = [
    {
        "A": Pin(PINMAP["ENC_FL_A"], Pin.IN, Pin.PULL_UP),
        "B": Pin(PINMAP["ENC_FL_B"], Pin.IN, Pin.PULL_UP),
        "cnt": 0,
        "last": 0,
    },  # FL - index 0
    {
        "A": Pin(PINMAP["ENC_FR_A"], Pin.IN, Pin.PULL_UP),
        "B": Pin(PINMAP["ENC_FR_B"], Pin.IN, Pin.PULL_UP),
        "cnt": 0,
        "last": 0,
    },  # FR - index 1
    {
        "A": Pin(PINMAP["ENC_RL_A"], Pin.IN, Pin.PULL_UP),
        "B": Pin(PINMAP["ENC_RL_B"], Pin.IN, Pin.PULL_UP),
        "cnt": 0,
        "last": 0,
    },  # RL - index 2
    {
        "A": Pin(PINMAP["ENC_RR_A"], Pin.IN, Pin.PULL_UP),
        "B": Pin(PINMAP["ENC_RR_B"], Pin.IN, Pin.PULL_UP),
        "cnt": 0,
        "last": 0,
    },  # RR - index 3
]


def _mk_isr(idx):
    # 4x quadrature decode lookup table (transitions)
    LUT = (0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0)

    def isr(pin):
        irq = _disable_irq()
        e = ENC[idx]
        # current 2-bit state: A<<1 | B
        cur = (e["A"].value() << 1) | e["B"].value()
        idx_lut = (e.get("last", cur) << 2) | cur
        e["cnt"] += LUT[idx_lut]
        e["last"] = cur
        _enable_irq(irq)

    return isr


# attach IRQ on BOTH edges for A and B to get full resolution
for i in range(4):
    ENC[i]["last"] = (ENC[i]["A"].value() << 1) | ENC[i]["B"].value()
    handler = _mk_isr(i)
    ENC[i]["A"].irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handler)
    ENC[i]["B"].irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handler)


# Neue Hilfsfunktionen: Encoder lesen / zurücksetzen
def read_enc_counts():
    irq_state = _disable_irq()
    vals = [ENC[i]["cnt"] for i in range(4)]
    _enable_irq(irq_state)
    return vals


def reset_enc_counts():
    irq_state = _disable_irq()
    for i in range(4):
        ENC[i]["cnt"] = 0
    _enable_irq(irq_state)


# Richtungspins (siehe Mapping oben)

M_DIR = [
    (Pin(PINMAP["M_FL_IN1"], Pin.OUT), Pin(PINMAP["M_FL_IN2"], Pin.OUT)),  # FL
    (Pin(PINMAP["M_FR_IN1"], Pin.OUT), Pin(PINMAP["M_FR_IN2"], Pin.OUT)),  # FR
    (Pin(PINMAP["M_RL_IN1"], Pin.OUT), Pin(PINMAP["M_RL_IN2"], Pin.OUT)),  # RL
    (Pin(PINMAP["M_RR_IN1"], Pin.OUT), Pin(PINMAP["M_RR_IN2"], Pin.OUT)),  # RR
]

M_pwms = []
for p in M_PWM_PINS:
    pwm = PWM(Pin(p, Pin.OUT))
    pwm.freq(MOTOR_PWM_FREQ)  # 10 kHz (leise)
    pwm.duty_u16(0)  # aus
    M_pwms.append(pwm)

_last_sign = [0, 0, 0, 0]  # -1, 0, +1 per motor


def motor_set(i, speed_pct):  # i=0..3, speed -100..+100
    # Clamp to safe range and convert
    speed_pct = max(-100, min(100, int(speed_pct)))
    a, b = M_DIR[i]

    # Zero speed: set PWM to 0 and put bridge into a safe stop
    if speed_pct == 0:
        M_pwms[i].duty_u16(0)
        # For TB6612, equal inputs are a brake state. Using 0/0 keeps it simple.
        a.value(0)
        b.value(0)
        _last_sign[i] = 0
        print(f"[DBG] motor_set({i}) STOP -> DIR={a.value()},{b.value()} DUTY=0")
        return

    new_sign = 1 if speed_pct > 0 else -1

    # If changing direction under load, briefly cut PWM before flipping DIR
    if _last_sign[i] != 0 and _last_sign[i] != new_sign:
        M_pwms[i].duty_u16(0)
        utime.sleep_ms(2)

    # Apply direction, then PWM duty
    a.value(1 if new_sign > 0 else 0)
    b.value(0 if new_sign > 0 else 1)
    duty = int(65535 * abs(speed_pct) / 100)
    M_pwms[i].duty_u16(duty)
    _last_sign[i] = new_sign

    # Debug output
    try:
        print(
            f"[DBG] motor_set({i}) -> sign={new_sign} DIR={a.value()},{b.value()} DUTY={duty} ({abs(speed_pct)}%)"
        )
    except Exception:
        pass


def motors_stop():
    for i in range(4):
        motor_set(i, 0)


# ======= Hilfsfunktionen =======


def us_to_duty(us, freq=PWM_FREQ):
    # duty_u16 = 65535 *(us / Period)
    # Period (us) = 1_000_000 / freq
    duty = int(65535 * us * freq / 1_000_000)
    # Clamp sicherheitshalber
    if duty < 0:
        duty = 0
    if duty > 65535:
        duty = 65535
    return duty


def mecanum(vx, vy, wz):
    # Standard mecanum wheel mixing (assuming front-left wheel orientation)
    fl = vx + vy + wz
    fr = vx - vy - wz
    rl = vx - vy + wz
    rr = vx + vy - wz
    m = max(1.0, max(abs(fl), abs(fr), abs(rl), abs(rr)))
    vals = [int(100 * fl / m), int(100 * fr / m), int(100 * rl / m), int(100 * rr / m)]
    for i, v in enumerate(vals):
        motor_set(i, v)


def parse_speed_arg(parts, current_default):
    """Parse optional speed from CLI parts and update default if a single arg is given.
    Returns (speed_to_use, new_default_speed).
    """
    speed = current_default
    new_default = current_default
    if len(parts) >= 2:
        try:
            s = int(float(parts[1]))
            s = max(0, min(100, s))
            speed = s
            if len(parts) == 2:
                new_default = s
        except Exception:
            pass
    return speed, new_default


class ServoLike:
    """Generische PWM-Steuerung für Servo/ESC."""

    def __init__(
        self, pin, freq=PWM_FREQ, min_us=MIN_US, max_us=MAX_US, center_us=CENTER_US
    ):
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

# Enable standby pin
Pin(PINMAP["TB_STBY"], Pin.OUT).value(1)

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
    # Ensure percent is within 0‑100 before applying to ESC
    percent = max(0, min(100, int(percent)))
    if esc_id == 1:
        esc1.throttle_percent(percent)
    elif esc_id == 2:
        esc2.throttle_percent(percent)
    else:
        print("[ERR] Invalid ESC id (must be 1 or 2)")


def set_both(percent):
    # Clamp percent to safe range before sending to both ESCs
    percent = max(0, min(100, int(percent)))
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
    print(
        """
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
      enc                      - Zeigt aktuelle Encoder-Zähler (FL,FR,RL,RR)
      enc reset                - Setzt alle Encoder-Zähler auf 0

      Movement Commands (WASD):
      w [speed]                - Move forward (uses default_speed)
      s [speed]                - Move backward
      a [speed]                - Strafe left
      d [speed]                - Strafe right
      q [speed]                - Turn left (CCW)
      e [speed]                - Turn right (CW)
      x                        - Stop all motors

      speed                    - Show or set default_speed (e.g., speed 75)

      help                     - diese Hilfe (ESC id validation added)
      quit                     - beendet Programm sauber
    """
    )


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
                handled = False
                if dev == "esc1":
                    esc1.pulse_us(us)
                    handled = True
                elif dev == "esc2":
                    esc2.pulse_us(us)
                    handled = True
                elif dev == "gear":
                    gear.pulse_us(us)
                    handled = True
                if handled:
                    print(f"[OK] {dev} ← {us} µs")
                else:
                    print("[ERR] Unbekanntes Gerät (esc1|esc2|gear).")

            elif cmd == "enc":
                # "enc" -> anzeigen, "enc reset" -> nullen
                if len(parts) >= 2 and parts[1].lower() in ("reset", "zero", "clear"):
                    reset_enc_counts()
                    print("[OK] Encoder-Zähler zurückgesetzt.")
                else:
                    vals = read_enc_counts()
                    print(f"[INFO] Encoder counts (FL,FR,RL,RR): {vals}")

            elif cmd == "w":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(speed, 0, 0)
                print(f"[OK] Moving forward at {speed}%")

            elif cmd == "s":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(-speed, 0, 0)
                print(f"[OK] Moving backward at {speed}%")

            elif cmd == "a":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(0, -speed, 0)
                print(f"[OK] Strafing left at {speed}%")

            elif cmd == "d":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(0, speed, 0)
                print(f"[OK] Strafing right at {speed}%")

            elif cmd == "q":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(0, 0, -speed)
                print(f"[OK] Turning left at {speed}%")

            elif cmd == "e":
                speed, default_speed = parse_speed_arg(parts, default_speed)
                mecanum(0, 0, speed)
                print(f"[OK] Turning right at {speed}%")

            elif cmd == "x":
                motors_stop()
                print("[OK] All motors stopped")

            elif cmd == "speed":
                if len(parts) >= 2:
                    try:
                        new_speed = max(0, min(100, int(float(parts[1]))))
                        default_speed = new_speed
                        print(f"[OK] default_speed set to {new_speed}%")
                    except ValueError:
                        print("[ERR] Invalid speed value")
                else:
                    print(f"[INFO] default_speed = {default_speed}%")

            elif cmd == "motortest" and len(parts) >= 4:
                try:
                    idx = int(parts[1])
                    pct = int(float(parts[2]))
                    ms = int(float(parts[3]))
                    if not (0 <= idx < 4):
                        print("[ERR] index muss 0..3 sein")
                    else:
                        print(f"[OK] Test motor {idx} @ {pct}% für {ms}ms")
                        motor_set(idx, pct)
                        utime.sleep_ms(ms)
                        motor_set(idx, 0)
                except Exception as ex:
                    print("[ERR] motortest:", ex)

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

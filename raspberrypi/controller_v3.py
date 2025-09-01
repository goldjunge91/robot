# Verkabelungs-Check für DEIN PINMAP auf Raspberry Pi Pico (MicroPython)
# Testet: 2x TB6612, 4x DC + Encoder, 2x ESC, 1x 360°-Servo
# Terminal 115200 Baud

from machine import Pin, PWM
import time

PINMAP = {
    "TB_STBY": 28,   # GP0 -> HIGH (Hinweis: Für UART0 frei machen? s.u.)
    # Motor Front-Left  (TB1 Channel A)
    "M_FL_IN1": 18, "M_FL_IN2": 19, "M_FL_PWM": 2,   # PWM 20 kHz (GP2 -> Slice1A)
    # Motor Front-Right (TB1 Channel B)
    "M_FR_IN1": 17, "M_FR_IN2": 20, "M_FR_PWM": 3,   # PWM 20 kHz (GP3 -> Slice1B)
    # Motor Rear-Left   (TB2 Channel A)
    "M_RL_IN1": 21, "M_RL_IN2": 22, "M_RL_PWM": 4,   # PWM 20 kHz (Slice2A)
    # Motor Rear-Right  (TB2 Channel B)
    "M_RR_IN1": 26, "M_RR_IN2": 27, "M_RR_PWM": 5,   # PWM 20 kHz (Slice2B)
    # Encoder A/B
    "ENC_FL_A": 8,  "ENC_FL_B": 9,
    "ENC_FR_A": 10, "ENC_FR_B": 11,
    "ENC_RL_A": 12, "ENC_RL_B": 13,
    "ENC_RR_A": 6,  "ENC_RR_B": 7,
    # ESCs + 360°-Servo (50 Hz)
    "ESC1": 14,     # Slice7A
    "ESC2": 15,     # Slice7B
    "GEAR": 16,     # GP16 (Kommentar in deiner Liste war vertauscht)
}

# ===== Helpers =====
def pwm_init(pin, freq):
    p = PWM(Pin(pin))
    p.freq(freq)
    return p

def pwm_duty_u16(pwm, duty_u16):
    if duty_u16 < 0: duty_u16 = 0
    if duty_u16 > 65535: duty_u16 = 65535
    pwm.duty_u16(duty_u16)

def set_pulse_us(pwm, us, period_us=20000):
    duty = int(us * 65535 // period_us)
    pwm_duty_u16(pwm, duty)

class TB6612Channel:
    def __init__(self, pin_pwm, pin_in1, pin_in2, pwm_freq=20000):
        self.in1 = Pin(pin_in1, Pin.OUT, value=0)
        self.in2 = Pin(pin_in2, Pin.OUT, value=0)
        self.pwm = pwm_init(pin_pwm, pwm_freq)
        pwm_duty_u16(self.pwm, 0)

    # speed: -1.0..+1.0
    def drive(self, speed):
        if speed > 1: speed = 1
        if speed < -1: speed = -1
        mag = int(abs(speed) * 65535)
        if speed > 0:
            self.in1.value(1); self.in2.value(0)
        elif speed < 0:
            self.in1.value(0); self.in2.value(1)
        else:
            self.in1.value(0); self.in2.value(0)
        pwm_duty_u16(self.pwm, mag)

    def stop(self):
        self.in1.value(0); self.in2.value(0)
        pwm_duty_u16(self.pwm, 0)

class TB6612Board:
    def __init__(self, chA_pins, chB_pins, stby_pin, pwm_freq=20000):
        self.stby = Pin(stby_pin, Pin.OUT, value=1)
        self.chA = TB6612Channel(*chA_pins, pwm_freq=pwm_freq)
        self.chB = TB6612Channel(*chB_pins, pwm_freq=pwm_freq)

    def enable(self, en=True): self.stby.value(1 if en else 0)

class QuadEncoder:
    def __init__(self, pin_a, pin_b):
        self.a = Pin(pin_a, Pin.IN, Pin.PULLUP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULLUP)
        self.count = 0
        self.last = (self.a.value() << 1) | self.b.value()
        self.a.irq(self._cb, Pin.IRQ_RISING | Pin.IRQ_FALLING)
        self.b.irq(self._cb, Pin.IRQ_RISING | Pin.IRQ_FALLING)

    def _cb(self, _):
        state = (self.a.value() << 1) | self.b.value()
        delta = ((self.last << 2) | state)
        if delta in (0b0001, 0b0111, 0b1110, 0b1000): self.count += 1
        elif delta in (0b0010, 0b0100, 0b1101, 0b1011): self.count -= 1
        self.last = state

# ===== Setup =====
print("\n[Pico Minimal-Test mit DEINEM PINMAP]")
board1 = TB6612Board(
    (PINMAP["M_FL_PWM"], PINMAP["M_FL_IN1"], PINMAP["M_FL_IN2"]),
    (PINMAP["M_FR_PWM"], PINMAP["M_FR_IN1"], PINMAP["M_FR_IN2"]),
    stby_pin=PINMAP["TB_STBY"],
    pwm_freq=20000
)
board2 = TB6612Board(
    (PINMAP["M_RL_PWM"], PINMAP["M_RL_IN1"], PINMAP["M_RL_IN2"]),
    (PINMAP["M_RR_PWM"], PINMAP["M_RR_IN1"], PINMAP["M_RR_IN2"]),
    stby_pin=PINMAP["TB_STBY"],
    pwm_freq=20000
)

enc = {
    "FL": QuadEncoder(PINMAP["ENC_FL_A"], PINMAP["ENC_FL_B"]),
    "FR": QuadEncoder(PINMAP["ENC_FR_A"], PINMAP["ENC_FR_B"]),
    "RL": QuadEncoder(PINMAP["ENC_RL_A"], PINMAP["ENC_RL_B"]),
    "RR": QuadEncoder(PINMAP["ENC_RR_A"], PINMAP["ENC_RR_B"]),
}

esc1 = pwm_init(PINMAP["ESC1"], 50)   # ESC1 + ESC2 teilen Slice7 -> gleiche 50 Hz
esc2 = pwm_init(PINMAP["ESC2"], 50)
servo = pwm_init(PINMAP["GEAR"], 50)  # eigener Slice (Slice0A), 50 Hz

led = Pin(25, Pin.OUT)

def pulse(ms): led.value(1); time.sleep(ms/1000); led.value(0)

def dump_enc():
    print(" Enc:", {k: v.count for k, v in enc.items()})

def motor_step(lbl, ch, speed, t=1.0):
    print(" ", lbl, "speed=%.2f" % speed)
    ch.drive(speed); time.sleep(t); ch.stop()

# ===== Tests =====
print("\n[I²C/LiDAR Hinweis] In diesem Mapping sind derzeit keine freien Hardware-Pins für I²C/UART reserviert – Sensor-Tests sind deaktiviert.")

print("\n[Motor/Encoder] 30% vor/zurück je Achse")
for label, ch in (("FL", board1.chA), ("FR", board1.chB), ("RL", board2.chA), ("RR", board2.chB)):
    motor_step(f"{label} vor",  ch, +0.30, 1.0); dump_enc(); time.sleep(0.2)
    motor_step(f"{label} rück", ch, -0.30, 1.0); dump_enc(); time.sleep(0.2)

print("\n[ESC] Neutral → Kurz High → Neutral (vorsichtig!)")
for p in (esc1, esc2):
    # Falls Arming nötig: hier ggf. 1100 µs für 2s vorsehen
    for us in (1500, 1800, 1500):
        duty = int(us * 65535 // 20000)
        pwm_duty_u16(p, duty)
        time.sleep(0.9)

print("\n[Servo 360°] 1100 µs → 1900 µs → 1500 µs (Stop)")
for us in (1100, 1900, 1500):
    set_pulse_us(servo, us); time.sleep(1.0)

print("\n[Fertig] Encoder sollten vor/rück entgegengesetzte Zählrichtung zeigen.")
pulse(120)

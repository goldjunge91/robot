# Minimal TB6612 motor test for Raspberry Pi Pico (MicroPython)
# Focus: make 4 DC motors move reliably.

from machine import Pin, PWM
import utime

# Single source of truth: wiring map
PINMAP = {
    "TB_STBY": 0,   # Tie both TB6612 STBY pins to GP0 and drive HIGH

    # Front-Left (TB6612 #1 CH A)
    "M_FL_IN1": 18,
    "M_FL_IN2": 19,
    "M_FL_PWM": 2,

    # Front-Right (TB6612 #1 CH B)
    "M_FR_IN1": 17,
    "M_FR_IN2": 20,
    "M_FR_PWM": 3,

    # Rear-Left (TB6612 #2 CH A)
    "M_RL_IN1": 21,
    "M_RL_IN2": 22,
    "M_RL_PWM": 4,

    # Rear-Right (TB6612 #2 CH B)
    "M_RR_IN1": 26,
    "M_RR_IN2": 27,
    "M_RR_PWM": 5,
}

MOTOR_PWM_FREQ = 10000  # 10 kHz (quiet, well within TB6612 limits)


# Enable TB6612 chips (STBY HIGH)
Pin(PINMAP["TB_STBY"], Pin.OUT).value(1)

# Direction pins: (IN1, IN2) per motor in order FL, FR, RL, RR
M_DIR = [
    (Pin(PINMAP["M_FL_IN1"], Pin.OUT), Pin(PINMAP["M_FL_IN2"], Pin.OUT)),
    (Pin(PINMAP["M_FR_IN1"], Pin.OUT), Pin(PINMAP["M_FR_IN2"], Pin.OUT)),
    (Pin(PINMAP["M_RL_IN1"], Pin.OUT), Pin(PINMAP["M_RL_IN2"], Pin.OUT)),
    (Pin(PINMAP["M_RR_IN1"], Pin.OUT), Pin(PINMAP["M_RR_IN2"], Pin.OUT)),
]

# PWM pins
M_pwms = []
for p in (PINMAP["M_FL_PWM"], PINMAP["M_FR_PWM"], PINMAP["M_RL_PWM"], PINMAP["M_RR_PWM"]):
    pwm = PWM(Pin(p, Pin.OUT))
    pwm.freq(MOTOR_PWM_FREQ)
    pwm.duty_u16(0)
    M_pwms.append(pwm)

_last_sign = [0, 0, 0, 0]


def motor(i: int, pct: int) -> None:
    """Set motor i (0..3 = FL, FR, RL, RR) to speed -100..+100.
    Uses TB6612 truth table (IN1/IN2) and PWM duty.
    """
    if not (0 <= i < 4):
        return
    pct = int(pct)
    if pct > 100:
        pct = 100
    if pct < -100:
        pct = -100

    a, b = M_DIR[i]

    if pct == 0:
        # Stop PWM and set 0/0 (coast/low) to be safe
        M_pwms[i].duty_u16(0)
        a.value(0)
        b.value(0)
        _last_sign[i] = 0
        return

    sign = 1 if pct > 0 else -1
    # If reversing direction, briefly drop PWM
    if _last_sign[i] != 0 and _last_sign[i] != sign:
        M_pwms[i].duty_u16(0)
        utime.sleep_ms(2)

    # Apply direction then duty
    a.value(1 if sign > 0 else 0)
    b.value(0 if sign > 0 else 1)
    duty = int(65535 * abs(pct) / 100)
    M_pwms[i].duty_u16(duty)
    _last_sign[i] = sign


def all_stop():
    for i in range(4):
        motor(i, 0)


def self_test():
    print("Self-test: each motor forward/back at 40%")
    for idx in range(4):
        print(" Motor", idx, "FWD")
        motor(idx, 40)
        utime.sleep_ms(800)
        motor(idx, 0)
        utime.sleep_ms(200)
        print(" Motor", idx, "REV")
        motor(idx, -40)
        utime.sleep_ms(800)
        motor(idx, 0)
        utime.sleep_ms(300)
    print("Done.")


if __name__ == "__main__":
    try:
        self_test()
        print("Enter commands: 'm <i> <pct>', 'all <pct>', 'stop', 'quit'")
        while True:
            try:
                line = input("cmd> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()
            if cmd == "m" and len(parts) >= 3:
                i = int(parts[1]); pct = int(float(parts[2]))
                motor(i, pct)
            elif cmd == "all" and len(parts) >= 2:
                pct = int(float(parts[1]))
                for i in range(4):
                    motor(i, pct)
            elif cmd in ("stop", "x"):
                all_stop()
            elif cmd in ("quit", "exit"):
                break
            else:
                print("Commands: m <i 0..3> <pct -100..100> | all <pct> | stop | quit")
    finally:
        all_stop()
        print("Stopped. TB6612 outputs idle.")


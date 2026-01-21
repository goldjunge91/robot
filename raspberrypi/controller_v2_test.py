# Simple test script for controller_v2.py
# This script can be run on the Raspberry Pi Pico (MicroPython) to verify basic functionality.
# It demonstrates initialization, ESC arming, speed setting, gear rotation, and mecanum movement.

# import utime
import time

import controller_v2 as ctrl
# Minimal MicroPython "machine" shim for local testing


class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    PULL_DOWN = 3

    def __init__(self, pin_id, mode=OUT, pull=None):
        self.pin_id = pin_id
        self.mode = mode
        self.pull = pull
        self._value = 0

    def init(self, mode=None, pull=None):
        if mode is not None:
            self.mode = mode
        if pull is not None:
            self.pull = pull

    def value(self, v=None):
        if v is None:
            return self._value
        self._value = 1 if v else 0

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0


class PWM:
    def __init__(self, pin):
        self.pin = pin
        self._freq = 50
        self._duty_u16 = 0

    def freq(self, f=None):
        if f is None:
            return self._freq
        self._freq = int(f)

    def duty_u16(self, val=None):
        if val is None:
            return self._duty_u16
        self._duty_u16 = int(max(0, min(65535, val)))

    def duty(self, val=None):
        if val is None:
            return (self._duty_u16 * 1023) // 65535
        if val <= 1023:
            self._duty_u16 = int((val / 1023) * 65535)
        else:
            self._duty_u16 = int(max(0, min(65535, val)))

    def deinit(self):
        self._duty_u16 = 0


def ADC(pin):
    raise NotImplementedError("ADC shim: not implemented in this test shim")


# MicroPython-like API for local testing on CPython
def sleep(seconds):
    time.sleep(seconds)


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def sleep_us(us):
    time.sleep(us / 1_000_000.0)


def ticks_ms():
    return time.time_ns() // 1_000_000


def ticks_us():
    return time.time_ns() // 1_000


def ticks_diff(new, old):
    # keep same sign semantics as MicroPython: new - old
    return int(new - old)


# Import the controller module (assumes this script is in the same directory)


def demo_initialization():
    print("[Demo] Initializing controller and printing help")
    ctrl.print_help()

def demo_esc_arm():
    print("[Demo] Arming ESCs for 2 seconds (minimum throttle)")
    ctrl.arm_escs(2)

def demo_set_esc():
    print("[Demo] Setting ESC1 to 40% and ESC2 to 70%")
    ctrl.set_esc(1, 40)
    ctrl.set_esc(2, 70)
    utime.sleep(1)
    ctrl.set_both(0)

def demo_gear():
    print("[Demo] Rotating gear clockwise")
    ctrl.gear_one_rotation(True)
    utime.sleep(0.5)
    print("[Demo] Rotating gear counter‑clockwise")
    ctrl.gear_one_rotation(False)

def demo_mecanum():
    print("[Demo] Moving forward at default speed")
    ctrl.mecanum(ctrl.default_speed, 0, 0)
    utime.sleep(1)
    print("[Demo] Strafing right at 60%")
    ctrl.mecanum(0, 60, 0)
    utime.sleep(1)
    print("[Demo] Turning left at 30%")
    ctrl.mecanum(0, 0, -30)
    utime.sleep(1)
    ctrl.motors_stop()

def demo_encoder_counts():
    print("[Demo] Encoder tick counts (raw)")
    for i, enc in enumerate(ctrl.ENC):
        print(f"  Encoder {i}: {enc['cnt']} ticks")
    # In a real test you would move the robot and verify counters change.

def run_all():
    demo_initialization()
    demo_esc_arm()
    demo_set_esc()
    demo_gear()
    demo_mecanum()
    demo_encoder_counts()
    print("[Demo] All tests completed.")

if __name__ == "__main__":
    run_all()

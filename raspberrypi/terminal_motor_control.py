#!/usr/bin/env python3

import sys
import termios
import tty
from time import sleep
import RPi.GPIO as GPIO
# from motor import Motor  # deine Motor-Klasse arbeitet im BOARD-Modus
# Raspberry Pi TB6612FNG Library

# BOARD = physische Pin-Nummern
GPIO.setmode(GPIO.BOARD)
# GPIO.setmode(GPIO.BCM)

class Motor:
	in1 = ""
	in2 = ""
	pwm = ""
	standbyPin = ""

	# Defaults
	hertz = 1000
	reverse = False  # Reverse flips the direction of the motor

	# Constructor (Pins jetzt als BOARD/physische Nummern übergeben!)
	def __init__(self, in1, in2, pwm, standbyPin, reverse):
		self.in1 = in1
		self.in2 = in2
		self.pwm = pwm
		self.standbyPin = standbyPin
		self.reverse = reverse

		GPIO.setup(in1, GPIO.OUT)
		GPIO.setup(in2, GPIO.OUT)
		GPIO.setup(pwm, GPIO.OUT)
		GPIO.setup(standbyPin, GPIO.OUT)
		GPIO.output(standbyPin, GPIO.HIGH)  # STBY aktiv

		self.p = GPIO.PWM(pwm, self.hertz)
		self.p.start(0)

	# Speed from -100 to 100
	def drive(self, speed):
		# clamp & Richtung
		try:
			speed = int(speed)
		except:
			pass
		speed = max(-100, min(100, speed))

		# Reverse-Option anwenden
		if self.reverse:
			speed = -speed

		dutyCycle = abs(speed)

		if speed > 0:
			GPIO.output(self.in1, GPIO.HIGH)
			GPIO.output(self.in2, GPIO.LOW)
		elif speed < 0:
			GPIO.output(self.in1, GPIO.LOW)
			GPIO.output(self.in2, GPIO.HIGH)
		else:
			# Coast: beide LOW
			GPIO.output(self.in1, GPIO.LOW)
			GPIO.output(self.in2, GPIO.LOW)

		self.p.ChangeDutyCycle(dutyCycle)

	def brake(self):
		self.p.ChangeDutyCycle(0)
		# Elektronische Bremse: beide HIGH
		GPIO.output(self.in1, GPIO.HIGH)
		GPIO.output(self.in2, GPIO.HIGH)

	def standby(self, value):
		self.p.ChangeDutyCycle(0)
		GPIO.output(self.standbyPin, value)

	def __del__(self):
		try:
			self.p.ChangeDutyCycle(0)
		except:
			pass
		GPIO.cleanup()
  
  
# ===== Pin-Layout (BOARD/physische Pins) =====
# TB6612 #1  -> Motor1 (A), Motor2 (B)
STBY1  = 11   # GPIO17
M1_IN1 = 13   # GPIO27
M1_IN2 = 15   # GPIO22
M1_PWM = 12   # GPIO18 (PWM möglich)

M2_IN1 = 16   # GPIO23
M2_IN2 = 18   # GPIO24
M2_PWM = 33   # GPIO13 (PWM möglich)

# TB6612 #2  -> Motor3 (A), Motor4 (B)
STBY2  = 22   # GPIO25
M3_IN1 = 29   # GPIO5
M3_IN2 = 31   # GPIO6
M3_PWM = 32   # GPIO12 (PWM möglich)

M4_IN1 = 36   # GPIO16
M4_IN2 = 38   # GPIO20
M4_PWM = 35   # GPIO19 (PWM möglich)

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def choose_motors():
    while True:
        print("Wähle Motor: [1] M1, [2] M2, [3] M3, [4] M4, [5] Alle")
        c = input("Auswahl (1/2/3/4/5): ").strip()
        if c in ("1", "2", "3", "4", "5"):
            return int(c)
        print("Ungültige Auswahl. Bitte 1, 2, 3, 4 oder 5 eingeben.")

def print_help(speed, sel):
    names = {1:"M1",2:"M2",3:"M3",4:"M4",5:"Alle"}
    print("--- Steuerung ---")
    print("w: vorwärts | d: rückwärts | s/Space: stop | +: schneller | -: langsamer")
    print("q: quit | m: Motor-Auswahl ändern (1–5) | Aktuell: {} | Geschwindigkeit: {}%".format(names.get(sel, "?"), speed))
    print("-----------------")

def main():
    # reverse-Flags bei Bedarf anpassen (True kehrt Drehrichtung um)
    M1 = Motor(M1_IN1, M1_IN2, M1_PWM, STBY1, True)
    M2 = Motor(M2_IN1, M2_IN2, M2_PWM, STBY1, False)
    M3 = Motor(M3_IN1, M3_IN2, M3_PWM, STBY2, True)
    M4 = Motor(M4_IN1, M4_IN2, M4_PWM, STBY2, False)

    sel = choose_motors()

    def selected_list(code):
        if code == 1: return [M1]
        if code == 2: return [M2]
        if code == 3: return [M3]
        if code == 4: return [M4]
        return [M1, M2, M3, M4]  # code == 5

    motors = selected_list(sel)
    speed = 50  # %
    running = True

    try:
        # STBY beider Treiber aktivieren
        for m in (M1, M2, M3, M4):
            try:
                m.standby(True)
            except Exception:
                pass

        print_help(speed, sel)
        while running:
            print('\nTaste (w/d/s/+/-/1-5/m/q): ', end='', flush=True)
            ch = getch()
            print(ch)

            if ch == 'w':
                for m in motors:
                    m.drive(speed)
                print(f"Fahre vorwärts {speed}%")
            elif ch == 'd':
                for m in motors:
                    m.drive(-speed)
                print(f"Fahre rückwärts {speed}%")
            elif ch in ('s', ' '):
                for m in motors:
                    m.drive(0)
                print("Stopp")
            elif ch == 'm':
                sel = choose_motors()
                motors = selected_list(sel)
                print_help(speed, sel)
            elif ch in ('1','2','3','4','5'):
                sel = int(ch)
                motors = selected_list(sel)
                print_help(speed, sel)
            elif ch == '+':
                speed = min(100, speed + 10)
                print(f"Geschwindigkeit: {speed}%")
            elif ch == '-':
                speed = max(0, speed - 10)
                print(f"Geschwindigkeit: {speed}%")
            elif ch == 'q':
                running = False
            else:
                print("Unbekannte Taste. Hilfe: w/d/s/+/ - / 1..5 / m / q")

    except KeyboardInterrupt:
        print('\nBeende wegen STRG-C')
    finally:
        try:
            for m in (M1, M2, M3, M4):
                try:
                    m.drive(0)
                    m.standby(False)
                except Exception:
                    pass
        except Exception:
            pass
        print('Programm beendet.')

if __name__ == '__main__':
    main()

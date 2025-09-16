
# Omnidirectional Robot — Projektbeschreibung

Ziel

Aufbau einer omnidirektionalen Plattform mit Mecanum-Antrieb zur Fernsteuerung und Computer-Vision-gestützte Assistenzfunktionen.

Scope

Enthalten sind mechanisches Chassis mit Mecanum-Rädern, Antriebs- und Leistungs-elektronik, Basis-Sensorik, Steuer- und Recheneinheiten sowie Telemetrie- und Logging-Funktionen. Externe Infrastruktur  wird nicht beschrieben.

Features

- Omnidirektionale Fahrt (seitwärts, diagonal, Rotation auf der Stelle)
- Individuelle PWM-Steuerung der Antriebs-motoren
- Onboard-Strom-/Spannungs-Monitoring für Batterie-Überwachung
- Abstandsmessung für Hinderniserkennung
- USB-Kamera-Integration für CV und Video-Streaming

# Komponentenliste

## Hardware
<!-- RUNCCI-YUN 8pcs TT Motoren -->
- 4x GM3865-520 12V DC Reduction Ratio 1:40, Metal Gear Motor with Hall Encoder Feedback, Suitable for Small Wheelbase Robots (300RPM) (L-Type 520 Motor)
- 4x Mecanum-Radsatz 80mm
- TB6612FNG Motor Driver
- INA3221 3-Kanal Sensor
- ADS1115 16-Bit ADC
- TCA9548A I2C Multiplexer
- VL53L0X ?? unklar
- 1x TM1637 LED-Anzeigemodul
- 1x Raspberry Pi 4B 8GB
- 1x USB-Kameras (1080p)
- 1x Displays (10", 5")
- 1x INJS022-360 22KG 360° Digital Servo
- 1x 9g Servos
- 2x RS2205 2205 2300KV CW CCW Bürstenloser Motor für FPV RC QAV250 X210 Racing
- Xbox Controller
- Verkabelung / Jumper

## Elektronik

- 2x Brushless Motoren & 2x ESC 40A für Brushless Motoren (Nerf dart launcher)
- Lidar LDS01RR
Load Sharing Components ?? unklar

## Batterie und Batterieladung

- 18650 Batteriehalter
- 3S Lademodul USB-C 4A
- EVE INR18650-25P
- TP4056 Lademodule
- 3S 10A Li-Ion Batterieschutzplatine

Systemarchitektur

- Steuer- und Wahrnehmungsebene: Raspberry Pi 4B führt CV, Benutzer-Interface und Telemetrie zusammen; USB-Kameras sind direkt am Pi angeschlossen.
- Motorsteuerung: TB6612FNG-Module erhalten PWM/DIR-Signale von Pi Pico oder MCU zuRS2205 2205 2300KV CW CCW Bürstenloser Motor für FPV RC QAV250 X210 Racing Ansteuerung der DC-Motoren, Motorstromversorgung über die Akku-/Power-Ebene.
- Sensorbus: INA3221, ADS1115 und VL53L0X sind per I2C angebunden; bei Adresskonflikten kann ein I2C-Multiplexer eingesetzt werden.
- Energie- und Ladeebene: 3S-Akku, Batterieschutzplatine und Lademodule versorgen Motor- und Elektronikspannungen; Load-Sharing-Hardware steuert Ladebetrieb und Versorgung.

Kommunikation und Bedienung

- Xbox-Controller (Bluetooth/USB) oder Smartphone-App für manuelle Steuerung

- WiFi-Interface für Telemetrie, Web-Dashboard.

# Kernentscheidungen

- Antrieb: Mecanum-Räder (omnidirektional)
- Motor-Treiber: TB6612FNG
- Steuerung: Raspberry Pi 4B

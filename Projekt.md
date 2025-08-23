

# Omnidirectional Robot — Projektbeschreibung

Ziel

Aufbau einer omnidirektionalen Plattform mit Mecanum-Antrieb zur Fernsteuerung und für spätere Computer-Vision-gestützte Assistenzfunktionen.

Scope

Enthalten sind mechanisches Chassis mit Mecanum-Rädern, Antriebs- und Leistungs-elektronik, Basis-Sensorik, Steuer- und Recheneinheiten sowie Telemetrie- und Logging-Funktionen. Externe Infrastruktur (Netzwerk, Ladeinfrastruktur) wird nicht beschrieben.

Features

- Omnidirektionale Fahrt (seitwärts, diagonal, Rotation auf der Stelle)
- Individuelle PWM-Steuerung der Antriebs-motoren
- Onboard-Strom-/Spannungs-Monitoring für Batterie-Überwachung
- Abstandsmessung für Hinderniserkennung
- USB-Kamera-Integration für CV und Video-Streaming

Komponentenliste

RUNCCI-YUN 8pcs TT Motoren
Mecanum-Radsatz 80mm
TB6612FNG Motor Driver
INA3221 3-Kanal Sensor
EVE INR18650-25P
3S Lademodul USB-C 4A
Load Sharing Components
TP4056 Lademodule
MicroSD Modul
16GB MicroSD
3S 10A Li-Ion Batterieschutzplatine
18650 Batteriehalter
ADS1115 16-Bit ADC
TCA9548A I2C Multiplexer
VL53L0X
TM1637 LED-Anzeigemodul
TT-Motoren 4er Set
Raspberry Pi 4B 8GB
ESP32
USB-Kameras (1080p)
Displays (10", 5")
9g Servos
3D-Drucker
Xbox Controller
Verkabelung / Jumper

Systemarchitektur

- Steuer- und Wahrnehmungsebene: Raspberry Pi 4B führt CV, Benutzer-Interface und Telemetrie zusammen; USB-Kameras sind direkt am Pi angeschlossen.
- BMS- und Telemetrieebene: ESP32 sammelt INA3221-Messdaten und loggt auf MicroSD; ESP32 stellt Telemetrie per WiFi/Serial zur Verfügung.
- Motorsteuerung: TB6612FNG-Module erhalten PWM/DIR-Signale von Pi oder MCU zur Ansteuerung der DC-Motoren, Motorstromversorgung über die Akku-/Power-Ebene.
- Sensorbus: INA3221, ADS1115 und VL53L0X sind per I2C angebunden; bei Adresskonflikten kann ein I2C-Multiplexer eingesetzt werden.
- Energie- und Ladeebene: 3S-Akku, Batterieschutzplatine und Lademodule versorgen Motor- und Elektronikspannungen; Load-Sharing-Hardware steuert Ladebetrieb und Versorgung.

Kommunikation und Bedienung

- Xbox-Controller (Bluetooth/USB) oder Smartphone-App für manuelle Steuerung

- WiFi-Interface (über Pi oder ESP32) für Telemetrie, Web-Dashboard und OTA

t Systems (BMS). Budgetziel: < 100€.

Kernentscheidungen
- Antrieb: Mecanum-Räder (omnidirektional)
- Motor-Treiber: TB6612FNG
- Batterie-Monitoring: INA3221 (3-Kanal)
- Batterie: 3S (11.1 V)
- Steuerung: Raspberry Pi 4B (bereits vorhanden) + ESP32 für BMS

Bestandsüberischt
Bereits vorhanden (vorhanden)
- Raspberry Pi 4B 8GB
- ESP32 (mehrere)
- USB-Kameras (2x 1080p)
- Displays (10", 5")
- 9g Servos (2x)
- 3D-Drucker
- Xbox Controller
- Verkabelung/Jumper
- TB6612FNG Motor Driver (3)
- INA3221 3-Kanal Sensor (2)
- TP4056 Lademodule (10)
- TT-Motoren 4er Set (1)
- 3S USB-C Lademodule (3)
- 3S Batterieschutzplatinen (2)
- 18650 Batteriehalter (3)
- ADS1115 ADC (2)
- TCA9548A I2C-Multiplexer (3)
- VL53L0X Abstandssensor (1)
- TM1637 LED-Display (1)
- Mecanum-Räder 80 mm (Set) — erforderlich für omnidirektionales Fahren
- 3x 18650-Zellen (für 3S-Pack) — Batterien fehlen
- Load-Sharing-Bauteile (IRF4905 P‑MOSFET, 1N5819 Schottky, 10 kΩ Widerstände, Perfboard)


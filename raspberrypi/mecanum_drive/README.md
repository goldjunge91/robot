# Mecanum Drive Controller (ESP32/Arduino)

Dieses Beispiel zeigt, wie vier TT-Motoren mit zwei TB6612FNG-Treibern als Mecanum-Antrieb gesteuert werden können. Die Klasse `MecanumDriver` berechnet die erforderlichen Raddrehzahlen aus linearer und rotatorischer Geschwindigkeit und erzeugt PWM/DIR-Signale für jeden Motor.

## Nutzung

1. **Verdrahtung**
   - Jeder TB6612FNG steuert zwei Motoren. Für jeden Motor werden die Pins `IN1`, `IN2` und `PWM` benötigt.
   - Trage die passenden GPIO-Pins deines ESP32 in die `MotorPins`-Strukturen im Beispiel ein.

2. **Kompilierung**
   - Lade die Dateien in deine Arduino- oder PlatformIO-Umgebung.
   - Ersetze ggf. die Stub-Funktionen durch die echten Implementierungen aus `Arduino.h`.

3. **Beispiel**
   - Die Datei `example.cpp` zeigt eine minimale Verwendung der Klasse. In einer echten Anwendung würdest du `drive(vx, vy, omega)` z.B. aus einer Steuerloop oder über ein Kommando aufrufen.

## Formel
Die Raddrehzahlen werden nach dem ülichen Mecanum-Schema berechnet:

```
fl = vx - vy - (L+W) * omega
fr = vx + vy + (L+W) * omega
rl = vx + vy - (L+W) * omega
rr = vx - vy + (L+W) * omega
```

`L` und `W` sind dabei Länge und Breite des Roboters, `omega` ist die Rotationsgeschwindigkeit um die Hochachse.


# Mecanum Drive Controller

Dieser Ordner enthält Beispielcode für einen Arduino/ESP32, der vier TT-Motoren mit Mecanum-Rädern über TB6612FNG-Treiber ansteuert.

Der Sketch `mecanum_drive.ino` erwartet Geschwindigkeitseingaben über die serielle Schnittstelle im Format:
```
vx vy omega\n
```
- `vx` vorwärts/rückwärts [m/s]
- `vy` seitwärts [m/s]
- `omega` Rotation um die Hochachse [rad/s]

Die Kinematik berechnet daraus die Drehzahl für jedes Rad und setzt die PWM-Signale entsprechend.

> Hinweis: Die Pins sind als Platzhalter gewählt und müssen an die tatsächliche Verdrahtung angepasst werden.

## Dateien
- `mecanum_drive.ino` – Arduino/ESP32-Sketch

## Integration
1. Sketch auf Mikrocontroller laden.
2. Serielle Schnittstelle vom Raspberry Pi aus verwenden, um `vx vy omega` zu senden (z.B. über ROS2 Node).
3. TB6612FNG-Module mit den in `mecanum_drive.ino` definierten Pins verbinden.
4. `STBY`-Pins der Treiber dauerhaft auf HIGH legen oder über einen digitalen Pin steuern.

Damit ersetzt der Sketch das bisher verwendete `diffdrive_arduino`-Setup und ermöglicht eine vollständig omnidirektionale Steuerung mit Mecanum-Rädern.

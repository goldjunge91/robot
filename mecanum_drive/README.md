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

## Hinweis
Diese Dateien ersetzen **nicht** den bestehenden Code im Repository, sondern liefern eine Vorlage für einen Mecanum-Antrieb. Die diffdrive-Logik kann damit später ersetzt oder ergänzt werden.


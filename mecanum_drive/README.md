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

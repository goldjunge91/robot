# Teleoperation — schnelle Anleitung (Deutsch)

Dieses Dokument beschreibt kurz und praxisnah, wie du das Paket `robot` per Gamepad/Controller steuerst. Die Anleitung geht davon aus, dass dein ROS2‑Workspace gebaut ist und du ihn gesourct hast.

## Voraussetzungen
- ROS2 (passende Distribution für dieses Repo) installiert
- Workspace gebaut: `colcon build`
- Workspace sourcen (Beispiel WSL/Bash):

  ```bash
  source install/setup.bash
  ```

- Controller verbunden (USB oder Bluetooth)
- Pakete: `joy` und `teleop_twist_joy` installiert (sonst per apt installieren)

## Kurzüberblick
1) Launchfile starten (joy + teleop):

   ```bash
   ros2 launch robot joystick.launch.py
   ```

   Das Launchfile lädt Parameter aus `config/` (z. B. `joystick.yaml`, `xbox_elite_config.yaml`).

2) Joy‑Daten prüfen:

   ```bash
   ros2 topic echo /joy
   ```

   Bewege Sticks und drücke Tasten — du solltest sensor_msgs/Joy‑Nachrichten sehen.

3) Prüfen, ob Teleop /cmd_vel erzeugt:

   ```bash
   ros2 topic echo /cmd_vel
   ```

4) Manueller Start (falls Launchfile nicht verwendet wird):

   ```bash
   ros2 run joy joy_node
   ros2 run teleop_twist_joy teleop_node --ros-args -p <param>=<value>
   ```

5) Integration prüfen
- Vergewissere dich, dass ein Node in diesem Repo (z. B. `tb6612_bridge.py`, `motor.py`) `/cmd_vel` abonniert und die Twist → Motor‑Kommandos umsetzt.
- Falls nicht vorhanden: einen Subscriber schreiben, der Twist in Raddrehzahlen bzw. Motorkommandos umwandelt.

## Troubleshooting (häufig)
- Controller nicht sichtbar: unter Linux `ls /dev/input` prüfen oder `evtest` verwenden.
- Keine `/cmd_vel`: Teleop nicht gestartet oder Achsen/Tasten‑Mapping in `config/joystick.yaml` anpassen.
- Axis/Button Mapping anpassen: `config/xbox_elite_config.yaml` oder `config/joystick.yaml` editieren.

## Sichere Tests
- Roboter vor echten Fahrtests aufbocken (Räder in der Luft), dann mit niedrigen Geschwindigkeiten testen.

## Weiteres
- Wenn du möchtest, erstelle ich eine auf deinen Controller zugeschnittene `joystick.yaml` (z. B. für Xbox Elite) mit korrekten Axis/Button Indizes.
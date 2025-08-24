# ros2_control — Roboter fahren (Deutsch)

Kurz: dieses Dokument erklärt, wie `ros2_control` mit dem lokalen Hardware‑Interface (z. B. Arduino / serieller Motorcontroller) verbunden wird und wie du den Roboter sicher per Teleop/Controller fährst.

Voraussetzungen
- Workspace gebaut: `colcon build`
- Workspace sourcen (Beispiel WSL/Bash):

  ```bash
  source install/setup.bash
  ```

- `ros2_control` und `ros2_controllers` installiert (auf dem Rechner, der die Controller/Hardware laufen lässt)
- Hardware‑Interface (Plugin) vorhanden: in diesem Repo heißt das z. B. `diff_drive_arduino` oder es gibt alternative Bridges in `raspberrypi/` bzw. `tb6612_bridge.py`.

1) URDF / ros2_control Block prüfen
- Öffne die URDF (`description/robot.urdf.xacro` oder ähnlich) und finde den `<ros2_control>` Block.
- Achte auf das aktivierte Plugin (z. B. `diff_drive_arduino/diff_drive_arduino`) und die Parametrierung (Serial Port, Baudrate, encoder_counts, wheel_radius, wheel_separation, timeouts).

2) Launchfile verwenden
- Nutze das vorhandene Launchfile `launch/launch_robot.launch.py` (oder `launch/launch_sim.launch.py` für Gazebo). Beispiel starten:

  ```bash
  ros2 launch robot launch_robot.launch.py
  ```

  Das Launchfile startet `robot_state_publisher`, den `ros2_control_node` (ControllerManager) und die Spawner für `diff_drive_controller` und `joint_state_broadcaster`.

3) Controller‑Parameter prüfen
- Konfigurationsdatei: `config/my_controllers.yaml` oder `config/mycontrollers.yaml` (Name im Launchfile prüfen)
- Wichtige Parameter:
  - Verwendung von non‑sim time auf dem realen Robot: `use_sim_time: false`
  - Controller‑Konfiguration (diff_drive_controller): wheel_radius, wheel_separation, topic‑Remappings

4) Teleop (Controller) → cmd_vel
- Starte Teleop wie in `Teleoperation.md` beschrieben (Launchfile `joystick.launch.py`), prüfe `/cmd_vel`.
- Remappings: Falls deine ControllerManager/Controller `cmd_vel_unstamped` oder einen anderen Topic‑Namen erwartet, remappe z. B. `cmd_vel` → `cmd_vel_unstamped` im Launchfile oder beim Teleop.

5) Sicherheitstest (wichtig)
- Prop den Roboter auf (Räder frei drehbar) und teste mit kleinen Geschwindigkeiten.
- Prüfe Encoder‑Feedback: `ros2 topic echo /joint_states` und visualisiere Model in RViz (`config/main.rviz`).

6) Fehleranalyse & Tuning
- Odometry drift / inkorrekte Distanz:
  - Überprüfe `encoder_counts_per_rev` und `wheel_radius` in deinem Hardware‑Interface / URDF.
  - Fahre eine gemessene Strecke (z. B. 1 m) und korrigiere wheel_radius falls nötig.
- Drehungen nicht genau:
  - Korrigiere `wheel_separation`
- Encoder nicht korrekt:
  - Prüfe serielle Kommunikation (baudrate, timeout) und den Hardware‑Interface Code (`arduino/` Beispiele im Repo).

7) Simulation ↔ Real Robot
- In der URDF/Launchfiles ist üblicherweise ein Schalter/Argument (`sim_mode` / `use_sim_time`) eingebaut, um zwischen Gazebo (sim) und realer Hardware zu wechseln.
- Beim Test in Gazebo aktiviere `use_sim_time: true` und lade die Gazebo‑ros2_control Plugins; für realen Betrieb `use_sim_time: false`.

Kurz‑Checklist zum Fahren mit Controller
- Workspace sourcen
- `ros2 launch robot launch_robot.launch.py` (ControllerManager + Spawner laufen)
- `ros2 launch robot joystick.launch.py` (joy + teleop)
- `ros2 topic echo /cmd_vel` prüfen
- Roboter aufbocken, sicher testen, dann am Boden testen

Wenn du möchtest, mache ich:
- eine kurze, getestete `config/joystick.yaml` für deinen speziellen Controller (z. B. Xbox Elite)
- einen kleinen Check‑Script, das per Topic‑Echo prüft, ob `/joy`, `/cmd_vel` und `/joint_states` korrekt laufen

---

Anmerkung: Ich habe die langen Video‑Transkripte hier durch prägnante, handlungsorientierte Schritte ersetzt — sag Bescheid, falls du mehr Details zur Serial‑Plugin‑Installation oder Beispiel‑paramsets brauchst.
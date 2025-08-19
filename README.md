# Robot Package

Dies ist ein ROS 2 Robot-Paket. Bitte passe den Namen an, falls du das Paket umbenennst (alle Vorkommen von `robot` ersetzen).

---

## Projektstruktur

```txt
dev_ws_robot/
├── build/           # Von colcon generierte temporäre Build-Dateien
│   ├── .built_by        # Marker-Datei für den Build-Prozess
│   ├── COLCON_IGNORE    # Verhindert, dass colcon dieses Verzeichnis erneut baut
│   └── robot/           # Build-Artefakte für das Paket "robot"
├── install/         # Installierte Artefakte nach dem Build
│   ├── setup.bash       # Setup-Skript für ROS 2 Umgebung (bash)
│   ├── setup.ps1        # Setup-Skript für PowerShell
│   ├── setup.sh         # Setup-Skript für sh
│   ├── setup.zsh        # Setup-Skript für zsh
│   ├── local_setup.*    # Lokale Setup-Skripte für verschiedene Shells
│   ├── COLCON_IGNORE    # Siehe oben
│   └── robot/           # Installierte Dateien des Pakets "robot"
├── log/             # Build- und Ausführungslogs
│   ├── COLCON_IGNORE    # Siehe oben
│   └── build_*/         # Einzelne Build-Logs mit Zeitstempel
└── src/             # Quellcode-Verzeichnis für ROS 2 Pakete
    └── robot/           # Dein ROS 2 Paket "robot"
```

**Kurze Beschreibung der wichtigsten Ordner:**

- **.vscode/**  
  Enthält Einstellungen für Visual Studio Code, z.B. für Python-Interpreter, ROS-Plugins oder Formatierung.

- **build/**  
  Temporäre Build-Artefakte, die von colcon beim Kompilieren erzeugt werden. Kann bei Problemen gelöscht werden (`colcon build` erstellt sie neu).

- **install/**  
  Enthält die ausführbaren Dateien, Setupscripte und installierten ROS 2 Pakete nach dem Build. Wird ebenfalls von colcon verwaltet.

- **log/**  
  Speichert Logdateien von Build- und Ausführungsvorgängen. Nützlich zur Fehlersuche.

- **src/**  
  Hier liegen alle ROS 2 Pakete deines Workspaces.  
  - **robot/**  
    Dein zentrales ROS 2 Paket. Hier befinden sich Quellcode, Launchfiles, Konfigurationen, URDF/Xacro-Dateien, Nodes usw.

> **Hinweis:** Die Ordner `build/`, `install/` und `log/` werden automatisch erzeugt und sollten nicht in die Versionskontrolle (z.B. git) aufgenommen werden.  

---

## Vorbereitung & Installation

### WSL2: USB-Controller binden

```sh
# Als Admin in Windows PowerShell:
usbipd bind --busid 1-1
```

### Notwendige Pakete installieren

```sh
sudo apt install ros-<ROS-DISTRO>-gazebo-ros-pkgs
```

Ersetze `<ROS-DISTRO>` z.B. durch `humble`.

---

## Build & Start

```sh
colcon build --symlink-install
source install/setup.bash
```


### Starten der Simulation

1. Terminal öffnen (`wsl -d Ubuntu-22.04`)
2. ROS2 Launch starten:
    - `ros2 launch robot rsp.launch.py`
    - `rviz2` (optional: `rviz2 -d src/robot/config/view_robot.rviz`)
    - `ros2 run joint_state_publisher_gui joint_state_publisher_gui`

#### Simulation aktivieren

```sh
ros2 launch robot rsp.launch.py use_sim_time:=true
ros2 launch gazebo_ros gazebo.launch.py
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity robot
ros2 launch robot launch_sim.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

- ros2 launch robot rsp.launch.py use_sim_time:=true // wie man prüft ob die simulation erfolgreich gestartet wurde  'ros2 param get /robot_state_publisher use_sim_time' Boolean value is: True
ros2 launch gazebo_ros gazebo.launch.py
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity robot
- ros2 launch robot launch_sim.launch.py
- ros2 run teleop_twist_keyboard teleop_twist_keyboard

#### Andere Welt laden

```sh
ros2 launch robot launch_sim.launch.py world:=src/robot/worlds/obstacles.world
ros2 launch robot launch_sim.launch.py world:=$(pwd)/src/robot/worlds/obstacles.world
```

---

## Troubleshooting

- Prüfe die Geschwindigkeiten auf `/cmd_vel`:
  ```sh
  ros2 topic echo /cmd_vel
  ```
- Für Joystick-Steuerung:
  - `teleop_twist_joy` (Node: `teleop_node`)
  - `joy` (Node: `joy_node`)

---


teleop_twist_joy -- teleop_node
joy --- joy_node

## How to build WSL2 Kernel
https://blog.thetechcorner.sk/posts/Update-WSL2-kernel-to-6-6-x/
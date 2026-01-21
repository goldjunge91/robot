# Robot Package

Dies ist ein ROS 2 Robot-Paket. Bitte passe den Namen an, falls du das Paket umbenennst (alle Vorkommen von `robot` ersetzen).

---

## Kurzübersicht

Dieses Repository enthält ein ROS 2-Paket `robot` mit Launchfiles, URDF/Xacro-Dateien, Konfigurationen für Gazebo und RViz, sowie Hilfsdokumentation. Diese README ist so strukturiert, dass du schnell Installation, Aufbau, Start und Troubleshooting findest.

Wenn du das Paket umbenennst: ersetze alle Vorkommen von `robot`.

## Inhalt / Projektstruktur

```txt
dev_ws_robot/
src/
└── robot/
    ├── CMakeLists.txt         # Build-Konfiguration für das ROS 2 Paket
    ├── LICENSE.md             # Lizenzinformationen
    ├── package.xml            # Paketbeschreibung und Abhängigkeiten
    ├── README.md              # Dokumentation zum Paket
    ├── config/                # Konfigurationsdateien (z.B. RViz, Joystick, Parameter)
    │   ├── drive_robot_gazebo_rviz.rviz
    │   ├── empty.yaml
    │   ├── view_robot.rviz
    │   └── xbox_elite_config.yaml
    ├── description/           # Roboterbeschreibung (URDF/Xacro-Dateien)
    │   ├── gazebo_control.xacro
    │   ├── inertial_macros.xacro
    │   ├── robot_core.xacro
    │   └── robot.urdf.xacro
    ├── launch/                # Launchfiles zum Starten von Simulation und Nodes
    │   ├── launch_sim.launch.py
    │   └── rsp.launch.py
    └── worlds/                # Gazebo-Welten für die Simulation
        ├── empty.world
        └── obstacles.world
```

Kurze Beschreibung wichtiger Ordner:

- `.vscode/` – VS Code Einstellungen.
- `build/` – temporäre Build-Artefakte von `colcon`.
- `install/` – installierte Artefakte nach Build.
- `log/` – Logs von Build/Runtime.
- `src/` – Quellpakete; `robot/` ist das Paket in diesem Repo.

Hinweis: `build/`, `install/` und `log/` werden automatisch erzeugt und sollten nicht in die Versionskontrolle aufgenommen werden.

---

## Schnellstart: Initiale Installation (Remote PC und Raspberry Pi)

Diese Sektion fasst die ersten Schritte zusammen, um ein System entweder auf einem Remote-PC (Desktop/Server) oder einem Raspberry Pi vorzubereiten.

### Remote PC (Ubuntu / WSL2)

1. Systemabhängigkeiten installieren (ersetze `<ROS-DISTRO>` durch z.B. `humble`):

```sh
sudo apt update
sudo apt install -y ros-<ROS-DISTRO>-gazebo-ros-pkgs
sudo apt install -y ros-<ROS-DISTRO>-ros2-control ros-<ROS-DISTRO>-ros2-controllers ros-<ROS-DISTRO>-gazebo-ros2-control
sudo apt install -y ros-<ROS-DISTRO>-xacro ros-<ROS-DISTRO>-joint-state-publisher-gui
```

2. Optional / nützlich:

```sh
sudo apt install -y joystick jstest-gtk evtest
sudo apt install -y python3-colcon-common-extensions
sudo apt install -y ros-<ROS-DISTRO>-twist-mux ros-<ROS-DISTRO>-urdf ros-<ROS-DISTRO>-urdf-tutorial
```

3. (WSL2) USB-Controller binden (in Windows PowerShell als Admin):

```sh
usbipd bind --busid 1-1
```

4. Workspace bauen und sourcen:

```sh
source /opt/ros/<ROS-DISTRO>/setup.bash
source install/setup.bash || true
colcon build --symlink-install
```

5. Hinweis: Web-Video-Server / Web-Tools (optional):

```sh
# Beispiel: web_video_server
git clone -b ros2 https://github.com/RobotWebTools/web_video_server.git
# Nach dem Bauen: ros2 run web_video_server web_video_server
```

### Raspberry Pi

Auf dem Raspberry Pi gelten ähnliche Schritte. Wichtige Checks und Befehle:

```sh
# Prüfen, ob ros2 in PATH ist
which ros2 || echo "ros2 nicht in PATH"
# Prüfen des ROS-Distros
echo $ROS_DISTRO || echo "ROS_DISTRO nicht gesetzt"
# Source ROS (falls nötig)
source /opt/ros/<distro>/setup.bash   # <distro> z.B. humble, iron, usw.
```

Beispielpakete für Pi (optional):

```sh
sudo apt install -y ros-<ROS-DISTRO>-gazebo-* \
  ros-<ROS-DISTRO>-cartographer ros-<ROS-DISTRO>-cartographer-ros \
  ros-<ROS-DISTRO>-navigation2 ros-<ROS-DISTRO>-nav2-bringup
```

---

## Vollständige Paket-Installliste (aus Original-README)

Die folgende Liste stammt aus dem Original-README und ist unverändert erhalten:

```sh
sudo apt install ros-humble-xacro ros-humble-joint-state-publisher-gui
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control
joystick jstest-gtk evtest
sudo apt-get install ros-humble-twist-mux
sudo apt install ros-humble-urdf
sudo apt install ros-humble-joint-state-publisher-gui
sudo apt install ros-humble-urdf-tutorial
sudo apt install ros-humble-urdf-launch
sudo apt install ros-jazzy-rqt
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control
 git clone -b ros2https://github.com/RobotWebTools/web_video_server.git
(https://github.com/RobotWebTools/web_video_server.git)
Rebuild the workspace with colcon
In two different tabs, source the workspace, launch the camera driver (like normal), and run ros2 run web_video_server web_video_server
sudo apt install ros-humble-rosbridge-suite

sudo apt install ros-humble-gazebo-*
sudo apt install ros-humble-cartographer
sudo apt install ros-humble-cartographer-ros
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
cd ~/turtlebot3_ws/src/
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3/turtlebot3_example.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_example.git
sudo apt install python3-colcon-common-extensions
cd ~/turtlebot3_ws

colcon build --symlink-install

source install/setup.bash echo  oder 'source ~/turtlebot3_ws/install/setup.bash' >> ~/.bashrc
das nur wenn nicht direkt gesourced wurde source ~/.bashrc
echo 'export ROS_DOMAIN_ID=30 #TURTLEBOT3' >> ~/.bashrc
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

---

## Build & Start

Standard-Build- und Start-Schritte:

```sh
source /opt/ros/<ROS-DISTRO>/setup.bash
source install/setup.bash
colcon build --symlink-install
```

---

## ROS-Kommandos (kompakte Sammlung)

Alle ROS-/Gazebo-/Controller-Befehle aus dem Original an einem Ort.

- ros2 topic list | zeigt alle topics
- ros2 run joint_state_publisher_gui joint_state_publisher_gui
- rviz2
- rviz2 -d src/robot/config/view_robot.rviz
- ros2 control
- ros2 control list_hardware_interfaces
- ros2 control list_controllers
- ros2 run controller_manager spawner diff_cont
- ros2 run controller_manager spawner joint_broad
- ros2 run controller_manager spawner.py
- ros2 run controller_manager spawner.py diff_cont
- ros2 run controller_manager spawner.py joint_broad
  - Beispiel-Log:
    [INFO] [1755746501.725611869] [spawner_diff_cont]: Loaded diff_cont
    [INFO] [1755746501.840605257] [spawner_diff_cont]: Configured and activated diff_cont
    [INFO] [1755746504.006178285] [spawner_joint_broad]:  Loaded joint_broad
    [INFO] [1755746504.119964744] [spawner_joint_broad]: Configured and activated joint_broad
- ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
- ros2 param list
- ros2 run joy joy_enumerate_devices
- ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
- ros2 topic echo /diff_cont/odom

Simulation / Gazebo / Spawn:

```sh
ros2 launch robot rsp.launch.py
ros2 launch robot rsp.launch.py use_sim_time:=true
ros2 launch gazebo_ros gazebo.launch.py
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity robot
ros2 launch robot launch_sim.launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# Andere Welt laden:
ros2 launch robot launch_sim.launch.py world:=src/robot/worlds/obstacles.world
```

---

## Image / Kamera / Web-Video

Original-Content (vollständig erhalten):

```sh
sudo apt update
sudo apt install -y ros-jazzy-desktop
# oder nur rqt / image-View falls du nur GUI brauchst:
sudo apt install -y ros-jazzy-rqt ros-jazzy-rqt-image-view
sudo apt install -y ros-humble-rqt ros-humble-rqt-image-view

ros2 run rqt_image_view rqt_image_view
ros2 run image_transport list_transports | zeigt alle verschiede format die das system kennt
ros2 run image_transport  republish compressed raw --ros-args -r in/compressed:=/camera/image_raw/compressed -r out:=/camera/image_raw/uncompressed
#ros2-humble-rqt-image-view
#ros2-jazzy-rqt-image-view
```

Web-Video-Server Hinweis (aus Original):

```sh
git clone -b ros2 https://github.com/RobotWebTools/web_video_server.git
# Nach dem Bauen: in zwei Terminal-Tabs workspace sourcen, Kamera starten und dann:
ros2 run web_video_server web_video_server
```

---

## TurtleBot-spezifische Hinweise (aus Original)

Diese Kommandos wurden im Original als Anleitung für TurtleBot-Setups gelistet. Ich lasse sie hier vollständig stehen:

```sh
cd ~/turtlebot3_ws/src/
git clone -b humble https://github.com/ROBOTIS-GIT/DynamixelSDK.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3/turtlebot3_example.git
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_example.git
sudo apt install python3-colcon-common-extensions
cd ~/turtlebot3_ws
colcon build --symlink-install
source install/setup.bash
echo 'export ROS_DOMAIN_ID=30 #TURTLEBOT3' >> ~/.bashrc
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

---

## Raspberry Pi / Checks (aus Original)

Original-Inhalte zur Kontrolle auf dem Pi:

```sh
which ros2 || echo "ros2 nicht in PATH"
/opt/ros/jazzy/bin/ros2
echo $ROS_DISTRO || echo "ROS_DISTRO nicht gesetzt"
jazzy
apt-cache policy ros-jazzy-v4l2-camera
apt-cache madison ros-jazzy-v4l2-camera
source /opt/ros/<distro>/setup.bash   # <distro> z.B. humble, iron, usw.
echo $ROS_DISTRO
```

---

## Troubleshooting

- Prüfe die Geschwindigkeiten auf `/cmd_vel`:

```sh
ros2 topic echo /cmd_vel
```

- Für Joystick-Steuerung (Original):
  - `teleop_twist_joy` (Node: `teleop_node`)
  - `joy` (Node: `joy_node`)

Weitere Originalzeilen, vollständig erhalten:

teleop_twist_joy -- teleop_node
joy --- joy_node

---

## WSL2 Kernel bauen (Original-Link)

https://blog.thetechcorner.sk/posts/Update-WSL2-kernel-to-6-6-x/

---

## Joystick-Konfiguration (`config/joystick.yaml`)

Open the file: config/joystick.yaml

Modify the values for the axes and buttons to match your controller's layout.

Original YAML example (vollständig erhalten):

YAML

teleop_node:
  ros__parameters:
    # --- MOVEMENT ---
    axis_linear:
      x: 1  # Vertical axis of the left stick
    axis_angular:
      yaw: 0 # Horizontal axis of the left stick

    # --- BUTTONS ---
    enable_button: 6 # The "dead-man's switch"
    enable_turbo_button: 7 # The button for faster speeds

You'll need to use a tool like jstest-gtk to find the correct number for each button and axis on your specific controller.

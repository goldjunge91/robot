# initilize 
(only as example too show what i mean)
"on Remote PC"

Terminal 1
```sh
# Install ROS + tools (pick your distro; tries jazzy first, then humble)
sudo apt update
sudo apt install -y ros-jazzy-desktop || sudo apt install -y ros-humble-desktop

# Optional GUI tools (rqt, image view)
sudo apt install -y ros-jazzy-rqt ros-jazzy-rqt-image-view || \
sudo apt install -y ros-humble-rqt ros-humble-rqt-image-view

# Simulation + control stack
sudo apt install -y \
  ros-$ROS_DISTRO-gazebo-ros-pkgs \
  ros-$ROS_DISTRO-gazebo-ros2-control \
  ros-$ROS_DISTRO-ros2-control \
  ros-$ROS_DISTRO-ros2-controllers \
  ros-$ROS_DISTRO-xacro \
  ros-$ROS_DISTRO-teleop-twist-joy \
  ros-$ROS_DISTRO-joy

# Build workspace
cd ~/dev_ws_robot
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## make build an run 
Terminal 2
```sh
# Launch full simulation (gzserver+gzclient, RSP, spawn, controllers)
# Uses mecanum controller defined in config/my_controllers_mecanum.yaml
ros2 launch robot launch_sim.launch.py
# Optional: choose a world
# ros2 launch robot launch_sim.launch.py world:=src/robot/worlds/obstacles.world
```

Alternative: manual spawn (if Gazebo is running and /robot_description is published)
```sh
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity my_bot
```

| command   |   arg1 | value1 | description |  arg2    |  value2  |
|--- |--- |--- |--- |--- |--- |
|  `ros2 run gazebo_ros spawn_entity.py`  |`-topic`    |  `robot_description`  |Spawn entity from URDF on this topic | `-entity`   | `my_bot` |
|    |    |    | Must match robot_state_publisher output   |    |    |

```sh
# (optional) Inspect controllers (mecanum + joint_state_broadcaster)
ros2 control list_controllers
ros2 control list_hardware_interfaces
```

Terminal 3
```sh
# Keyboard teleop (simple)
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# OR Xbox/Joystick teleop (publishes /cmd_vel expected by mecanum controller)
ros2 launch robot joystick_xbox_mecanum_pico.launch.py use_sim_time:=true

# Optional sensors in sim (if desired)
# ros2 launch robot camera.launch.py
# ros2 launch robot rplidar.launch.py
```

"on Robot hardware"

Terminal 1
```sh
cd ~/dev_ws_robot
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Terminal 2
```sh
# Launch hardware stack: URDF (ros2_control disabled), bridge, camera
ros2 launch robot launch_robot_pi.launch.py

# Optional: set the bridge cmd topic explicitly
# ros2 launch robot launch_robot_pi.launch.py cmd_topic:=/diff_cont/cmd_vel_unstamped
```

| command   |   arg1 | value1 |  arg2    |  value2  |
|--- |--- |--- |--- |--- |
|  `ros2 launch robot launch_robot_pi.launch.py`  | `cmd_topic`   |  `/cmd_vel` (default)  |    |     |
|    |    | Bridge subscribes here and sends to Arduino (TB6612)   |    |    |

Terminal 3
```sh
# Send velocity commands
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# OR controller-based teleop (joystick + teleop_twist_joy)
ros2 launch robot joystick_xbox_mecanum_pico.launch.py

# Optional sensors on hardware
# ros2 launch robot camera.launch.py
# ros2 launch robot rplidar.launch.py
```

Notes
- Package name: `robot`; simulation spawns entity `my_bot` (as in `launch_sim.launch.py`).
- Mecanum controller: topic `cmd_vel` (unstamped) per `config/my_controllers_mecanum.yaml`.
- RViz example: `rviz2 -d src/robot/config/view_robot.rviz`.
- If joystick isn’t detected: verify `/dev/input/js0` permissions; install `joystick jstest-gtk` and test with `jstest-gtk`.

Advanced
- Minimal ros2_control demo (diff drive variant): `ros2 launch robot launch_robot.launch.py`
  - Controllers: `diff_cont`, `joint_broad` (see `config/my_controllers.yaml`).
  - Useful for testing controller_manager separate from Gazebo.

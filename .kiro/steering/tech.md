# Technology Stack

## Core Framework
- **ROS 2 Humble/Jazzy**: Primary robotics framework
- **Build System**: ament_cmake (CMake-based ROS 2 build system)
- **Package Manager**: colcon for workspace building

## Programming Languages
- **C++**: Arduino firmware, ROS 2 nodes, and hardware interfaces
- **Python**: Launch files, ROS 2 nodes, and utility scripts
- **URDF/Xacro**: Robot description and simulation models

## Simulation & Visualization
- **Gazebo**: Physics simulation environment
- **RViz2**: Robot visualization and debugging
- **ros2_control**: Hardware abstraction and controller framework
- **Gazebo ROS 2 Control**: Simulation integration

## Hardware Integration
- **Arduino**: Motor control firmware (SparkFun TB6612FNG library)
- **Serial Communication**: Arduino-ROS bridge via USB/UART
- **I2C Sensors**: INA3221, ADS1115, VL53L0X integration

## Control Systems
- **ros2_controllers**: Differential drive and joint state controllers
- **twist_mux**: Command velocity multiplexing
- **teleop_twist_keyboard**: Keyboard teleoperation
- **joy/teleop_twist_joy**: Joystick control integration

## Common Commands

### Build & Setup
```bash
# Source ROS 2 environment
source /opt/ros/humble/setup.bash
source install/setup.bash

# Build workspace
colcon build --symlink-install

# Clean build (if needed)
rm -rf build/ install/ log/
```

### Simulation
```bash
# Launch robot description
ros2 launch robot rsp.launch.py

# Start simulation
ros2 launch robot launch_sim.launch.py

# Alternative world
ros2 launch robot launch_sim.launch.py world:=src/robot/worlds/obstacles.world
```

### Hardware Control
```bash
# Spawn controllers
ros2 run controller_manager spawner diff_cont
ros2 run controller_manager spawner joint_broad

# Manual control
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
```

### Debugging
```bash
# List topics and controllers
ros2 topic list
ros2 control list_controllers
ros2 control list_hardware_interfaces

# Monitor data
ros2 topic echo /diff_cont/odom
ros2 topic echo /cmd_vel
```

## Dependencies
Key ROS 2 packages that must be installed:
- `ros-humble-gazebo-ros-pkgs`
- `ros-humble-ros2-control`
- `ros-humble-ros2-controllers` 
- `ros-humble-gazebo-ros2-control`
- `ros-humble-twist-mux`
- `ros-humble-xacro`
- `ros-humble-joint-state-publisher-gui`
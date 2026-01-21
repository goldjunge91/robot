# Project Structure

## Root Level Organization

```
robot/                          # Main ROS 2 package
├── CMakeLists.txt             # Build configuration
├── package.xml                # Package metadata and dependencies
├── config/                    # Configuration files
├── description/               # Robot URDF/Xacro models
├── launch/                    # Launch files
├── worlds/                    # Gazebo simulation worlds
├── arduino/                   # Arduino firmware
├── raspberrypi/              # Raspberry Pi specific code
├── docs/                     # Documentation and PDFs
└── serial/                   # Serial communication library
```

## Key Directories

### `/config/`
Configuration files for various components:
- `*.rviz` - RViz visualization configurations
- `*.yaml` - Parameter files for controllers, joystick, twist_mux
- Controller configurations (my_controllers.yaml, gaz_ros2_ctl_use_sim.yaml)

### `/description/`
Robot model definitions using URDF/Xacro:
- `robot.urdf.xacro` - Main robot description file
- `robot_core.xacro` - Core robot structure
- `ros2_control.xacro` - Hardware interface definitions
- `gazebo_control.xacro` - Gazebo-specific control
- Sensor definitions: `camera.xacro`, `lidar.xacro`, `depth_camera.xacro`
- `inertial_macros.xacro` - Reusable inertial calculations

### `/launch/`
Python launch files for different scenarios:
- `launch_sim.launch.py` - Complete simulation setup
- `rsp.launch.py` - Robot state publisher
- `joystick.launch.py` - Joystick control setup
- `camera.launch.py` - Camera nodes
- Platform-specific: `launch_robot_pi.launch.py`

### `/arduino/`
Arduino firmware and libraries:
- `robot_core/` - Main motor control firmware
  - `robot_core.ino` - Main Arduino sketch
  - `robot_core_config.h` - Pin and configuration definitions
- `MotorTestRun/` - Motor testing utilities

### `/raspberrypi/`
Raspberry Pi specific implementations:
- `robot_bridge/` - ROS 2 package for Arduino communication
- `mecanum_drive/` - Mecanum wheel drive algorithms
- `tb6612_bridge.py` - Motor driver bridge

## File Naming Conventions

### Launch Files
- Use descriptive names: `launch_sim.launch.py`, `launch_robot_pi.launch.py`
- Include platform suffix when platform-specific
- Always use `.launch.py` extension for Python launch files

### Configuration Files
- Use component name + purpose: `my_controllers.yaml`, `joystick.yaml`
- RViz configs: `<purpose>.rviz` (e.g., `view_robot.rviz`)
- Parameter files: `<component>_params.yaml`

### URDF/Xacro Files
- Main robot file: `robot.urdf.xacro`
- Component files: `<component>.xacro` (e.g., `camera.xacro`, `lidar.xacro`)
- Macro files: `<purpose>_macros.xacro`

## Package Dependencies

The project follows ROS 2 package structure with:
- Build dependencies in `package.xml`
- Install targets in `CMakeLists.txt` for config, description, launch, worlds directories
- Proper sourcing order: ROS 2 → workspace → package-specific

## Development Workflow

1. **Simulation Development**: Work in `/description/`, `/config/`, `/launch/`
2. **Hardware Integration**: Develop in `/arduino/`, `/raspberrypi/`
3. **Testing**: Use `/worlds/` for different simulation scenarios
4. **Documentation**: Update `/docs/` with findings and procedures

## Important Notes

- Package name "robot" should be changed if renaming the project
- All launch files must update `package_name` variable when renaming
- The `diffdrive_arduino-main/` directory contains reference implementation
- Build artifacts (`build/`, `install/`, `log/`) are auto-generated and git-ignored
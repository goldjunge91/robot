# GEMINI.md

## Project Overview

This is a ROS 2 project for a mobile robot. The project is named "robot" and is based on the `ament_cmake` build system. It includes launch files, URDF/Xacro files for the robot description, configuration files for Gazebo and RViz, and Gazebo worlds for simulation.

The robot is a four-wheeled omnidirectional platform, likely using mecanum wheels, and is equipped with a camera and a lidar. The control system appears to be set up using `ros2_control` and includes a `diff_drive_controller`.

The repository also contains code for a Raspberry Pi, suggesting a hardware counterpart to the simulated robot.

## Building and Running

### Prerequisites

- ROS 2 (Humble or newer)
- Gazebo
- `ros2_control` and related packages
- `colcon`

### Building the Workspace

1. Source your ROS 2 installation:

    ```bash
    source /opt/ros/<ROS-DISTRO>/setup.bash
    ```

2. Build the workspace using `colcon`:

    ```bash
    colcon build --symlink-install
    ```

### Running the Simulation

1. Source the workspace:

    ```bash
    source install/setup.bash
    ```

2. Launch the simulation:

    ```bash
    ros2 launch robot launch_sim.launch.py
    ```

    To load a different world, use the `world` argument:

    ```bash
    ros2 launch robot launch_sim.launch.py world:=src/robot/worlds/obstacles.world
    ```

### Running on the Raspberry Pi

The `raspberrypi` directory contains code for the robot's hardware. The `README.md` in that directory likely contains instructions for setting up and running the code on the Raspberry Pi.

## Development Conventions

- The project uses `ament_cmake` as the build system.
- The robot's description is written in URDF/Xacro files.
- Launch files are written in Python.
- Configuration files are written in YAML.
- The project includes a `.gitignore` file, which should be respected.
- The `specs` directory contains design documents and specifications.
- The `.github` directory contains prompts for an AI agent, which suggests that AI-assisted development is being used.

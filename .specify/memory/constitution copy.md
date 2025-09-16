# Robot Project Constitution (ROS 2)

## Core Principles

### I. Buildable & Launchable

- All functionality ships as ROS2 nodes with clear topics/services; launch files must start subsystems independently; use standard message types when available.
- The workspace builds cleanly with colcon for all packages under `src/`.
- Provide runnable launch files. For this repo: `launch_sim.launch.py`, `rsp.launch.py`, and `launch_robot.launch.py` must run without exceptions.
- URDF/Xacro in `description/` parses without errors; TF tree loads; Gazebo worlds from `worlds/` load via launch.

### II. Minimal Tests (must exist)

- At least one automated test per package (C++: `ament_cmake_gtest`; Python: `ament_pytest`).
- `colcon test` passes locally and in CI before merge.

### III. Parameters over Hard‑coding

- Tunables live in `config/*.yaml`. Nodes declare parameters and read from YAML (topic names, frame IDs, gains, ports).
- Launch files expose common args (e.g., `use_sim_time`, `world`, `robot_description` source, controller config path).

### IV. Code Quality Baseline

- Enable ament linters. C++: `ament_lint_auto` (cpplint/cppcheck); Python: `flake8` (and prefer `black`/`isort`).
- Lint runs as part of tests: `colcon test --ctest-args -R lint` should succeed.

### V. Observability & Interfaces

- Use ROS 2 logging (`rclcpp`/`rclpy`) with proper levels; avoid bare prints in runtime paths.
- Document topics/services/actions/TF frames in `README.md`. Keep names stable; breaking changes require a version bump and note.

## Working Constraints

- Target: ROS 2 Humble (or newer). Simulation via Gazebo with `ros2_control` using configs in `config/` and `description/`.
- All deps declared in `package.xml`; build logic only in `CMakeLists.txt`/`setup.py`.
- Hardware/sim parity: same node graph should run in sim and on hardware (Raspberry Pi/Pico bridge) via launch args and YAML.

## Minimum Hardware & Software Stack

- Chassis: 4 DC geared motors with encoders, 80 mm mecanum wheels, TB6612FNG drivers
- Compute: Raspberry Pi 4B (8 GB) on Ubuntu + ROS2; Raspberry Pi Pico for deterministic PWM/servo loops
- Sensors: LDS01RR LiDAR, ICM-20948 IMU, VL53L0X ToF, 1080p USB camera
- Launcher: dual RS2205 brushless flywheels with 40 A ESCs, two-axis servo gimbal
- Power & Display: 3S Li-Ion pack with BMS, INA3221 current monitor, TM1637 status display

### Split High/Low Control

Raspberry Pi 4B runs perception, navigation, web UI and teleop; Raspberry Pi Pico executes all real-time motor and launcher control; communication stays in Twist/actuator commands with watchdogs for safe fallback.

### Reliable Navigation Stack

Fuse LDS01RR LiDAR, ICM-20948 IMU and wheel encoders for SLAM/localization; VL53L0X provides near-field obstacle checks; the robot must boot into mapping or localization modes and degrade safely if a sensor fails.

## Development Workflow & Quality Gates

- Before merge to default branch:

 1) Build: `colcon build --symlink-install` succeeds.
 2) Tests: `colcon test` green; at least one test per package.
 3) Lint: ament linters pass.
 4) Smoke launch: run `launch_sim.launch.py` headless; verify no exceptions and controllers spawn.

- Versioning: semantic via `package.xml`. Interface changes (topics/services/params) bump MINOR; breaking changes bump MAJOR.
- Docs: `README.md` shows build/source/launch commands and lists primary topics/frames.

## Governance

- This Constitution supersedes ad‑hoc practices. Changes require a PR updating this file; include migration notes when interfaces change.
- Reviewers verify compliance with the gates; exceptions are rare and must be justified in the PR.

**Version**: 0.1.0 | **Ratified**: 2025-09-16 | **Last Amended**: 2025-09-16

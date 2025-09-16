# OmniROS Project Constitution

## Core Principles

### ROS2 Modular Nodes

All functionality ships as ROS2 nodes with clear topics/services; launch files must start subsystems independently; use standard message types when available.

### Split High/Low Control

Raspberry Pi 4B runs perception, navigation, web UI and teleop; Raspberry Pi Pico executes all real-time motor and launcher control; communication stays in Twist/actuator commands with watchdogs for safe fallback.

### Reliable Navigation Stack

Fuse LDS01RR LiDAR, ICM-20948 IMU and wheel encoders for SLAM/localization; VL53L0X provides near-field obstacle checks; the robot must boot into mapping or localization modes and degrade safely if a sensor fails.

### Safe Launcher Handling

Face-tracking and firing engage only after manual arm; ESCs/servos halt on lost target, estop or watchdog timeout; servo limits and ESC spin-up run at every boot.

### Continuous Telemetry

Publish battery data (INA3221), camera stream and key diagnostics to the dashboard; Xbox controller override remains available and overrides autonomy.

## Minimum Hardware & Software Stack

- Chassis: 4 DC geared motors with encoders, 80 mm mecanum wheels, TB6612FNG drivers
- Compute: Raspberry Pi 4B (8 GB) on Ubuntu + ROS2; Raspberry Pi Pico for deterministic PWM/servo loops
- Sensors: LDS01RR LiDAR, ICM-20948 IMU, VL53L0X ToF, 1080p USB camera
- Launcher: dual RS2205 brushless flywheels with 40 A ESCs, two-axis servo gimbal
- Power & Display: 3S Li-Ion pack with BMS, INA3221 current monitor, TM1637 status display

## Workflow Minimums

- Supply simulation or recorded data tests for new navigation or launcher code before hardware trials
- Document each node with expected interfaces and a bench test recipe
- Capture a validation run after changing kinematics, control loops or safety logic
- Check launcher arm switch, estop and watchdog behaviour before every live-fire session

## Governance

This constitution defines the minimum platform and process; any deviations require documented approval; reviewers confirm compliance during code and hardware reviews; keep runtime guidance documents aligned with this baseline.

**Version**: 0.2.0 | **Ratified**: 2025-09-16 | **Last Amended**: 2025-09-16

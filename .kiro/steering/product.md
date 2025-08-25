# Product Overview

This is an omnidirectional robot project built with ROS 2, featuring mecanum wheels for advanced mobility. The robot combines simulation capabilities with real hardware control.

## Core Features

- **Omnidirectional Movement**: Mecanum wheel drive system enabling sideways, diagonal, and rotation-in-place movement
- **Dual Platform Support**: Works in both Gazebo simulation and real hardware with Raspberry Pi + Arduino
- **Motor Control**: Individual PWM control of 4 motors via TB6612FNG motor drivers
- **Sensor Integration**: Camera, LiDAR, and distance sensors for perception
- **Remote Control**: Xbox controller and joystick teleoperation support
- **Power Management**: Battery monitoring with INA3221 sensors and 3S Li-ion battery system

## Target Applications

- Educational robotics platform
- Computer vision and autonomous navigation research
- Teleoperation and remote control systems
- ROS 2 development and testing

## Hardware Components

- **Compute**: Raspberry Pi 4B (8GB) + ESP32 for BMS
- **Motors**: 4x TT motors with mecanum wheels (80mm)
- **Sensors**: USB cameras, VL53L0X distance sensors, optional LiDAR
- **Power**: 3S Li-ion battery system with protection and monitoring
- **Control**: TB6612FNG motor drivers, various I2C sensors

The project is designed as a learning platform for ROS 2 development while providing a solid foundation for advanced robotics applications.
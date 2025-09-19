# Data Model (Phase 1)

Defines core entities, fields, and constraints.

## RobotState

- pose: geometry_msgs/Pose (frame: map)
- twist: geometry_msgs/Twist
- battery: sensor_msgs/BatteryState
- mode: enum { mapping, navigation, teleop }
- turret: { pan_deg: float, tilt_deg: float, aiming: bool, armed: bool }
- last_error: string

## Map

- name: string (e.g., livingroom_2025-09-16)
- path_image: string (.pgm)
- path_yaml: string (.yaml)
- created_at: datetime
- frame_id: string

## Target

- id: string
- bbox: { x: int, y: int, w: int, h: int }
- range_m: float
- confidence: float (0..1)
- timestamp: time

## EventLog

- ts: time
- type: enum { mode_change, fire, error, battery_alert }
- details: string or JSON

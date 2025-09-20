# Research (Phase 0)

This document captures decisions, rationale, and alternatives considered.

## Decisions

1. SLAM/localization

   - Decision: slam_toolbox for 2D mapping/localization, nav2 for planning/control in Navigation mode.
   - Rationale: Stable on Humble; wide examples; compatible with LiDAR + IMU; easy map save/load.
   - Alternatives: hector_slam (no odom), cartographer (deprecated on Humble), GMapping (aged).

2. Dashboard & streaming

   - Decision: Use rosbridge_suite and web_video_server; add a minimal Next.js App Router UI only if needed beyond standard ROS web tools.
   - Rationale: Minimizes deps; fast to wire; mobile-friendly via responsive CSS.
   - Alternatives: Foxglove Web (heavier), custom WebRTC pipeline (complex), rqt_web (limited).

3. Face detection

   - Decision: OpenCV DNN (e.g., ResNet SSD) as a starting point; publish Target messages with pose estimate.
   - Rationale: Lightweight; CPU-capable on Pi 4; acceptable accuracy indoors.
   - Alternatives: YOLO-based detectors (heavier), mediapipe (good but additional deps).

4. Mecanum control

   - Decision: ros2_control with custom Mecanum controller (existing `mecanum_drive_controller`) and TB6612 bridge to Pico.
   - Rationale: Reuse current config; sim parity; clear interfaces.
   - Alternatives: Direct rclpy node for kinematics (lower reuse, more code).

5. Safety envelope

   - Decision: Enforce 1.0–5.0 m distance and −10°..+30° tilt before firing; require arm + watchdog.
   - Rationale: From spec; ensures safe operation.
   - Alternatives: Dynamic envelope (adds complexity) — deferred.

6. Maps persistence

   - Decision: Store maps as .pgm + .yaml in `src/robot/maps/` with descriptive names; manual save in Mapping, read-only load in Navigation.
   - Rationale: Matches spec; simple file I/O.
   - Alternatives: Database-backed map store (overkill).

7. Testing & quality

   - Decision: Add ament linters and one minimal test per package; smoke launch test for Gazebo sim.
   - Rationale: Satisfy constitution gates.
   - Alternatives: Full integration harness now (defer to later).

## Open Items

- Tune nav2 params for mecanum kinematics.
- Verify performance of face detector at target frame rates; adjust resolution.
- Finalize message schema for Target and EventLog.

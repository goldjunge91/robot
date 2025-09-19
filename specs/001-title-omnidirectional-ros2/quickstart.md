# Quickstart (Phase 1)

Follow these steps to run the robot in simulation or on hardware.

## Simulation (Gazebo)

1. Build workspace and source overlay.
2. Launch simulation:
   - ros2 launch robot launch_sim.launch.py world:=`/absolute/path/to/world.sdf`
3. In RViz, verify TF and odometry; controllers should spawn.

## Hardware (Raspberry Pi)

1. Launch robot stack:
   - ros2 launch robot launch_robot.launch.py
2. Optional: start motor bridge (if commented out in launch file):
   - python3 raspberrypi/tb6612_bridge.py

## Mapping Mode

1. Start SLAM toolbox mapping launch (to be added) with LiDAR/IMU.
2. Drive around to build map.
3. Save map manually to src/robot/maps/ as .pgm + .yaml.

## Navigation Mode

1. Start map_server to load a saved map.
2. Launch nav2 stack; send NavigateToPose goals.

## Web Dashboard

- Start rosbridge_suite and web_video_server nodes.
- Open the dashboard (Next.js or minimal HTML) on mobile/desktop; confirm FPV, status, estop, and fire mode controls.

## Safety & Firing

- Ensure arm is required; verify safety envelope (1.0–5.0 m distance, −10°..+30° tilt) enforced in launcher before firing.
- Use estop when in doubt.

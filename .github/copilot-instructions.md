## AI agent quickstart for this repo (ROS 2 robot)

Use this as your working contract when generating code or running commands in this project. Keep guidance concrete and repo-specific.

### What this is
- A ROS 2 package named `robot` (ament_cmake). It contains URDF/Xacro, ros2_control, Gazebo/RViz configs, launch files, and simulation worlds.
- A separate ROS 2 Python package under `raspberrypi/robot_bridge` for hardware bridges (TB6612 motor driver, Xbox → Pico bridge).

### Architecture (big picture)
- Robot model: `description/robot.urdf.xacro` with args `sim_mode` and `use_ros2_control`; includes `ros2_control.xacro` to select hardware vs simulation backends.
- ros2_control:
  - Sim: `gazebo_ros2_control/GazeboSystem` with parameters in `config/gaz_ros2_ctl_use_sim.yaml` and controller YAML (e.g., `config/my_controllers_mecanum.yaml`).
  - Real HW: `drive_arduino/TB6612HardwareInterface` (open loop) configured in `description/ros2_control.xacro`.
- Launch stack:
  - Simulation: `launch/launch_sim.launch.py` → robot_state_publisher (xacro), Gazebo server/client, spawn entity, spawners for `joint_state_broadcaster` and `mecanum_drive_controller`, and `launch/tf_odometry_relay.py` to forward odom TF to `/tf`.
  - Hardware: `launch/launch_robot.launch.py` → includes `launch/rsp.launch.py`, starts `ros2_control_node` with `config/my_controllers.yaml`, spawns `diff_cont` and `joint_broad` (names from that YAML). A minimal direct bridge exists in `raspberrypi/tb6612_bridge.py`, but prefer the dedicated `raspberrypi/robot_bridge` package.
- Worlds: `worlds/*.world` for Gazebo. Prefer using launch files; avoid hardcoded paths inside worlds.

### Critical workflows (tested paths)
- Build the workspace (Linux/WSL recommended): source ROS, then `colcon build --symlink-install`; source `install/setup.bash` before launching.
- Simulate:
  - `ros2 launch robot launch_sim.launch.py world:=<abs path to .world>`
  - Publish commands to the Mecanum controller: `/mecanum_drive_controller/reference_unstamped` with `geometry_msgs/Twist` (not `/cmd_vel`). Example: `ros2 topic pub -r 10 /mecanum_drive_controller/reference_unstamped geometry_msgs/Twist "{linear:{x:0.5,y:0.0}, angular:{z:0.0}}"`.
  - Verify: `ros2 topic echo /tf --once` shows `odom -> base_link`; `ros2 topic hz /joint_states` has traffic.
- Hardware bring-up:
  - `ros2 launch robot launch_robot.launch.py` (ensures `ros2_control_node` + spawners). If using the bridge package: `ros2 launch robot_bridge robot_pi_bridge.launch.py` (see `raspberrypi/robot_bridge/launch/`).

### Conventions and patterns
- Keep tunables in `config/*.yaml`; do not hardcode in code. Controllers are named and spawned exactly as in YAML (e.g., `joint_state_broadcaster`, `mecanum_drive_controller`, `diff_cont`, `joint_broad`).
- Use `get_package_share_directory('robot')` / `FindPackageShare` to locate files in launch code; pass xacro args explicitly: `sim_mode`, `use_ros2_control`.
- Topics: the mecanum controller subscribes to `/mecanum_drive_controller/reference_unstamped`. If you introduce teleop or mux, remap accordingly (see `config/twist_mux.yaml`).
- TF: we rely on `launch/tf_odometry_relay.py` to bridge controller odometry TF into `/tf` for RViz.

### Integration points
- Gazebo plugins: `description/ros2_control.xacro` inserts `<plugin name="gazebo_ros2_control" ...>` with parameters to YAML in `config/`.
- Bridges and utilities live under `raspberrypi/`:
  - `raspberrypi/robot_bridge` is a proper ROS 2 Python package with entry points: `tb6612_bridge`, `xbox_pico_bridge` (see `setup.py`).
  - Low-level Arduino/Pico examples live under `raspberrypi/arduino` and `raspberrypi/mecanum*` (not built by colcon).

### Gotchas and tips
- Re-launch collisions: if Gazebo already has `my_bot`, delete it via `ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'my_bot'}"` before respawn.
- Mecanum strafing visuals may look unrealistic with cylinder wheels in Gazebo; forward/rotation motion is a better validity check.
- Some legacy content references diff drive; prefer the mecanum controller for omnidirectional motion in simulation. Align controller names between launch and YAML.
- Worlds like `test.world` contain old absolute paths; launch through `launch_sim.launch.py` instead.

### AI-specific helpers in this repo
- Prompts for automation live in `.github/prompts/*.prompt.md` and assume PowerShell scripts under `.specify/scripts/powershell/*.ps1` run from the repo root, returning JSON with absolute paths. Follow those prompts when generating specs/plan/tasks artifacts under `specs/001-*/`.

When in doubt, cite and mirror existing patterns from:
- `launch/launch_sim.launch.py`, `launch/rsp.launch.py`, `launch/launch_robot.launch.py`
- `description/ros2_control.xacro`, `description/robot.urdf.xacro`
- `config/*.yaml`
- `raspberrypi/robot_bridge/*`




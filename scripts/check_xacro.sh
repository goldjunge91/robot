#!/usr/bin/env bash
# Local helper to expand xacro and check for expected plugins
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v xacro >/dev/null 2>&1; then
  echo "xacro command not found. Install ROS and xacro before running this script."
  exit 2
fi

echo "Expanding robot.urdf.xacro with sim_mode=false"
xacro description/robot.urdf.xacro > /tmp/robot_non_sim.urdf
if grep -q "drive_arduino/TB6612HardwareInterface" /tmp/robot_non_sim.urdf; then
  echo "OK: TB6612HardwareInterface found"
else
  echo "ERROR: TB6612HardwareInterface not found in /tmp/robot_non_sim.urdf"
  exit 1
fi

echo "Expanding robot.urdf.xacro with sim_mode=true"
xacro description/robot.urdf.xacro sim_mode:=true > /tmp/robot_sim.urdf
if grep -q "gazebo_ros2_control/GazeboSystem" /tmp/robot_sim.urdf; then
  echo "OK: GazeboSystem found"
else
  echo "ERROR: GazeboSystem not found in /tmp/robot_sim.urdf"
  exit 1
fi

echo "All checks passed."

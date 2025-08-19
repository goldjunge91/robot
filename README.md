## Robot Package Template

This is a GitHub template. You can make your own copy by clicking the green "Use this template" button.

It is recommended that you keep the repo/package name the same, but if you do change it, ensure you do a "Find all" using your IDE (or the built-in GitHub IDE by hitting the `.` key) and rename all instances of `robot` to whatever your project's name is.

Note that each directory currently has at least one file in it to ensure that git tracks the files (and, consequently, that a fresh clone has direcctories present for CMake to find). These example files can be removed if required (and the directories can be removed if `CMakeLists.txt` is adjusted accordingly).



## Packages to install

sudo apt install 
- sudo apt install ros-humble-gazebo-ros-pkgs  // dabei muss humble durch die richtige <ROS-DISTRO> 

how to run:
colcon build  --symlink-install
source install/setup.bash
1. Terminals öffnen wsl -d Ubuntu-22.04
- ros2 launch robot rsp.launch.py
- rviz2  // rviz2 -d src/robot/config/view_robot.rviz 
- ros2 run joint_state_publisher_gui joint_state_publisher_gui

Simulation aktivieren
- ros2 launch robot rsp.launch.py use_sim_time:=true // wie man prüft ob die simulation erfolgreich gestartet wurde  'ros2 param get /robot_state_publisher use_sim_time' Boolean value is: True
ros2 launch gazebo_ros gazebo.launch.py
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity robot
- ros2 launch robot launch_sim.launch.py
# Bridge (passt ggf. den Port an)

ros2 run foxbot_bridge foxbot_bridge --ros-args -p port:=/dev/ttyACM0

# Teleop

sudo apt install -y ros-humble-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard

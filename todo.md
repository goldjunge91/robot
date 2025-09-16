Controllers active; /joint_states at ~10 Hz.
Gazebo moves; odometry published on /mecanum_drive_controller/odometry.
TF relay added so odom->base_link goes to /tf.
Do This Now

Start clean
Close old sim or kill: pkill -f gzserver; pkill -f gzclient
source install/setup.bash
ros2 launch robot launch_sim.launch.py
RViz setup
rviz2 -d src/robot/config/view_robot.rviz
Global Options → check “Use Sim Time”
Fixed Frame: set base_link first; after TF flows, switch to odom
Drive using correct topic
ros2 topic pub -r 20 /mecanum_drive_controller/reference_unstamped geometry_msgs/Twist "{linear: {x: 1.0, y: 0.0}, angular: {z: 0.0}}"
Sanity Checks

TF present:
ros2 topic echo /tf --once (look for odom -> base_link and chassis -> front_*_wheel)
Joint states flowing (already OK):
ros2 topic hz /joint_states
Relay running:
You should see “Relaying /mecanum_drive_controller/tf_odometry -> /tf” in launch output
If needed: python3 src/robot/launch/tf_odometry_relay.py
Why RViz showed wheel TF errors

RViz wasn’t using sim time or hadn’t received /joint_states/TF yet. With sim time enabled and joint states active, robot_state_publisher provides chassis -> wheel transforms and errors clear.
Avoid Re-launch Collisions

The spawn errors (“Entity [my_bot] already exists”) happen if Gazebo is still running and you launch again. Either kill Gazebo first or remove the model:
ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'my_bot'}"
Notes

Command topic: controller subscribes to /mecanum_drive_controller/reference_unstamped (not /cmd_vel).
Strafing with simple cylinder wheels won’t look realistic in Gazebo; forward/rotate should be obvious.
If RViz still complains after the steps above, paste:

ros2 topic echo /tf --once
ros2 node list | grep robot_state_publisher
ros2 topic echo /joint_states --once
and I’ll pinpoint the last gap.
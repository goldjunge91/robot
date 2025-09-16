# Topics, Services, and Actions (Phase 1 Draft)

This draft enumerates expected ROS 2 interfaces. Final message types may adjust during implementation.

## Mobility & State

- /cmd_vel (geometry_msgs/Twist)
- /odom (nav_msgs/Odometry)
- /tf, /tf_static (tf2_msgs/TFMessage)
- /joint_states (sensor_msgs/JointState)

## Perception

- /camera/image_raw (sensor_msgs/Image)
- /camera/camera_info (sensor_msgs/CameraInfo)
- /scan (sensor_msgs/LaserScan)
- /imu (sensor_msgs/Imu)
- /range/front (sensor_msgs/Range)

## SLAM / Navigation

- /map (nav_msgs/OccupancyGrid)
- /map_metadata (nav_msgs/MapMetaData)
- /amcl_pose or /slam_toolbox/pose (geometry_msgs/PoseWithCovarianceStamped)
- nav2 actions: NavigateToPose, FollowWaypoints

## Turret & Launcher

- /turret/cmd (custom: pan_deg, tilt_deg)
- /turret/state (custom: pan_deg, tilt_deg, aiming: bool)
- /fire/arm (std_msgs/Bool)
- /fire/cmd (std_msgs/Bool) — respected only when armed and safety envelope satisfied
- /target/detections (custom: array of Target)
- /target/selected (custom: Target)

## Power & Diagnostics

- /battery (sensor_msgs/BatteryState or custom INA3221 aggregate)
- /diagnostics (diagnostic_msgs/DiagnosticArray)
- /events (custom EventLog)

## Dashboard Bridge (rosbridge)

- Websocket JSON over rosbridge to publish/subscribe to the above.
- Video via web_video_server on /camera/image_raw.

Notes:

- Names to be finalized; prefer standard types where possible.
- Safety envelope checks enforced in launcher node before honoring /fire/cmd.

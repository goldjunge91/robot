import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():

    # Das 'robot' Paket, in dem wir uns befinden
    robot_package_name = "robot"
    # Das 'robot_bridge' Paket, das den Treiber-Node enthält
    bridge_package_name = "robot_bridge"

    # --- Launch-Argumente ---
    cmd_topic = LaunchConfiguration('cmd_topic')

    # --- 1. Robot State Publisher (RSP) ---
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory(robot_package_name), "launch", "rsp.launch.py")]
        ),
        launch_arguments={"use_sim_time": "false", "use_ros2_control": "false"}.items(),
    )

    # --- 2. Arduino Bridge Node ---
    tb6612_bridge_node = Node(
        package=bridge_package_name,  # SEHR WICHTIG: Hier muss 'robot_bridge' stehen!
        executable='tb6612_bridge',
        name='tb6612_bridge',
        output='screen',
        parameters=[{
            'cmd_topic': cmd_topic,
            'port': '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0',
            # Füge hier bei Bedarf weitere Parameter hinzu
        }]
    )

    # --- 3. Sensoren ---
    camera_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory(robot_package_name), 'launch', 'camera.launch.py')]
        )
    )
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory(robot_package_name), 'launch', 'rplidar.launch.py')]
        )
    )

    # --- Alles zusammenführen und starten ---
    return LaunchDescription([
        DeclareLaunchArgument(
            'cmd_topic', 
            default_value='/cmd_vel', 
            description='Topic for bridge/teleop'
        ),
        rsp,
        camera_launch,
        tb6612_bridge_node,
    ])

# import os
# from ament_index_python.packages import get_package_share_directory
# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch.substitutions import LaunchConfiguration
# from launch_ros.actions import Node

# def generate_launch_description():

#     package_name = "robot"

#     # --- Launch-Argumente ---
#     cmd_topic = LaunchConfiguration('cmd_topic')

#     # --- 1. Robot State Publisher (RSP) ---
#     # Lädt das Roboter-Modell (URDF)
#     rsp = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource(
#             [os.path.join(get_package_share_directory(package_name), "launch", "rsp.launch.py")]
#         ),
#         launch_arguments={"use_sim_time": "false", "use_ros2_control": "false"}.items(),
#     )

#     # --- 2. Arduino Bridge (Dein Code) ---
#     # Dies ist der korrekte Weg, deinen Python-Node zu starten.
#     # Wir sagen ROS2: "Finde das Paket 'robot_bridge' und starte darin
#     # das Executable 'tb6612_bridge'".
#     tb6612_bridge_node = Node(
#         package='robot_bridge',  # Name des Pakets, in dem sich der Code befindet
#         executable='tb6612_bridge',  # Name des Executables aus der setup.py
#         name='tb6612_bridge',
#         output='screen',
#         parameters=[{
#             'cmd_topic': cmd_topic,
#             'port': '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0',
#             'baud': 115200,
#             'max_lin': 0.5,
#             'max_ang': 1.0,
#             'mix': 1.0,
#             'send_hz': 20.0
#         }]
#     )

#     # --- 3. Kamera-Node ---
#     camera_launch = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource(
#             [os.path.join(get_package_share_directory(package_name), 'launch', 'camera.launch.py')]
#         )
#     )

#     # --- 4. Lidar-Node ---
#     lidar_launch = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource(
#             [os.path.join(get_package_share_directory(package_name), 'launch', 'rplidar.launch.py')]
#         )
#     )

#     # --- Alles zusammenführen und starten ---
#     return LaunchDescription([
#         DeclareLaunchArgument(
#             'cmd_topic', 
#             default_value='/cmd_vel', 
#             description='Topic for bridge/teleop'
#         ),
        
#         # Alle Komponenten starten
#         rsp,
#         # camera_launch,
#         # lidar_launch,
#         tb6612_bridge_node,
#     ])

# # import os

# # from ament_index_python.packages import get_package_share_directory


# # from launch import LaunchDescription
# # from launch.actions import IncludeLaunchDescription, TimerAction, ExecuteProcess
# # from launch.launch_description_sources import PythonLaunchDescriptionSource
# # from launch.substitutions import Command
# # from launch.actions import RegisterEventHandler
# # from launch.event_handlers import OnProcessStart

# # from launch_ros.actions import Node
# # from launch.substitutions import LaunchConfiguration
# # from launch.actions import DeclareLaunchArgument
# # from launch.conditions import IfCondition


# # def generate_launch_description():

# #     # Include the robot_state_publisher launch file, provided by our own package.
# #     # Two launch arguments are provided so we can disable ros2_control at runtime
# #     # during development (the hardware plugin may not be available).

# #     package_name = "robot"

# #     use_ros2_control = LaunchConfiguration('use_ros2_control')
# #     cmd_topic_arg = DeclareLaunchArgument(
# #         'cmd_topic', 
# #         default_value='/cmd_vel', 
# #         description='Topic for the robot bridge'
# #     )
# #     cmd_topic = LaunchConfiguration('cmd_topic')

# #     rsp = IncludeLaunchDescription(
# #         PythonLaunchDescriptionSource(
# #             [
# #                 os.path.join(
# #                     get_package_share_directory(package_name), "launch", "rsp.launch.py"
# #                 )
# #             ]
# #         ),
# #         launch_arguments={"use_sim_time": "false", "use_ros2_control": "false"}.items(),
# #         #       launch_arguments={"use_sim_time": "false", "use_ros2_control": use_ros2_control}.items(),
# #     )

# #     robot_description = Command(
# #         ["ros2 param get --hide-type /robot_state_publisher robot_description"]
# #     )

# #     controller_params_file = os.path.join(
# #         get_package_share_directory(package_name), "config", "my_controllers.yaml"
# #     )

# #     # 2. Arduino Bridge (Dein Code)
# #     # Startet deine Python-Bridge, die auf Geschwindigkeitsbefehle lauscht
# #     tb6612_bridge_proc = ExecuteProcess(
# #         cmd=["python3", "-m", "robot_bridge.tb6612_bridge"],
# #         name="tb6612_bridge",
# #         output="screen",
# #         additional_env={"CMD_TOPIC": cmd_topic},
# #     )
# #     # --- 3. Kamera-Node ---
# #     # Startet den Treiber für die Kamera.
# #     camera_launch = IncludeLaunchDescription(
# #         PythonLaunchDescriptionSource(
# #             [os.path.join(get_package_share_directory(package_name), 'launch', 'camera.launch.py')]
# #         )
# #     )

# #     # --- 4. Lidar-Node ---
# #     # Startet den Treiber für den RPLIDAR.
# #     lidar_launch = IncludeLaunchDescription(
# #         PythonLaunchDescriptionSource(
# #             [os.path.join(get_package_share_directory(package_name), 'launch', 'rplidar.launch.py')]
# #         )
# #     )
# #     controller_manager = Node(
# #         package="controller_manager",
# #         executable="ros2_control_node",
# #         parameters=[{"robot_description": robot_description}, controller_params_file],
# #         condition=IfCondition(use_ros2_control),
# #     )

# #     delayed_controller_manager = TimerAction(period=3.0, actions=[controller_manager], condition=IfCondition(use_ros2_control))

# #     diff_drive_spawner = Node(
# #         package="controller_manager",
# #         executable="spawner",
# #         arguments=["diff_cont"],
# #         condition=IfCondition(use_ros2_control),
# #     )

# #     delayed_diff_drive_spawner = RegisterEventHandler(
# #         event_handler=OnProcessStart(
# #             target_action=controller_manager,
# #             on_start=[diff_drive_spawner],
# #         ),
# #         condition=IfCondition(use_ros2_control),
# #     )

# #     joint_broad_spawner = Node(
# #         package="controller_manager",
# #         executable="spawner",
# #         arguments=["joint_broad"],
# #         condition=IfCondition(use_ros2_control),
# #     )

# #     delayed_joint_broad_spawner = RegisterEventHandler(
# #         event_handler=OnProcessStart(
# #             target_action=controller_manager,
# #             on_start=[joint_broad_spawner],
# #         ),
# #         condition=IfCondition(use_ros2_control),
# #     )

# #     # Code for delaying a node (I haven't tested how effective it is)
# #     #
# #     # First add the below lines to imports
# #     # from launch.actions import RegisterEventHandler
# #     # from launch.event_handlers import OnProcessExit
# #     #
# #     # Then add the following below the current diff_drive_spawner
# #     # delayed_diff_drive_spawner = RegisterEventHandler(
# #     #     event_handler=OnProcessExit(
# #     #         target_action=spawn_entity,
# #     #         on_exit=[diff_drive_spawner],
# #     #     )
# #     # )
# #     #
# #     # Replace the diff_drive_spawner in the final return with delayed_diff_drive_spawner

# #     # --------------------- NEU (minimal) ---------------------
# #     # Start the tb6612 bridge by running the package module directly with python -m
# #     # This avoids requiring an installed console entrypoint (libexec) during dev builds.
# #     # tb6612_bridge_proc = ExecuteProcess(
# #     #     cmd=[
# #     #         "python3",
# #     #         "-m",
# #     #         "robot_bridge.tb6612_bridge",
# #     #         "--ros-args",
# #     #         "-p",
# #     #         "port:=/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0",
# #     #         "-p",
# #     #         "baud:=115200",
# #     #         "-p",
# #     #         "max_lin:=0.5",
# #     #         "-p",
# #     #         "max_ang:=1.0",
# #     #         "-p",
# #     #         "mix:=1.0",
# #     #         "-p",
# #     #         "send_hz:=20.0",
# #     #     ],
# #     #     name="tb6612_bridge",
# #     #     output="screen",
# #     #     additional_env={"CMD_TOPIC": cmd_topic},
# #     # )
# #     # ---------------------------------------------------------

# #     # Launch them all!
# #     # return LaunchDescription(
# #     #     [
# #     #         DeclareLaunchArgument(
# #     #             'use_ros2_control', default_value='false', description='Enable ros2_control (set false for dev)'
# #     #         ),
# #     #         DeclareLaunchArgument(
# #     #             'cmd_topic', default_value='/diff_cont/cmd_vel_unstamped', description='Topic for bridge/teleop'
# #     #         ),
# #     #         rsp,
# #     #         delayed_controller_manager,
# #     #         delayed_diff_drive_spawner,
# #     #         delayed_joint_broad_spawner,
# #     #          # -------- NEU: Bridge starten --------
# #     #         tb6612_bridge_proc,
# #     #     ]
# #     # )
# #     return LaunchDescription(
# #         [
# #             DeclareLaunchArgument(
# #                 'use_ros2_control', default_value='false', description='Enable ros2_control'
# #             ),
# #             DeclareLaunchArgument(
# #                 'cmd_topic', default_value='/cmd_vel', description='Topic for bridge/teleop'
# #             ),
            
# #             # Nodes, die immer laufen:
# #             # rsp,
# #             # camera_launch,
# #             # lidar_launch,
            
# #             # Entweder die Bridge ODER ros2_control:
# #             tb6612_bridge_proc,
            
# #             # delayed_controller_manager,
# #             # #...
# #             # diff_drive_spawner,
# #             # joint_broad_spawner
# #         ]
# #     )

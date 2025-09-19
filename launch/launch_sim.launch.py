import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share = get_package_share_directory('robot')
    
    # --- Launch-Argumente ---
    world_arg = DeclareLaunchArgument(
        name='world',
        default_value=os.path.join(pkg_share, 'worlds', 'empty.world'),
        description='Vollständiger Pfad zur zu ladenden World-Datei'
    )
    
    rviz_config_arg = DeclareLaunchArgument(
        name='rviz_config',
        # Wir setzen die Odometrie-Ansicht als neuen Standard
        default_value=os.path.join(pkg_share, 'config', 'drive_robot_gazebo_rviz.rviz'),
        description='Vollständiger Pfad zur RViz-Konfigurationsdatei'
    )

    use_sim_time_param = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # --- Kernkomponenten ---
    robot_description_config = Command([
        'xacro ',
        os.path.join(pkg_share, 'description', 'robot.urdf.xacro'),
        ' use_ros2_control:=true', ' sim_mode:=true'
    ])

    gzserver_cmd = ExecuteProcess(
        cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', LaunchConfiguration('world')],
        output='screen'
    )
    gzclient_cmd = ExecuteProcess(cmd=['gzclient'], output='screen')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_config,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )

    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'robot'],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    mecanum_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["mecanum_drive_controller", "--controller-manager", "/controller_manager"],
    )
    
    delay_spawners_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[joint_state_broadcaster_spawner, mecanum_drive_controller_spawner],
        )
    )

    # --- NEU: Hinzufügen des TF Relay Knotens ---
    tf_relay_node = Node(
        package='robot', # Das Skript ist Teil deines 'robot'-Pakets
        executable='tf_odometry_relay.py', # Name deines Python-Skripts
        name='tf_odometry_relay',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    # --- Launch-Beschreibung zusammenstellen ---
    return LaunchDescription([
        use_sim_time_param,
        world_arg,
        rviz_config_arg,
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_node,
        spawn_entity_node,
        rviz_node,
        delay_spawners_after_spawn,
        tf_relay_node, # Den neuen Relay-Knoten hinzufügen
    ])

# import os

# from launch import LaunchDescription
# from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler
# from launch.event_handlers import OnProcessExit  # Wichtig für den verzögerten Start
# from launch.substitutions import LaunchConfiguration, Command
# from launch_ros.actions import Node
# from ament_index_python.packages import get_package_share_directory

# def generate_launch_description():
#     pkg_share = get_package_share_directory('robot')
    
#     # --- Launch-Argumente ---
#     world_arg = DeclareLaunchArgument(
#         name='world',
#         default_value=os.path.join(pkg_share, 'worlds', 'empty.world'),
#         description='Vollständiger Pfad zur zu ladenden World-Datei'
#     )
    
#     rviz_config_arg = DeclareLaunchArgument(
#         name='rviz_config',
#         default_value=os.path.join(pkg_share, 'config', 'view_robot.rviz'),
#         description='Vollständiger Pfad zur RViz-Konfigurationsdatei'
#     )

#     # --- Globale Parameter ---
#     use_sim_time_param = DeclareLaunchArgument(
#         'use_sim_time',
#         default_value='true',
#         description='Use simulation (Gazebo) clock if true'
#     )

#     # --- Kernkomponenten ---

#     # 1. Roboterbeschreibung laden
#     robot_description_config = Command([
#         'xacro ',
#         os.path.join(pkg_share, 'description', 'robot.urdf.xacro'),
#         ' use_ros2_control:=true',
#         ' sim_mode:=true'
#     ])

#     # 2. Gazebo starten
#     gzserver_cmd = ExecuteProcess(
#         cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', LaunchConfiguration('world')],
#         output='screen'
#     )
#     gzclient_cmd = ExecuteProcess(cmd=['gzclient'], output='screen')

#     # 3. Robot State Publisher
#     robot_state_publisher_node = Node(
#         package='robot_state_publisher',
#         executable='robot_state_publisher',
#         output='screen',
#         parameters=[{
#             'robot_description': robot_description_config,
#             'use_sim_time': LaunchConfiguration('use_sim_time')
#         }]
#     )

#     # 4. Roboter in Gazebo spawnen
#     spawn_entity_node = Node(
#         package='gazebo_ros',
#         executable='spawn_entity.py',
#         arguments=['-topic', 'robot_description', '-entity', 'robot'],
#         output='screen'
#     )

#     # 5. RViz starten
#     rviz_node = Node(
#         package='rviz2',
#         executable='rviz2',
#         name='rviz2',
#         arguments=['-d', LaunchConfiguration('rviz_config')],
#         output='screen',
#         parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
#     )

#     # --- DER ENTSCHEIDENDE TEIL: Controller explizit starten ---
#     joint_state_broadcaster_spawner = Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
#     )

#     mecanum_drive_controller_spawner = Node(
#         package="controller_manager",
#         executable="spawner",
#         arguments=["mecanum_drive_controller", "--controller-manager", "/controller_manager"],
#     )
    
#     # Event-Handler, der wartet, bis der Roboter gespawnt ist, und DANN die Controller startet.
#     delay_spawners_after_spawn = RegisterEventHandler(
#         event_handler=OnProcessExit(
#             target_action=spawn_entity_node,
#             on_exit=[joint_state_broadcaster_spawner, mecanum_drive_controller_spawner],
#         )
#     )

#     # --- Launch-Beschreibung zusammenstellen ---
#     return LaunchDescription([
#         use_sim_time_param,
#         world_arg,
#         rviz_config_arg,
#         gzserver_cmd,
#         gzclient_cmd,
#         robot_state_publisher_node,
#         spawn_entity_node,
#         rviz_node,
#         delay_spawners_after_spawn, # Dieser Teil hat im von dir geposteten Code gefehlt.
#     ])
import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    RegisterEventHandler,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PythonExpression,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import xacro


def generate_launch_description():
    pkg_share = get_package_share_directory('robot')
    os.path.join(pkg_share, 'worlds')
    os.path.join(pkg_share, 'models')

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

    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='true',
        description='If true, skip gzclient and RViz (headless)'
    )

    use_gazebo_ros_launch_arg = DeclareLaunchArgument(
        'use_gazebo_ros_launch',
        default_value='false',
        description='Use gazebo_ros/gazebo.launch.py instead of raw gzserver/gzclient when true'
    )

    with_gazebo_gui_arg = DeclareLaunchArgument(
        'with_gazebo_gui',
        default_value='true',
        description='Start Gazebo client in addition to server'
    )

    with_rviz_arg = DeclareLaunchArgument(
        'with_rviz',
        default_value='true',
        description='Start RViz2 alongside the simulation'
    )

    # --- Kernkomponenten ---
    robot_description_processed = xacro.process_file(
        os.path.join(pkg_share, 'description', 'robot.urdf.xacro'),
        mappings={'use_ros2_control': 'true', 'sim_mode': 'true'}
    ).toxml()

    gzserver_cmd = ExecuteProcess(
        cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', LaunchConfiguration('world')],
        output='screen',
        condition=UnlessCondition(LaunchConfiguration('use_gazebo_ros_launch'))
    )
    gzclient_cmd = ExecuteProcess(
        cmd=['gzclient'],
        output='screen',
        condition=IfCondition(PythonExpression([
            '"', LaunchConfiguration('headless'), '" == "false" and "',
            LaunchConfiguration('use_gazebo_ros_launch'), '" == "false"'
        ]))
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_processed,
            'use_sim_time': LaunchConfiguration('use_sim_time')
        }]
    )
    #  robot_state_publisher_node = Node(
    #     package='robot_state_publisher',
    #     executable='robot_state_publisher',
    #     output='screen',
    #     parameters=[{
    #         'robot_description': robot_description_config,
    #         'use_sim_time': LaunchConfiguration('use_sim_time')
    #     }]
    # )

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
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        condition=IfCondition(PythonExpression([
            '"', LaunchConfiguration('with_rviz'), '" == "true" and "',
            LaunchConfiguration('headless'), '" == "false"'
        ]))
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    mecanum_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["drive_controller", "--controller-manager", "/controller_manager"],
    )

    delay_spawners_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[joint_state_broadcaster_spawner, mecanum_drive_controller_spawner],
        )
    )

    # Korrigierter Start des TF-Relay als direkter Python-Prozess
    tf_relay_script_path = os.path.join(pkg_share, 'launch', 'tf_odometry_relay.py')
    tf_relay_proc = ExecuteProcess(
        cmd=['python3', tf_relay_script_path],
        name='tf_odometry_relay',
        output='screen'
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            ])
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'verbose': 'true',
            'pause': 'false',
            'gui': LaunchConfiguration('with_gazebo_gui')
        }.items(),
        condition=IfCondition(LaunchConfiguration('use_gazebo_ros_launch'))
    )

    # # --- NEU: Hinzufügen des TF Relay Knotens ---
    # tf_relay_node = Node(
    #     package='robot', # Das Skript ist Teil deines 'robot'-Pakets
    #     executable='tf_odometry_relay.py', # Name deines Python-Skripts
    #     name='tf_odometry_relay',
    #     output='screen',
    #     parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    # )

    # --- Launch-Beschreibung zusammenstellen ---
    launch_actions = [
        use_sim_time_param,
        world_arg,
        rviz_config_arg,
        headless_arg,
        use_gazebo_ros_launch_arg,
        with_gazebo_gui_arg,
        with_rviz_arg,
    ]

    launch_actions.extend([
        gazebo_launch,
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_node,
        spawn_entity_node,
        rviz_node,
        delay_spawners_after_spawn,
        tf_relay_proc,
        # tf_relay_node,
    ])

    return LaunchDescription(launch_actions)


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

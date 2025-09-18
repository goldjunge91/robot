import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    pkg_share = get_package_share_directory('robot')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    world_arg = DeclareLaunchArgument(
        name='world',
        default_value=os.path.join(pkg_share, 'worlds', 'empty.world'),
        description='Full path to the world file to load'
    )

    # Optionally enable the tf odometry relay (only start once)
    enable_tf_relay_arg = DeclareLaunchArgument(
        name='enable_tf_relay',
        default_value='true',
        description='Enable tf odometry relay node to republish /mecanum_drive_controller/tf_odometry -> /tf'
    )

    # Robot Description (URDF)
    robot_description_config = Command([
        'xacro ',
        os.path.join(pkg_share, 'description', 'robot.urdf.xacro'),
        ' use_ros2_control:=true',
        ' sim_mode:=true'
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_config, 'use_sim_time': True}]
    )

    # Gazebo Simulation
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    # Spawner: Robot Model
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'my_bot'],
        output='screen'
    )

    # Note: We intentionally DO NOT spawn controllers externally here.
    # The gazebo_ros2_control plugin already loads and configures the controllers
    # from the robot's parameter files. Starting external spawners as well
    # causes STRICT switch failures and duplicate controller instances.

    # Start tf_odometry_relay only when explicitly enabled to avoid duplicates
    from launch.conditions import IfCondition

    tf_relay = ExecuteProcess(
        cmd=[
            'python3',
            os.path.join(pkg_share, 'launch', 'tf_odometry_relay.py'),
        ],
        output='screen',
        condition=IfCondition(LaunchConfiguration('enable_tf_relay')),
    )

    return LaunchDescription([
        world_arg,
        enable_tf_relay_arg,
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity_node,
        tf_relay,
    ])

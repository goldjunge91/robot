import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Define paths to key packages and files
    pkg_share = FindPackageShare(package="robot").find("robot")
    pkg_gazebo_ros = FindPackageShare(package="gazebo_ros").find("gazebo_ros")

    # --- Launch Arguments ---
    # Argument to allow users to specify a world file
    world_arg = DeclareLaunchArgument(
        name="world",
        default_value=os.path.join(pkg_share, "worlds", "empty.world"),
        description="Full path to the world file to load",
    )

    # --- Robot Description (URDF) ---
    # This processes your URDF file and prepares it for ROS 2
    xacro_file = os.path.join(pkg_share, "description", "robot.urdf.xacro")
    robot_description_config = Command(["xacro ", xacro_file, " sim_mode:=true"])
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description_config, "use_sim_time": True}
        ],
        output="screen",
    )

    # --- Gazebo Simulation ---
    # This starts the Gazebo physics server
    gzserver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzserver.launch.py")
        ),
        launch_arguments={"world": LaunchConfiguration("world")}.items(),
    )

    # This starts the Gazebo graphical client
    gzclient_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, "launch", "gzclient.launch.py")
        )
    )

    # --- Spawner Nodes ---
    # 1. This node spawns your robot model into the running Gazebo simulation
    spawn_entity_node = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "my_bot"],
        output="screen",
    )

    # 2. This node loads the Joint State Broadcaster controller
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # 3. This node loads your Mecanum Drive Controller
    mecanum_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "mecanum_drive_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
    )

    # 4. Relay controller's TF to standard /tf so RViz can see odom->base_link
    tf_relay = ExecuteProcess(
        cmd=[
            "python3",
            os.path.join(pkg_share, "launch", "tf_odometry_relay.py"),
        ],
        output="screen",
    )

    # --- Assemble the Launch Description ---
    # This defines the order in which things are started.
    return LaunchDescription(
        [
            world_arg,
            gzserver_launch,
            gzclient_launch,
            robot_state_publisher_node,
            spawn_entity_node,
            joint_state_broadcaster_spawner,
            mecanum_drive_controller_spawner,
            tf_relay,
        ]
    )

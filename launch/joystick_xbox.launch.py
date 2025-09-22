from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    cmd_topic = LaunchConfiguration("cmd_topic")

    joy_params = os.path.join(
        get_package_share_directory("robot"), "config", "joystick.yaml"
    )

    joy_node = Node(
        package="joy",
        executable="joy_node",
        parameters=[joy_params, {"use_sim_time": use_sim_time}],
    )

    teleop_node = Node(
        package="teleop_twist_joy",
        executable="teleop_node",
        name="teleop_node",
        parameters=[joy_params, {"use_sim_time": use_sim_time}],
        remappings=[("/cmd_vel", cmd_topic)],
    )

    # twist_stamper = Node(
    #     package="twist_stamper",
    #     executable="twist_stamper",
    #     parameters=[{"use_sim_time": use_sim_time}],
    #     remappings=[
    #         ("/cmd_vel_in", "/drive_controller/cmd_vel_unstamped"),
    #         ("/cmd_vel_out", "/drive_controller/cmd_vel"),
    #     ],
    # )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use sim time if true",
            ),
            DeclareLaunchArgument(
                "cmd_topic",
                default_value="/drive_controller/cmd_vel_unstamped",
                description="Topic where teleop publishes (forwarded to bridge)",
            ),
            joy_node,
            teleop_node,
            # twist_stamper
        ]
    )

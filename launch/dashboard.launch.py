"""Launch dashboard bridge stack with rosbridge and web_video_server."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    bridge_port_arg = DeclareLaunchArgument(
        "bridge_port",
        default_value="9090",
        description="Port exposed by rosbridge_websocket",
    )
    video_port_arg = DeclareLaunchArgument(
        "video_port",
        default_value="8080",
        description="HTTP port for web_video_server streams",
    )

    rosbridge = Node(
        package="rosbridge_server",
        executable="rosbridge_websocket",
        name="rosbridge_websocket",
        output="screen",
        parameters=[{"port": LaunchConfiguration("bridge_port")}],
    )

    web_video = Node(
        package="web_video_server",
        executable="web_video_server",
        name="web_video_server",
        output="screen",
        parameters=[{"port": LaunchConfiguration("video_port")}],
    )

    return LaunchDescription([
        bridge_port_arg,
        video_port_arg,
        rosbridge,
        web_video,
    ])

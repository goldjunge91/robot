from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        SetEnvironmentVariable('ROS_DOMAIN_ID', '90'),
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY', '0'),
        SetEnvironmentVariable('RMW_IMPLEMENTATION', 'rmw_cyclonedds_cpp'),

        Node(
            package='robot_bridge',
            executable='tb6612_bridge',
            name='tb6612_bridge',
            output='screen',
            parameters=[{
                'cmd_topic': '/cmd_vel',
                'port': '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0',
                'baud': 115200,
                'max_lin': 0.5,
                'max_ang': 1.0,
                'mix': 1.0,
                'send_hz': 20.0
            }],
        ),
    ])

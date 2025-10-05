from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    teleop_cfg = os.path.join(
        get_package_share_directory('robot'), 'config', 'xbox_mecanum_teleop.yaml'
    )

    joy = Node(
        package='joy',
        executable='joy_node',
        parameters=[teleop_cfg, {'use_sim_time': use_sim_time}],
        name='joy_node'
    )

    teleop = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy',
        parameters=[teleop_cfg, {'use_sim_time': use_sim_time}],
        # Default publishes /cmd_vel which the mecanum controller consumes
    )

    xbox_pico = Node(
        package='robot_bridge',
        executable='xbox_pico_bridge',
        name='xbox_pico_bridge',
        parameters=[
            # Defaults are fine; customize buttons/presets here if needed
            {
                'esc_presets': [0, 20, 40, 60],
                'publish_both': True,
                # Buttons: LB=4 (down), RB=5 (up), A=0 (CW), X=2 (CCW), Y=3 (arm), B=1 (stop)
                'btn_preset_up': 5,
                'btn_preset_down': 4,
                'btn_rotate_cw': 0,
                'btn_rotate_ccw': 2,
                'btn_arm': 3,
                'btn_stop': 1,
            },
            {'use_sim_time': use_sim_time},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        joy,
        teleop,
        xbox_pico,
    ])

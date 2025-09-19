import os

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription(
        [
            Node(
                package="v4l2_camera",
                executable="v4l2_camera_node",
                output="screen",
                parameters=[
                    {
                        "image_size": [640, 480],
                        "camera_frame_id": "camera_link_optical",
                        # Correct parameter name for v4l2_camera is "video_device"
                        "video_device": "/dev/v4l/by-id/usb-HD_USB_Camera_HD_USB_Camera-video-index0",
                        "camera_name": "camera",
                        "pixel_format": "YUYV",
                        "camera_info_url": "file:///home/pi/.ros/camera_info/camera.yaml",
                    }
                ],
            )
        ]
    )

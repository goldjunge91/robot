#!/usr/bin/env python3
"""Simple helper that waits until a ROS2 service is available.

Usage: python3 wait_for_service.py /controller_manager/list_controllers
"""
import sys
import rclpy
from controller_manager_msgs.srv import ListControllers


def main(argv=None):
    argv = argv or sys.argv[1:]
    svc_name = argv[0] if argv else '/controller_manager/list_controllers'

    rclpy.init()
    node = rclpy.create_node('wait_for_service_node')
    client = node.create_client(ListControllers, svc_name)
    node.get_logger().info(f'Waiting for service {svc_name}...')

    try:
        while rclpy.ok():
            if client.wait_for_service(timeout_sec=1.0):
                node.get_logger().info(f'Service {svc_name} is available')
                break
            node.get_logger().info(f'still waiting for {svc_name}...')
    except KeyboardInterrupt:
        node.get_logger().info('Interrupted while waiting for service')
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage


class TfOdometryRelay(Node):
    def __init__(self):
        super().__init__('tf_odometry_relay')
        # Subscribe to both new and legacy controller TF odometry topics
        self.sub_new = self.create_subscription(
            TFMessage,
            '/drive_controller/tf_odometry',
            self._cb,
            10,
        )
        self.sub_old = self.create_subscription(
            TFMessage,
            '/mecanum_drive_controller/tf_odometry',
            self._cb,
            10,
        )
        # Republish to the standard TF topic
        self.pub = self.create_publisher(TFMessage, '/tf', 10)
        self.get_logger().info('Relaying /drive_controller|/mecanum_drive_controller tf_odometry -> /tf')

    def _cb(self, msg: TFMessage):
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = TfOdometryRelay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

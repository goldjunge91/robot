#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import UInt8
from std_srvs.srv import Trigger


class XboxPicoBridge(Node):
    def __init__(self):
        super().__init__('xbox_pico_bridge')

        # Parameters
        self.declare_parameter('joy_topic', '/joy')
        self.declare_parameter('esc1_topic', '/esc1_percent')
        self.declare_parameter('esc2_topic', '/esc2_percent')
        self.declare_parameter('publish_both', True)
        self.declare_parameter('esc_presets', [0, 20, 40, 60])
        self.declare_parameter('btn_preset_up', 5)   # RB
        self.declare_parameter('btn_preset_down', 4) # LB
        self.declare_parameter('btn_rotate_cw', 0)   # A
        self.declare_parameter('btn_rotate_ccw', 2)  # X
        self.declare_parameter('btn_arm', 3)         # Y
        self.declare_parameter('btn_stop', 1)        # B

        joy_topic = self.get_parameter('joy_topic').value
        esc1_topic = self.get_parameter('esc1_topic').value
        esc2_topic = self.get_parameter('esc2_topic').value
        self.publish_both = bool(self.get_parameter('publish_both').value)
        self.esc_presets = list(self.get_parameter('esc_presets').value)
        self.btn_up = int(self.get_parameter('btn_preset_up').value)
        self.btn_dn = int(self.get_parameter('btn_preset_down').value)
        self.btn_cw = int(self.get_parameter('btn_rotate_cw').value)
        self.btn_ccw = int(self.get_parameter('btn_rotate_ccw').value)
        self.btn_arm = int(self.get_parameter('btn_arm').value)
        self.btn_stop = int(self.get_parameter('btn_stop').value)

        # Publishers
        self.pub_esc1 = self.create_publisher(UInt8, esc1_topic, 10)
        self.pub_esc2 = self.create_publisher(UInt8, esc2_topic, 10)

        # Service clients (micro-ROS on the Pico)
        self.cli_arm = self.create_client(Trigger, 'arm_escs')
        self.cli_stop = self.create_client(Trigger, 'stop_all')
        self.cli_gear_cw = self.create_client(Trigger, 'gear_one_rotation_cw')
        self.cli_gear_ccw = self.create_client(Trigger, 'gear_one_rotation_ccw')

        # Joy subscription
        self.sub_joy = self.create_subscription(Joy, joy_topic, self.on_joy, 10)

        # State
        self._last_buttons = []
        self._preset_idx = 0

        self.get_logger().info(
            f"Xbox→Pico bridge ready. Presets={self.esc_presets}, publish_both={self.publish_both}")

    # Helpers
    def _publish_esc_percent(self, p: int):
        p = max(0, min(100, int(p)))
        msg = UInt8(data=p)
        self.pub_esc1.publish(msg)
        if self.publish_both:
            self.pub_esc2.publish(msg)
        self.get_logger().info(f"ESC percent set to {p}%{' (both)' if self.publish_both else ''}")

    def _call_trigger(self, client: rclpy.node.Client, name: str):
        if not client.service_is_ready():
            client.wait_for_service(timeout_sec=0.0)
        if not client.service_is_ready():
            self.get_logger().warn(f"Service {name} not available")
            return
        req = Trigger.Request()
        future = client.call_async(req)
        # don't block spin; result will be logged when done
        future.add_done_callback(lambda f: self._on_trigger_done(f, name))

    def _on_trigger_done(self, future, name: str):
        try:
            res = future.result()
            self.get_logger().info(f"{name}: success={res.success} msg='{res.message}'")
        except Exception as e:
            self.get_logger().error(f"{name} call failed: {e}")

    def on_joy(self, msg: Joy):
        buttons = list(msg.buttons)
        # Initialize last_buttons on first message
        if not self._last_buttons:
            self._last_buttons = [0] * len(buttons)

        def pressed(idx: int) -> bool:
            return 0 <= idx < len(buttons) and self._last_buttons[idx] == 0 and buttons[idx] == 1

        # ESC preset up/down
        if pressed(self.btn_up):
            self._preset_idx = min(self._preset_idx + 1, len(self.esc_presets) - 1)
            self._publish_esc_percent(self.esc_presets[self._preset_idx])
        if pressed(self.btn_dn):
            self._preset_idx = max(self._preset_idx - 1, 0)
            self._publish_esc_percent(self.esc_presets[self._preset_idx])

        # Arm / Stop
        if pressed(self.btn_arm):
            self._call_trigger(self.cli_arm, 'arm_escs')
        if pressed(self.btn_stop):
            self._call_trigger(self.cli_stop, 'stop_all')

        # Gear one rotation CW/CCW
        if pressed(self.btn_cw):
            self._call_trigger(self.cli_gear_cw, 'gear_one_rotation_cw')
        if pressed(self.btn_ccw):
            self._call_trigger(self.cli_gear_ccw, 'gear_one_rotation_ccw')

        self._last_buttons = buttons


def main():
    rclpy.init()
    node = XboxPicoBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()


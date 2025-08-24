#!/usr/bin/env python3
import rclpy, serial, time
from rclpy.node import Node
from geometry_msgs.msg import Twist

PORT = "/dev/ttyACM0"  # ggf. anpassen
BAUD = 115200
MAX_LIN = 0.4  # m/s bei ±100% (kalibrieren!)
MAX_ANG = 1.2  # rad/s bei ±100% (kalibrieren!)
MIX = 0.5  # Drehanteil für Differential (0.5 = klassisch)


def clamp(x, a, b):
    return a if x < a else b if x > b else x


class TB6612Bridge(Node):
    def __init__(self):
        super().__init__("tb6612_bridge")
        try:
            self.ser = serial.Serial(PORT, BAUD, timeout=0.05)
            time.sleep(2.0)  # UNO-Autoreset
            self.get_logger().info(f"Opened {PORT} @ {BAUD}")
        except Exception as e:
            self.get_logger().error(f"Cannot open {PORT}: {e}")
            raise
        self.sub = self.create_subscription(Twist, "cmd_vel", self.on_cmd, 10)

    def on_cmd(self, msg: Twist):
        v = clamp(msg.linear.x / MAX_LIN, -1.0, 1.0)
        w = clamp(msg.angular.z / MAX_ANG, -1.0, 1.0)
        left = clamp(v - MIX * w, -1.0, 1.0)
        right = clamp(v + MIX * w, -1.0, 1.0)
        Lpct = int(round(left * 100))
        Rpct = int(round(right * 100))
        cmd = f"V {Lpct} {Rpct}\n".encode("ascii")
        try:
            self.ser.write(cmd)
        except Exception as e:
            self.get_logger().error(f"Write failed: {e}")


def main():
    rclpy.init()
    n = TB6612Bridge()
    rclpy.spin(n)


if __name__ == "__main__":
    main()

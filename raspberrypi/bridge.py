import rclpy, serial, math
from rclpy.node import Node
from geometry_msgs.msg import Twist


class Bridge(Node):
    def __init__(self):
        super().__init__("foxbot_bridge")
        dev = self.declare_parameter("port", "/dev/ttyACM0").value
        self.max_lin = self.declare_parameter("max_lin", 0.4).value  # m/s
        self.max_ang = self.declare_parameter("max_ang", 1.2).value  # rad/s
        self.ser = serial.Serial(dev, 115200, timeout=0.1)
        self.sub = self.create_subscription(Twist, "/cmd_vel", self.cb, 10)

    def cb(self, msg: Twist):
        v = max(-self.max_lin, min(self.max_lin, msg.linear.x))
        w = max(-self.max_ang, min(self.max_ang, msg.angular.z))
        # einfache Differential-Kinematik, normiert auf -100..100
        left = (v - 0.5 * w) / self.max_lin
        right = (v + 0.5 * w) / self.max_lin
        L = int(max(-1, min(1, left)) * 100)
        R = int(max(-1, min(1, right)) * 100)
        self.ser.write(f"V {L} {R}\n".encode("ascii"))


def main():
    rclpy.init()
    node = Bridge()
    rclpy.spin(node)


if __name__ == "__main__":
    main()

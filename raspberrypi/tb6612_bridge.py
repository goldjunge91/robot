#!/usr/bin/env python3
import glob, os, time, serial, rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

CANDIDATES = (
    *sorted(glob.glob('/dev/serial/by-id/*')),
    '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0'
)

def clamp(x,a,b): return a if x<a else b if x>b else x

class TB6612Bridge(Node):
    def __init__(self):
        super().__init__('tb6612_bridge')
        # ROS-Parameter
        self.declare_parameter('port', '')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('send_hz', 20.0)
        self.declare_parameter('max_lin', 0.3)   # m/s -> kalibrieren
        self.declare_parameter('max_ang', 1.0)   # rad/s -> kalibrieren
        self.declare_parameter('mix', 0.5)
        self.declare_parameter('cmd_topic', '/diff_cont/cmd_vel_unstamped') # This line is good

        self.port = self._pick_port(self.get_parameter('port').value)
        self.baud = int(self.get_parameter('baud').value)
        self.max_lin = float(self.get_parameter('max_lin').value)
        self.max_ang = float(self.get_parameter('max_ang').value)
        self.mix     = float(self.get_parameter('mix').value)

        self.ser = self._open_serial(self.port, self.baud)
        self.last_l = 0
        self.last_r = 0

        # self.sub = self.create_subscription(Twist, 'cmd_vel', self.on_cmd, 10)
        topic = self.get_parameter("cmd_topic").value
        self.sub = self.create_subscription(Twist, topic, self.on_cmd, 10)
        period = 1.0/float(self.get_parameter('send_hz').value)
        self.timer = self.create_timer(period, self.send_loop)

        self.get_logger().info(f'Bridge ready on {self.port} @ {self.baud}')

    def _pick_port(self, param_port: str) -> str:
        if param_port:
            return param_port
        for p in CANDIDATES:
            if os.path.exists(p):
                self.get_logger().info(f'Trying serial port: {p}')
                return p
        raise RuntimeError('No serial port found. Set -p port:=<path> or plug the device.')

    def _open_serial(self, port, baud):
        try:
            ser = serial.Serial(port, baud, timeout=0.05)
            time.sleep(2.0)  # UNO/CH340-Reset abwarten
            try:
                ser.write(b'PING\n')
            except Exception:
                pass
            return ser
        except Exception as e:
            self.get_logger().error(f'Cannot open {port}: {e}')
            raise

    def on_cmd(self, msg: Twist):
        v = clamp(msg.linear.x  / self.max_lin, -1.0, 1.0)
        w = clamp(msg.angular.z / self.max_ang, -1.0, 1.0)
        self.last_l = int(round(100 * clamp(v - self.mix*w, -1.0, 1.0)))
        self.last_r = int(round(100 * clamp(v + self.mix*w, -1.0, 1.0)))

    def send_loop(self):
        try:
            self.ser.write(f"V {self.last_l} {self.last_r}\n".encode('ascii'))
        except Exception as e:
            self.get_logger().error(f'Serial write failed: {e}')

def main():
    rclpy.init()
    n = TB6612Bridge()
    rclpy.spin(n)

if __name__ == '__main__':
    main()

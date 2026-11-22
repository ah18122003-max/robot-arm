import math

import serial
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory


JOINTS = ['base_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint']


class SerialBridge(Node):
    def __init__(self):
        super().__init__('arm_serial_bridge')
        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('servo_offset_deg', [90.0, 90.0, 90.0, 90.0])
        self.declare_parameter('servo_direction', [1.0, 1.0, 1.0, 1.0])

        port = self.get_parameter('port').value
        baud = self.get_parameter('baud').value
        self.offsets = list(self.get_parameter('servo_offset_deg').value)
        self.directions = list(self.get_parameter('servo_direction').value)

        self.serial_port = None
        try:
            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.get_logger().info(f'Connected to microcontroller on {port}')
        except serial.SerialException as exc:
            self.get_logger().error(f'Could not open serial port {port}: {exc}')
            raise

        self.subscription = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.trajectory_callback,
            10
        )

    def trajectory_callback(self, msg):
        if not msg.points:
            self.get_logger().warning('Received trajectory with no points')
            return

        positions = msg.points[-1].positions
        name_to_position = dict(zip(msg.joint_names, positions))
        if any(name not in name_to_position for name in JOINTS):
            self.get_logger().warning('Trajectory is missing one or more arm joints')
            return

        servo_angles = []
        for i, joint in enumerate(JOINTS):
            degrees = math.degrees(name_to_position[joint])
            servo = self.offsets[i] + self.directions[i] * degrees
            servo_angles.append(max(0, min(180, int(round(servo)))))

        line = ','.join(str(value) for value in servo_angles) + '\n'
        try:
            self.serial_port.write(line.encode('ascii'))
            self.get_logger().info(f'Sent servo angles: {line.strip()}')
        except serial.SerialException as exc:
            self.get_logger().error(f'Serial write failed: {exc}')

    def destroy_node(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

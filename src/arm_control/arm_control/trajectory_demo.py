import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


JOINTS = ['base_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint']


class TrajectoryDemo(Node):
    def __init__(self):
        super().__init__('trajectory_demo')
        self.publisher = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.timer = self.create_timer(2.0, self.publish_sequence)
        self.sequence = [
            [0.0, 0.0, 0.0, 0.0],
            [0.5, 0.4, -0.7, 0.3],
            [-0.5, -0.3, 0.8, -0.2],
            [0.0, 0.0, 0.0, 0.0],
        ]
        self.index = 0

    def publish_sequence(self):
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = self.sequence[self.index]
        point.time_from_start.sec = 2
        msg.points = [point]
        self.publisher.publish(msg)
        self.get_logger().info(f'Published joint target: {point.positions}')
        self.index = (self.index + 1) % len(self.sequence)


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

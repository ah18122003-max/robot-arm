import tkinter as tk

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


JOINTS = ['base_joint', 'shoulder_joint', 'elbow_joint', 'wrist_joint']
LIMITS = [(-180, 180), (-90, 90), (-115, 115), (-90, 90)]


class ArmGuiNode(Node):
    def __init__(self):
        super().__init__('arm_gui')
        self.publisher = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)

    def send_angles(self, degrees):
        msg = JointTrajectory()
        msg.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = [value * 3.141592653589793 / 180.0 for value in degrees]
        point.time_from_start.sec = 2
        msg.points = [point]
        self.publisher.publish(msg)
        self.get_logger().info(f'GUI command sent: {degrees} degrees')


def main(args=None):
    rclpy.init(args=args)
    node = ArmGuiNode()
    root = tk.Tk()
    root.title('ROS 2 Robotic Arm Controller')
    root.geometry('440x390')
    sliders = []

    tk.Label(root, text='Joint position control', font=('Arial', 16, 'bold')).pack(pady=10)
    for name, limits in zip(JOINTS, LIMITS):
        frame = tk.Frame(root)
        frame.pack(fill='x', padx=12, pady=5)
        tk.Label(frame, text=name, width=17, anchor='w').pack(side='left')
        slider = tk.Scale(frame, from_=limits[0], to=limits[1],
                          orient='horizontal', length=240)
        slider.set(0)
        slider.pack(side='right')
        sliders.append(slider)

    def publish():
        node.send_angles([slider.get() for slider in sliders])
        rclpy.spin_once(node, timeout_sec=0.0)

    tk.Button(root, text='Publish trajectory', command=publish,
              bg='#2563eb', fg='white', padx=12, pady=8).pack(pady=18)
    tk.Label(root, text='Angles are converted to radians before publishing.').pack()

    try:
        root.mainloop()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

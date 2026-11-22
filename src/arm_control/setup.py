from setuptools import setup

package_name = 'arm_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='Trajectory publisher, GUI and serial bridge for a ROS 2 robotic arm.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'trajectory_demo = arm_control.trajectory_demo:main',
            'arm_gui = arm_control.gui:main',
            'serial_bridge = arm_control.serial_bridge:main',
        ],
    },
)

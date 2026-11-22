# ROS 2 Robotic Arm — URDF, Gazebo, RViz2 & Arduino

A GitHub-ready starter implementation for the Robotics — Advanced ROS 2 assignment.
Target stack: **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**.

## 1. Project structure

```text
ros2_robotic_arm_github/
├── src/
│   ├── arm_description/
│   │   ├── config/controllers.yaml
│   │   ├── launch/simulation.launch.py
│   │   ├── rviz/arm.rviz
│   │   ├── urdf/robot.urdf.xacro
│   │   ├── worlds/empty.sdf
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   └── arm_control/
│       ├── arm_control/gui.py
│       ├── arm_control/trajectory_demo.py
│       ├── arm_control/serial_bridge.py
│       ├── resource/arm_control
│       ├── setup.cfg
│       ├── setup.py
│       └── package.xml
├── firmware/arm_servos/arm_servos.ino
├── .gitignore
└── LICENSE
```

## 2. Mechanical model

The model uses four revolute joints:
- `base_joint`: base rotation around Z.
- `shoulder_joint`: shoulder pitch around Y.
- `elbow_joint`: elbow pitch around Y.
- `wrist_joint`: wrist pitch around Y.

Dimensions from the assignment are represented in metres:
- Base height: 0.08 m
- L1: 0.12 m
- L2: 0.15 m
- L3: 0.09 m
- End-effector/gripper length: 0.06 m

The links use simple box/cylinder geometry. Each link has visual, collision and inertial elements.

## 3. Install dependencies

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-desktop \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-ros-gz \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-ros2-control \
  ros-jazzy-controller-manager \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-joint-trajectory-controller \
  python3-colcon-common-extensions \
  python3-pip

python3 -m pip install --user pyserial
```

> Package availability can vary with the ROS/Gazebo repository configuration. The simulation launch uses `gz_ros2_control` with Gazebo Harmonic. Confirm that the installed Gazebo version and `gz_ros2_control` package are compatible.

## 4. Build the workspace

From the repository root:

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 5. Run Gazebo and RViz2

```bash
ros2 launch arm_description simulation.launch.py
```

The launch file starts Gazebo, publishes the robot description, spawns the arm, starts the controller manager, and launches RViz2. The joint state broadcaster publishes `/joint_states`, allowing RViz2 to follow the simulated joint positions.

Check the controllers:

```bash
ros2 control list_controllers
```

Expected active controllers:
- `joint_state_broadcaster`
- `arm_controller`

## 6. Move the simulated arm

In a second terminal:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run arm_control trajectory_demo
```

Or use the slider GUI:

```bash
ros2 run arm_control arm_gui
```

Both publish `trajectory_msgs/msg/JointTrajectory` to:

```text
/arm_controller/joint_trajectory
```

Joint order must remain:
`base_joint`, `shoulder_joint`, `elbow_joint`, `wrist_joint`.

Example direct command:

```bash
ros2 topic pub --once /arm_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: [base_joint, shoulder_joint, elbow_joint, wrist_joint],
    points: [{positions: [0.0, 0.5, -0.5, 0.2],
    time_from_start: {sec: 2, nanosec: 0}}]}"
```

## 7. Arduino hardware

### Example wiring

| Arduino Uno pin | Connection |
|---|---|
| D3 | Base servo signal |
| D5 | Shoulder servo signal |
| D6 | Elbow servo signal |
| D9 | Wrist servo signal |
| GND | Common ground with external servo supply |

Use an external regulated 5–6 V supply sized for the servos. **Do not power multiple servos from the Arduino 5 V pin.** Connect the external supply ground to Arduino GND. Verify each servo's voltage/current requirements.

### Serial protocol

The ROS 2 bridge sends one line per command:

```text
90,110,70,90\n
```

Values are servo angles in degrees, clamped to 0–180. The Arduino firmware parses four comma-separated integer values and writes them to the servos.

Upload `firmware/arm_servos/arm_servos.ino` using the Arduino IDE.

### Run the hardware bridge

Close the Arduino Serial Monitor first. Then:

```bash
ros2 run arm_control serial_bridge --ros-args \
  -p port:=/dev/ttyACM0 \
  -p baud:=115200
```

Change `/dev/ttyACM0` to the actual serial device (often `/dev/ttyUSB0` or `/dev/ttyACM0`).

The bridge subscribes to the same `/arm_controller/joint_trajectory` topic, so the same published trajectory is sent to simulation and, when connected, to the physical servos.

**Servo calibration is essential:** the example mapping assumes 90 degrees is the neutral position for each joint and maps joint radians to servo degrees using `90 + degrees`. Adjust `servo_direction` and `servo_offset_deg` in `serial_bridge.py` to match the actual mechanism. Never force a servo against a mechanical stop.

## 8. Test checklist

- [ ] URDF contains at least four revolute joints.
- [ ] Every link includes visual, collision and inertial properties.
- [ ] Robot appears in RViz2 with `base_link` as fixed frame.
- [ ] Robot spawns in Gazebo.
- [ ] `arm_controller` and `joint_state_broadcaster` are active.
- [ ] A trajectory command moves the model in Gazebo and RViz2.
- [ ] Serial bridge starts and receives trajectory commands.
- [ ] At least two servo motors respond to commands.
- [ ] Full pipeline is demonstrated: GUI → ROS 2 trajectory → Gazebo/RViz2 and serial → Arduino → servos.

## 9. Important implementation notes

This repository is a project starter and has **not been physically tested on your specific computer, Gazebo installation, Arduino board or servo mechanics**. Validate the launch and controller configuration in your installed ROS 2 Jazzy environment, and calibrate the hardware before connecting the arm.

The simulation uses `gz_ros2_control`; the hardware bridge is a separate subscriber to the same trajectory topic. The simulated controller and physical bridge can therefore receive the same command. Do not connect the real mechanism until joint directions, offsets, travel limits and emergency-stop behavior have been checked.

## 10. GitHub

Create a new GitHub repository, then from this folder:

```bash
git init
git add .
git commit -m "Add ROS 2 robotic arm assignment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL.

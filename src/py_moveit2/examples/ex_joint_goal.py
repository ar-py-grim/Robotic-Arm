#!/usr/bin/env python3

"""
Example of moving robotic arm to a joint configuration.
`ros2 run pymoveit2 ex_joint_goal.py --ros-args -p joint_positions:="[]"`
"""

# ensure gripper is close before running this script

from threading import Thread
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from pymoveit2 import MoveIt2
from pymoveit2.robots import bot

"""
Example of moving to a joint configuration.
`ros2 run pymoveit2 ex_joint_goal.py --ros-args -p joint_positions:="[, , , , ]"`
"""

# home joint_positions [ 4.2650327714000014e-11, -2.0948842660573064e-10, 3.154809746774845e-11, -1.4490886268703207e-07, -1.9490187241899548e-11]

def main():
    rclpy.init()

    # Create node for this example
    node = Node("ex_joint_goal")

    # Declare parameter for joint positions
    node.declare_parameter(
        # can be accesed using /joint_states topic

        "joint_positions",
         [  -0.4200313347283844,
            -0.7094722304748737,
            -6.7680794302305e-10,
            0.7949439333283355,
            -6.768363647324804e-10
        ],)

    # Create callback group that allows execution of callbacks in parallel without restrictions
    callback_group = ReentrantCallbackGroup()

    # Create MoveIt 2 interface
    moveit2 = MoveIt2(
        node=node,
        joint_names = bot.joint_names(),
        base_link_name = bot.base_link_name(),
        end_effector_name = bot.end_effector_name(),
        group_name = bot.MOVE_GROUP_ARM,
        callback_group=callback_group,
    )

    # Spin the node in background thread(s)
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True, args=())
    executor_thread.start()

    # Get parameter
    joint_positions = (
        node.get_parameter("joint_positions").get_parameter_value().double_array_value
    )

    # Move to joint configuration
    node.get_logger().info(f"Moving to {{joint_positions: {list(joint_positions)}}}")
    moveit2.move_to_configuration(joint_positions)
    moveit2.wait_until_executed()

    rclpy.shutdown()
    exit(0)


if __name__ == "__main__":
    main()

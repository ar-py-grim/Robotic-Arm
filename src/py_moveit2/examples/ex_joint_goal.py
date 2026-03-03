#!/usr/bin/env python3

"""
Example of moving to a joint configuration.
- ros2 run pymoveit2 ex_joint_goal.py --ros-args -p joint_positions:="[]"
"""

from threading import Thread
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from pymoveit2 import MoveIt2
from pymoveit2.robots import bot

def main():
    rclpy.init()

    node = Node("ex_joint_goal")

    node.declare_parameter("joint_positions", value=[-0.0856427586014128,
                                                     -0.24535938599319973, 0.2351244067945224])

    callback_group = ReentrantCallbackGroup()

    moveit2 = MoveIt2(
        node=node,
        joint_names=bot.arm_joint_names(),
        base_link_name=bot.base_link_name(),
        end_effector_name=bot.end_effector_name(),
        group_name=bot.MOVE_GROUP_ARM,
        callback_group=callback_group,
        follow_joint_trajectory_action_name="arm_controller/follow_joint_trajectory",
        execute_via_moveit=True
    )

    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True, args=())
    executor_thread.start()
    node.create_rate(1.0).sleep()

    moveit2.max_velocity = 0.5
    moveit2.max_acceleration = 0.5

    joint_positions = (
        node.get_parameter("joint_positions").get_parameter_value().double_array_value
    )

    node.get_logger().info(f"Moving to {{joint_positions: {list(joint_positions)}}}")
    moveit2.move_to_configuration(joint_positions)
    moveit2.wait_until_executed()

    rclpy.shutdown()
    executor_thread.join()
    exit(0)


if __name__ == "__main__":
    main()
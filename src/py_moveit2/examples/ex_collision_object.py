#!/usr/bin/env python3

from os import path
from threading import Thread
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from pymoveit2 import MoveIt2
from pymoveit2.robots import bot

def main():
    rclpy.init()

    node = Node("upload_collision_scene")
    node.declare_parameter("action", "add")

    pkg_path = path.dirname(path.realpath(__file__))
    assets_path = path.join(pkg_path, "..", "assets")
    table_mesh = path.join(assets_path, "table_4_scaled_full.stl")
    rod_mesh = path.join(assets_path, "rod_fixed_0.1r_0.8h_origin_bottom.stl")

    callback_group = ReentrantCallbackGroup()

    moveit2 = MoveIt2(
        node=node,
        joint_names=bot.joint_names(),
        base_link_name=bot.base_link_name(),
        end_effector_name=bot.end_effector_name(),
        group_name=bot.MOVE_GROUP_ARM,
        callback_group=callback_group,
    )

    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True)
    executor_thread.start()

    action = node.get_parameter("action").get_parameter_value().string_value
    # frame_id = bot.base_link_name()
    frame_id = "world"

    if action == "add":
        # Table 1
        moveit2.add_collision_mesh(
            filepath=table_mesh,
            id="table_1",
            position=[1.0, 1.5, 0.0],
            quat_xyzw=[0.0, 0.0, 0.0, 1],
            frame_id=frame_id,
        )
        # Table 2
        moveit2.add_collision_mesh(
            filepath=table_mesh,
            id="table_2",
            position=[1.0, -1.1, 0.0],
            quat_xyzw=[0.0, 0.0, -0.7071, 0.7071],
            frame_id=frame_id,
        )
        # Rod
        moveit2.add_collision_mesh(
            filepath=rod_mesh,
            id="rod",
            position=[1.5, 0.0, 1.0],
            quat_xyzw=[0.0, 0.0, -0.7071, 0.7071],
            frame_id=frame_id,
        )
        node.get_logger().info("Environment objects added to planning scene.")
    else:
        moveit2.remove_collision_mesh(id="table_1")
        moveit2.remove_collision_mesh(id="table_2")
        moveit2.remove_collision_mesh(id="rod")
        node.get_logger().info("Environment objects removed.")

    rclpy.shutdown()
    exit(0)


if __name__ == "__main__":
    main()

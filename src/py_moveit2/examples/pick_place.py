#!/usr/bin/env python3

from threading import Thread
from os import path
import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from pymoveit2 import MoveIt2
from pymoveit2 import GripperInterface
from pymoveit2.robots import bot
from linkattacher_msgs.srv import AttachLink, DetachLink
from gazebo_msgs.srv import GetEntityState


APPROACH_ROD = [-0.0856427586014128, -0.24535938599319973, 0.2351244067945224]
GRASP_ROD    = [-0.0916, -0.4353, 0.4354]
HOME         = [0.0, 0.0, 0.0]
DROP         = [-1.6158905741270804, -0.5614629167025784, 0.5754775872890798]
HOME1        = [-1.5916130092949556, 0.023094374493890513, -0.016678305364773216]


def main():
    rclpy.init()
    node = Node("grasp_and_close")
    callback_group = ReentrantCallbackGroup()

    moveit2 = MoveIt2(
        node=node,
        joint_names=bot.arm_joint_names(),
        base_link_name=bot.base_link_name(),
        end_effector_name=bot.end_effector_name(),
        group_name=bot.MOVE_GROUP_ARM,
        execute_via_moveit=True,
        callback_group=callback_group,
        follow_joint_trajectory_action_name="arm_controller/follow_joint_trajectory",
    )
    moveit2.max_velocity = 0.3
    moveit2.max_acceleration = 0.3

    gripper = GripperInterface(
        node=node,
        gripper_joint_names=bot.gripper_joint_names(),
        open_gripper_joint_positions=bot.OPEN_GRIPPER_PICK_JOINT_POSITIONS,
        closed_gripper_joint_positions=bot.CLOSED_GRIPPER_PICK_JOINT_POSITIONS,
        gripper_group_name=bot.MOVE_GROUP_GRIPPER,
        callback_group=callback_group,
        follow_joint_trajectory_action_name="gripper_controller/follow_joint_trajectory",
        skip_planning=True,
    )

    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True)
    executor_thread.start()
    node.create_rate(2.0).sleep()

    attach_client = node.create_client(AttachLink, '/ATTACHLINK')
    detach_client = node.create_client(DetachLink, '/DETACHLINK')
    model_state_client = node.create_client(GetEntityState, '/gazebo/get_entity_state')
    attach_client.wait_for_service()
    detach_client.wait_for_service()
    model_state_client.wait_for_service()

    pkg_path = path.dirname(path.realpath(__file__))
    assets_path = path.join(pkg_path, "..", "assets")
    table_mesh = path.join(assets_path, "table.stl")

    node.get_logger().info("Moving to approach position")
    moveit2.move_to_configuration(APPROACH_ROD)
    if not moveit2.wait_until_executed():
        node.get_logger().error("Failed to reach approach position")
        rclpy.shutdown(); executor_thread.join(); exit(1)

    node.get_logger().info("Opening gripper")
    gripper.open()
    gripper.wait_until_executed()

    node.get_logger().info("Moving to grasp position")
    moveit2.move_to_configuration(GRASP_ROD)
    if not moveit2.wait_until_executed():
        node.get_logger().error("Failed to reach grasp position")
        rclpy.shutdown(); executor_thread.join(); exit(1)

    node.create_rate(2.0).sleep()

    node.get_logger().info("Closing gripper")
    gripper.close()
    gripper.wait_until_executed()
    node.get_logger().info("Object grasped.")

    attach_req = AttachLink.Request()
    attach_req.model1_name = 'roboticarm'
    attach_req.link1_name  = 'gripper_right'
    attach_req.model2_name = 'rod'
    attach_req.link2_name  = 'link'
    attach_client.call(attach_req)

    moveit2.attach_collision_object(
        id="rod",
        link_name=bot.end_effector_name(),
        touch_links=["gripper_left", "gripper_right", "claw_support"],
    )
    moveit2.remove_collision_object(id="table_1")
    moveit2.remove_collision_object(id="table_2")
    node.create_rate(2.0).sleep()

    node.get_logger().info("Returning to home position")
    moveit2.move_to_configuration(HOME)
    if not moveit2.wait_until_executed():
        node.get_logger().error("Failed to reach home position")
        rclpy.shutdown(); executor_thread.join(); exit(1)

    node.get_logger().info("Moving to drop position")
    moveit2.move_to_configuration(DROP)
    if not moveit2.wait_until_executed():
        node.get_logger().error("Failed to reach drop position")
        rclpy.shutdown(); executor_thread.join(); exit(1)


    detach_req = DetachLink.Request()
    detach_req.model1_name = 'roboticarm'
    detach_req.link1_name  = 'gripper_right'
    detach_req.model2_name = 'rod'
    detach_req.link2_name  = 'link'
    detach_client.call(detach_req)

    moveit2.detach_collision_object(id="rod")
    moveit2.remove_collision_object(id="rod")
    node.create_rate(1.0).sleep()

    node.get_logger().info("Opening gripper")
    gripper.open()
    gripper.wait_until_executed()
    node.get_logger().info("Rod released.")

    state_req = GetEntityState.Request()
    state_req.name = 'rod'
    state_req.reference_frame = 'world'
    state_res = model_state_client.call(state_req)
    rod_pos = state_res.state.pose.position
    rod_ori = state_res.state.pose.orientation
    node.get_logger().info(f"Rod position: x={rod_pos.x:.3f}, y={rod_pos.y:.3f}, z={rod_pos.z:.3f}")

    rod_mesh = path.join(assets_path, "rod.stl")
    moveit2.add_collision_mesh(
        filepath=rod_mesh,
        id="rod",
        position=[rod_pos.x, rod_pos.y, rod_pos.z],
        quat_xyzw=[rod_ori.x, rod_ori.y, rod_ori.z, rod_ori.w],
    )

    # Restoring planning scene
    moveit2.add_collision_mesh(
        filepath=table_mesh,
        id="table_1",
        position=[0.0, 2.0, 0.0],
        quat_xyzw=[0.0, 0.0, 0.0, 1.0],
    )
    moveit2.add_collision_mesh(
        filepath=table_mesh,
        id="table_2",
        position=[2.0, 0.0, 0.0],
        quat_xyzw=[0.0, 0.0, -0.7071, 0.7071],
    )
    node.create_rate(2.0).sleep()

    node.get_logger().info("Returning to home position")
    moveit2.move_to_configuration(HOME1)
    if not moveit2.wait_until_executed():
        node.get_logger().error("Failed to reach home position")
        rclpy.shutdown(); executor_thread.join(); exit(1)
    node.get_logger().info("Home reached.")

    gripper.close()
    gripper.wait_until_executed()

    rclpy.shutdown()
    executor_thread.join()
    exit(0)


if __name__ == "__main__":
    main()
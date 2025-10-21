from typing import List

MOVE_GROUP_ARM: str = "arm"
MOVE_GROUP_GRIPPER: str = "gripper"
                                            # yaw angles 
                                        # in order as in gripper_joint_names()
OPEN_GRIPPER_JOINT_POSITIONS: List[float] = [-1.57, 1.57]
CLOSED_GRIPPER_JOINT_POSITIONS: List[float] = [0.0, 0.0]

def joint_names() -> List[str]:

# order of joints found using ros2 topic echo /joint_states

    return["joint_1",
        "joint_2",
        "joint_4",
        "joint_3",
        "joint_5_mimic"]
        # "joint_5"]


def base_link_name() -> str:
    return "base_link"

def end_effector_name() -> str:
    return "gripper_right"

def gripper_joint_names() -> List[str]:
    return ["joint_4", 
            "joint_5_mimic"]
            # "joint_5"]
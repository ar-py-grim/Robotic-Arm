from typing import List

MOVE_GROUP_ARM: str = "arm"
MOVE_GROUP_GRIPPER: str = "gripper"
                                        
# yaw angles in order as in gripper_joint_names()
OPEN_GRIPPER_JOINT_POSITIONS: List[float] = [-1.57]
CLOSED_GRIPPER_JOINT_POSITIONS: List[float] = [0.0]
OPEN_GRIPPER_PICK_JOINT_POSITIONS: List[float] = [-0.5]
CLOSED_GRIPPER_PICK_JOINT_POSITIONS: List[float] = [-0.1]

def arm_joint_names() -> List[str]:

# order of joints found using ros2 topic echo /joint_states
    return["joint_1",
        "joint_2",
        "joint_3",
        ]

def base_link_name() -> str:
    return "base_link"

def end_effector_name() -> str:
    return "gripper_right"

def gripper_joint_names() -> List[str]:
    return ["joint_4"]

def joint_names() -> List[str]:
    """All robot joints"""
    return arm_joint_names() + gripper_joint_names()
import os
from launch import LaunchDescription
from moveit_configs_utils import MoveItConfigsBuilder
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_param_builder import ParameterBuilder
from ament_index_python.packages import get_package_share_directory

# https://github.com/moveit/moveit2/blob/humble/moveit_ros/moveit_servo/launch/servo_example.launch.py

# https://github.com/moveit/moveit2_tutorials/blob/humble/doc/examples/realtime_servo/launch/servo_cpp_interface_demo.launch.py

def generate_launch_description():

    is_sim = LaunchConfiguration('is_sim')
    is_sim_arg = DeclareLaunchArgument('is_sim', default_value='True')
    
    moveit_dir = get_package_share_directory("arm_moveit")
    rviz_config = os.path.join(moveit_dir, "config/moveit.rviz")
    ompl_config = os.path.join(moveit_dir, "config/ompl_planning.yaml")
    servo_params = (
        ParameterBuilder("moveit_servo")
        .yaml(
            parameter_namespace="moveit_servo",
            file_path=os.path.join(moveit_dir, "config/arm_servo.yaml"),
        )
        .to_dict()
    )

    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01
    }

    planning_scene_monitor_config = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True
    }

    moveit_config = (
        MoveItConfigsBuilder("robotic arm", package_name="arm_moveit")
        .robot_description(file_path=os.path.join(
            get_package_share_directory("demo_arm_description"),
            "urdf","project.urdf.xacro")
        )
        .robot_description_semantic(file_path=os.path.join(moveit_dir,"config/bot.srdf"))
        .trajectory_execution(file_path=os.path.join(moveit_dir,"config/moveit_controllers.yaml"))
        .robot_description_kinematics(file_path=os.path.join(moveit_dir,"config/kinematics.yaml"))
        .joint_limits(file_path=os.path.join(moveit_dir,"config/joint_limits.yaml"))
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict(), 
                    {'use_sim_time': is_sim},
                    {'publish_robot_description_semantic': True},
                    {'ompl': ompl_config},
                    {'planning_pipelines': ['ompl']},
                    trajectory_execution,
                    planning_scene_monitor_config,
                    ],
        arguments=["--ros-args", "--log-level", "info"],
    )

    # Servo node for realtime control
    servo_node = Node(
        package="moveit_servo",
        executable="servo_node_main",
        parameters=[
            servo_params,
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
        ],
        output="screen",
        arguments=["--ros-args", "--log-level", "info"],
    )

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
        ],
    )

    return LaunchDescription(
        [
            is_sim_arg,
            move_group_node, 
            rviz_node,
            servo_node,
        ]
    )
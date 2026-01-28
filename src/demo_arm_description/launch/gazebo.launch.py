import os
from os import pathsep
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, RegisterEventHandler
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    
    arm_description_dir = get_package_share_directory('demo_arm_description')
    arm_description_share = get_package_prefix('demo_arm_description')
    gazebo_ros_dir = get_package_share_directory('gazebo_ros')
    rviz_config_path = os.path.join(arm_description_dir, 'rviz', 'rviz_config.rviz')

    urdf_path = DeclareLaunchArgument(name='model', default_value=os.path.join(
                                        arm_description_dir, 'urdf', 'project.urdf.xacro'
                                        ),
                                      description='Absolute path to robot urdf file'
    )

    model_path = os.path.join(arm_description_dir, "models")
    model_path += pathsep + os.path.join(arm_description_share, "share")

    env_var = SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path)

    world = os.path.join(
        get_package_share_directory('demo_arm_description'),
        'worlds',
        'pick_place_scene.world'
    )

    robot_description = ParameterValue(Command(['xacro ', LaunchConfiguration('model')]),value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    start_gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    start_gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros_dir, 'launch', 'gzclient.launch.py')
        )
    )

    spawn_robot = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        arguments=['-entity', 'roboticarm', '-topic', 'robot_description'],
        output='screen'
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    arm_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
    )

    gripper_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager", "/controller_manager"],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path]
    )

    return LaunchDescription([
        env_var,
        urdf_path,
        start_gazebo_server,
        start_gazebo_client,
        robot_state_publisher_node,
        spawn_robot,
        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=spawn_robot,
                on_exit=[joint_state_broadcaster_spawner],)),

        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=joint_state_broadcaster_spawner,
                on_exit=[arm_controller_spawner],)),

        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=arm_controller_spawner,
                on_exit=[gripper_controller_spawner],)),

        RegisterEventHandler(
            event_handler=OnProcessExit(
                target_action=gripper_controller_spawner,
                on_exit=[rviz_node],)),
        
    ])
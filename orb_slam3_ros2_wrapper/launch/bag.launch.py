#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.actions import IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, FindExecutable, TextSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from nav2_common.launch import RewrittenYaml

def generate_launch_description():

#---------------------------------------------

    #Essential_paths
    orb_wrapper_pkg = get_package_share_directory('orb_slam3_ros2_wrapper')
#---------------------------------------------

    # LAUNCH ARGS
    bag_path = LaunchConfiguration('bag_path')
    declare_bag_path = DeclareLaunchArgument(
        name='bag_path',
        default_value=None,  # Make it required
        description='Path to the rosbag2')

    robot_namespace =  LaunchConfiguration('robot_namespace')
    declare_robot_namespace = DeclareLaunchArgument('robot_namespace', default_value="robot",
        description='The namespace of the robot')

    config_file_path =  LaunchConfiguration('config_file_path')
    declare_config_file_path = DeclareLaunchArgument(
        'config_file_path',
        default_value="/root/colcon_ws/src/orb_slam3_ros2_wrapper/params/gazebo_rgbd.yaml",
        description='Path for the yaml of ORB-SLAM3')

    executable =  LaunchConfiguration('executable')
    declare_executable = DeclareLaunchArgument(
        'executable',
        default_value="rgbd",
        description='Executable for ROS2')


#---------------------------------------------

    def all_nodes_launch(context, executable, robot_namespace, config_file_path):
        vocabulary_file_path = "/home/orb/ORB_SLAM3/Vocabulary/ORBvoc.txt"

        params_file = LaunchConfiguration('params_file')
        declare_params_file = DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(orb_wrapper_pkg, 'params', 'bag-ros-params.yaml'),
            description='Full path to the ROS2 parameters file to use for all launched nodes')

        base_frame = ""
        if(robot_namespace.perform(context) == ""):
            base_frame = ""
        else:
            base_frame = robot_namespace.perform(context) + "/"

        param_substitutions = {
            # 'robot_base_frame': base_frame + 'base_footprint',
            # 'odom_frame': base_frame + 'odom'
            }


        configured_params = RewrittenYaml(
            source_file=params_file,
            root_key=robot_namespace.perform(context),
            param_rewrites=param_substitutions,
            convert_types=True)
        
        orb_slam3_node = Node(
            package='orb_slam3_ros2_wrapper',
            executable=executable,
            output='screen',
            # prefix=["gdbserver localhost:3000"],
            namespace=robot_namespace.perform(context),
            arguments=[vocabulary_file_path, config_file_path],
            parameters=[configured_params])

        return [declare_params_file, orb_slam3_node]

    opaque_function = OpaqueFunction(function=all_nodes_launch, args=[executable, robot_namespace, config_file_path])
#---------------------------------------------

    execute_bag = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'play',
            bag_path,
            '--clock',
            '--rate', '0.3'
        ],
        output='screen'
    )

    return LaunchDescription([
        declare_bag_path,
        declare_executable,
        declare_robot_namespace,
        declare_config_file_path,
        execute_bag,
        opaque_function
    ])

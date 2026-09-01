import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node

import xacro


def generate_launch_description():

    package_share = get_package_share_directory(
        'amr_description'
    )

    gazebo_package_share = get_package_share_directory(
        'gazebo_ros'
    )

    robot_file = os.path.join(
        package_share,
        'urdf',
        'amr.urdf.xacro'
    )

    world_file = os.path.join(
        package_share,
        'worlds',
        'warehouse.world'
    )

    robot_description = xacro.process_file(
        robot_file
    ).toxml()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                gazebo_package_share,
                'launch',
                'gazebo.launch.py'
            )
        ),
        launch_arguments={
            'world': world_file
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'robot_description': robot_description
            }
        ]
    )

    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'custom_amr',
            '-topic', 'robot_description',
            '-x', '0',
            '-y', '0',
            '-z', '0.11'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_robot
    ])
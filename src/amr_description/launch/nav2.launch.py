import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    package_share = get_package_share_directory(
        'amr_description'
    )

    nav2_bringup_share = get_package_share_directory(
        'nav2_bringup'
    )

    map_file = os.path.expanduser(
        '~/dynamic_nav_ws/maps/warehouse_map.yaml'
    )

    params_file = os.path.join(
        package_share,
        'config',
        'nav2_params.yaml'
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_share,
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'map': map_file,
            'use_sim_time': 'True',
            'params_file': params_file,
            'autostart': 'True'
        }.items()
    )

    return LaunchDescription([
        nav2
    ])


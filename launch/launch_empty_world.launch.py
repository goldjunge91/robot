import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    package_name = "robot"
    pkg_share = get_package_share_directory(package_name)

    worlds_dir = os.path.join(pkg_share, "worlds")
    models_dir = os.path.join(pkg_share, "models")

    # Choose a world file that exists in the repo; fallback to empty.world if not present
    preferred_world = os.path.join(worlds_dir, "office_small.world")
    if not os.path.exists(preferred_world):
        # common system empty world locations are handled by gazebo if absolute path is given
        preferred_world = ""  # let gazebo use its default if not present

    # Set environment variables for this launch so Gazebo can find worlds and models in the package
    # Use SetEnvironmentVariable so changes apply to processes started by this launch only
    set_resource = SetEnvironmentVariable(
        name="GAZEBO_RESOURCE_PATH",
        value=(os.environ.get("GAZEBO_RESOURCE_PATH", "") + os.pathsep + worlds_dir)
        if worlds_dir
        else os.environ.get("GAZEBO_RESOURCE_PATH", ""),
    )

    set_model = SetEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=(os.environ.get("GAZEBO_MODEL_PATH", "") + os.pathsep + models_dir)
        if models_dir
        else os.environ.get("GAZEBO_MODEL_PATH", ""),
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [
                os.path.join(
                    get_package_share_directory("gazebo_ros"), "launch", "gazebo.launch.py"
                )
            ]
        ),
        launch_arguments={"world": preferred_world}.items(),
    )

    ld = LaunchDescription()
    ld.add_action(set_resource)
    ld.add_action(set_model)
    ld.add_action(gazebo_launch)

    return ld

from setuptools import setup, find_packages

package_name = 'robot_bridge'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(include=[package_name, f'{package_name}.*']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/robot_bridge']),
        ('share/robot_bridge', ['package.xml']),
        ('share/robot_bridge/launch', ['launch/robot_pi_bridge.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='marco',
    maintainer_email='unknown@example.com',
    description='TB6612 open-loop bridge (Pi->Arduino) as ROS 2 executable.',
    license='MIT',
    tests_require=[],
    entry_points={
        'console_scripts': [
            'tb6612_bridge = robot_bridge.tb6612_bridge:main',
        ],
    },
)

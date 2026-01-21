from setuptools import find_packages, setup

package_name = 'robot_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pi',
    maintainer_email='pi@todo.todo',
    description='TB6612 open-loop bridge.',
    license='MIT',
    tests_require=['pytest'],
#     entry_points={
#         'console_scripts': [
#             'tb6612_bridge = robot_bridge.tb6612_bridge:main',
#         ],
#     },
# )
    entry_points={
        'console_scripts': [
            'tb6612_bridge = robot_bridge.tb6612_bridge:main',
            'xbox_pico_bridge = robot_bridge.xbox_pico_bridge:main',
        ],
    },
)

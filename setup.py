from setuptools import setup, find_packages

setup(
    name="mrobot-controller",
    version="0.1.0",
    author="Amnon Paz",
    author_email="pazamnonl@gmail.com",
    description="Controller for the mRobot (Based on Zero Bot Pro)",
    long_description=open("Readme.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["docker", "config"]),
    install_requires=[
        "PyGObject",
    ],
    entry_points={
        'console_scripts': [
            'mrobot-controller=mrobot_controller.app:main',
        ],
    },
)

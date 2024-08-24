from setuptools import setup, find_packages

setup(
    name="video_streamer",
    version="0.1.0",
    description="A Python application for streaming v4l over RTP using GStreamer",
    author="Amnon Paz",
    author_email="pazamnonl@gmail.com",
    packages=find_packages(),
    install_requires=[
        "PyGObject",
    ],
    entry_points={
        'console_scripts': [
            'video-streamer=video_streamer.app:main',
        ],
    },
)

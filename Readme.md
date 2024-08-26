# mRobot Controller

Python application for controlling the [Zero Bot Pro](https://hackaday.io/project/25092-zerobot-raspberry-pi-zero-fpv-robot)

## Features

- **Video Streaming**: Streams video from a specified device using GStreamer.
- **Custom Configuration**: Load configuration from a JSON file, including video and server settings.
- **TBD**: WebSocket interface for controlling the motor, LEDs, and other peripherals

### Prerequisites

- Python 3.6 or later
- GStreamer
  With base, good and bad plugins packages
- PyGObject

## Installation

```bash
pip install --no-cache-dir -r requirements.txt
pip install .
```

See [meta-mrobot Yocto layer](https://github.com/amnonpaz/meta-mrobot) for integrating with Yocto.

## Usage

To run the application, use the following command:

```bash
python main.py path/to/your/config.json
```

Running with docker:
```bash
docker-compose -f docker/docker-compose.yml up
```

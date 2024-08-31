# mRobot Controller

Python application for controlling the [Zero Bot Pro](https://hackaday.io/project/25092-zerobot-raspberry-pi-zero-fpv-robot) (Original software [here](https://github.com/CoretechR/ZeroBot))

## Features

- **Custom Configuration**: Load configuration from a JSON file, including video and server settings.
- **Video Streaming**: Streams video from a specified device using GStreamer.
- **WebSocket server**:
	For controlling:
    - Video stream start/stop
	- Motors *TBD*
	- LEDs *TBD*

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
python -m mrobot_controller.app config/default.json
```

Running with docker:
```bash
docker-compose -f docker/docker-compose.yml up
```


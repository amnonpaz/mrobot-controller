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

- Python 3.6 or later, with:
    - PyGObject
    - websockets
    - asyncio
    - msgpack (for serializing/deserializing messages)
- GStreamer
  With base, good, bad and ugly plugins packages

## Installation

```bash
pip install --no-cache-dir -r requirements.txt
pip install .
```

See [meta-mrobot Yocto layer](https://github.com/amnonpaz/meta-mrobot) for integrating with Yocto.

## Using the application

To run the application, use the following command:

```bash
python -m mrobot_controller.app config/default.json
```

Running with docker:
```bash
docker-compose -f docker/docker-compose.yml up
```

## Communication
Communication with the controller is done over websockets. The messages are serialized using [messagepack](https://msgpack.org/), which has an extensive support for various programming languages.
The server receives commands and sends response on each command. These messages have these structures:

**Command structure**:
```json
{
	"command": string
	"parameters": dict
}
```

** Response structure**:
```json
{
	"success": bool
	"response": string
}
```

### Start video command
**Command structure**:
```json
{
	"command": "video_start"
	"parameters": {
		"host": string,
		"port": int
	}
}
```

### Stop video command
**Command structure**:
```json
{
	"command": "video_stop"
	"parameters": {}
}
```

# Video Streaming Application

This is a Python application for streaming video using GStreamer. The application reads configuration from a JSON file, which defines video parameters and server settings. It is designed to be easily configurable and extendable.

## Features

- **Video Streaming**: Streams video from a specified device using GStreamer.
- **Custom Configuration**: Load configuration from a JSON file, including video and server settings.
- **Error Handling**: Comprehensive error handling with logging.
- **Command-Line Interface**: Pass the configuration file as a command-line argument.

## Installation

### Prerequisites

- Python 3.6 or later
- GStreamer
  With base, good and bad plugins packages
- PyGObject

## Usage

To run the application, use the following command:

```bash
python main.py path/to/your/config.json
```

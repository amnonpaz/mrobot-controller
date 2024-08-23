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
- GStreamer installed on your system
- PyGObject

### Installation Steps

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/video_streamer.git
    cd video_streamer
    ```

2. **Install Dependencies:**

    Use `pip` to install the necessary Python packages:

    ```bash
    pip install -r requirements.txt
    ```

3. **Install the Package:**

    You can install the package locally using:

    ```bash
    python setup.py install
    ```

## Usage

### Command-Line Interface

To run the application, use the following command:

```bash
python main.py --config path/to/your/config.json
```

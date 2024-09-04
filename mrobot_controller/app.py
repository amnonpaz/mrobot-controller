import argparse
import logging
import asyncio
from . import Controller
from .app_config import AppConfig

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S'
        )


def parse_arguments():
    parser = argparse.ArgumentParser(description="Video Streaming Application")
    parser.add_argument('config', type=str, help='Path to configuration JSON file')
    return parser.parse_args()


def main():
    logger = logging.getLogger('Main')

    logger.info('mRobot Controller')
    # Parse command-line arguments
    args = parse_arguments()

    # Load configuration from JSON file
    config = AppConfig(args.config)

    controller = Controller(config.get_app_server_config()['port'], config.get_video_config())
    try:
        # Initialize and start the VideoStreamer with the configuration
        logger.info("Starting controller...")
        asyncio.run(controller.run())
    except Exception as e:
        logger.critical(f"Failed to start controller: {e}")
        controller.stop()
        exit(1)


if __name__ == "__main__":
    main()

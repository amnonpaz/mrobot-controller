import argparse
import logging
from video_streamer import VideoStreamer
from app_config import AppConfig

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

    logger.info('V4L to RTP streamer')
    # Parse command-line arguments
    args = parse_arguments()

    # Load configuration from JSON file
    config = AppConfig(args.config)

    try:
        # Initialize and start the VideoStreamer with the configuration
        streamer = VideoStreamer(config.device, config.width, config.height, config.host, config.port, config.test)
        logger.info("Starting video streaming...")
        streamer.start()
    except Exception as e:
        logger.critical(f"Failed to start video streaming: {e}")
        exit(1)


if __name__ == "__main__":
    main()

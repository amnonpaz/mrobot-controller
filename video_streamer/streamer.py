import gi
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from video_streamer.config import Config

# Set up logging

class VideoStreamer:
    def __init__(self, config: Config):

        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize GStreamer
        Gst.init(None)
        self.logger.debug("GStreamer initialized")

        # Create and set up the pipeline
        self.pipeline = self.setup_pipeline(config)

        # Create a bus to get messages from the GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.logger.debug("Bus connected to pipeline")

        self.loop = GLib.MainLoop()

    def setup_pipeline(self, config: Config):
        # Create the pipeline
        pipeline = Gst.Pipeline.new("video-stream")
        if not pipeline:
            self.logger.error("Failed to create GStreamer pipeline")
            raise Exception("Failed to create GStreamer pipeline")
        self.logger.debug("Pipeline created")

        # Create elements
        videosrc = self.create_v4l2src(config.device)
        capsfilter = self.create_capsfilter(config.width, config.height)
        h264parse = self.create_h264parse()
        rtph264pay = self.create_rtph264pay()
        udpsink = self.create_udpsink(config.host, config.port)

        # Add elements to the pipeline
        pipeline.add(videosrc)
        pipeline.add(capsfilter)
        pipeline.add(h264parse)
        pipeline.add(rtph264pay)
        pipeline.add(udpsink)
        self.logger.debug("Elements added to pipeline")

        # Link the elements
        if not videosrc.link(capsfilter):
            self.logger.error("Failed to link videosrc to capsfilter")
            raise Exception("Failed to link videosrc to capsfilter")
        if not capsfilter.link(h264parse):
            self.logger.error("Failed to link capsfilter to h264parse")
            raise Exception("Failed to link capsfilter to h264parse")
        if not h264parse.link(rtph264pay):
            self.logger.error("Failed to link h264parse to rtph264pay")
            raise Exception("Failed to link h264parse to rtph264pay")
        if not rtph264pay.link(udpsink):
            self.logger.error("Failed to link rtph264pay to udpsink")
            raise Exception("Failed to link rtph264pay to udpsink")

        self.logger.debug("Elements linked successfully")
        return pipeline

    def create_v4l2src(self, device):
        v4l2src = Gst.ElementFactory.make("v4l2src", "source")
        if not v4l2src:
            self.logger.error("Failed to create v4l2src element")
            raise Exception("Failed to create v4l2src element")
        v4l2src.set_property("device", device)
        self.logger.debug(f"v4l2src element created with device {device}")
        return v4l2src

    def create_videotestsrc(self):
        videotestsrc = Gst.ElementFactory.make("videotestsrc", "source")
        if not videotestsrc:
            self.logger.error("Failed to create videotestsrc element")
            raise Exception("Failed to create videotestsrc element")
        self.logger.debug(f"videotestsrc element created")
        return videotestsrc

    def create_capsfilter(self, width, height):
        capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        if not capsfilter:
            self.logger.error("Failed to create capsfilter element")
            raise Exception("Failed to create capsfilter element")
        caps = Gst.Caps.from_string(f"video/x-h264,width={width},height={height}")
        capsfilter.set_property("caps", caps)
        self.logger.debug(f"capsfilter element created with caps {caps.to_string()}")
        return capsfilter

    def create_h264parse(self):
        h264parse = Gst.ElementFactory.make("h264parse", "parser")
        if not h264parse:
            self.logger.error("Failed to create h264parse element")
            raise Exception("Failed to create h264parse element")
        self.logger.debug("h264parse element created")
        return h264parse

    def create_rtph264pay(self):
        rtph264pay = Gst.ElementFactory.make("rtph264pay", "payloader")
        if not rtph264pay:
            self.logger.error("Failed to create rtph264pay element")
            raise Exception("Failed to create rtph264pay element")
        self.logger.debug("rtph264pay element created")
        return rtph264pay

    def create_udpsink(self, host, port):
        udpsink = Gst.ElementFactory.make("udpsink", "sink")
        if not udpsink:
            self.logger.error("Failed to create udpsink element")
            raise Exception("Failed to create udpsink element")
        udpsink.set_property("host", host)
        udpsink.set_property("port", port)
        self.logger.debug(f"udpsink element created with host {host} and port {port}")
        return udpsink

    def on_message(self, bus, message):
        res = True
        msg_type = message.type
        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self.logger.error(f"Error: {err}, {debug}")
            self.stop()
            res = False
        elif msg_type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            self.logger.warning(f"Warning: {err}, {debug}")
        elif msg_type == Gst.MessageType.EOS:
            self.logger.info("End-Of-Stream reached")
            self.stop()
            res = False
        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                self.logger.debug(f"Pipeline state changed from {old_state.value_nick} to {new_state.value_nick}")
        return res

    def start(self):
        # Start playing the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        self.logger.info("Pipeline started")

        # Run the pipeline
        try:
            self.loop = self.loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        # Clean up
        self.pipeline.set_state(Gst.State.NULL)
        self.logger.info("Pipeline stopped")
        self.loop.quit()


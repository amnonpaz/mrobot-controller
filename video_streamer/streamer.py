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
        self.logger.debug('GStreamer initialized')

        # Create and set up the pipeline
        self.pipeline = self.setup_pipeline(config)

        # Create a bus to get messages from the GStreamer pipeline
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.on_message)
        self.logger.debug('Bus connected to pipeline')

        self.loop = GLib.MainLoop()

    def setup_pipeline(self, config: Config):
        # Create the pipeline
        pipeline = Gst.Pipeline.new('video-stream')
        if not pipeline:
            self.logger.error('Failed to create GStreamer pipeline')
            raise Exception('Failed to create GStreamer pipeline')
        self.logger.debug('Pipeline created')

        # Create elements
        videosrc = self.create_element('v4l2src', 'source',
                                       {'device': config.device})

        capsfilter = self.create_element('capsfilter', 'source-capsfilter')
        self.set_caps(capsfilter, f'video/x-h264,width={config.width},height={config.height}')

        h264parse = self.create_element('h264parse', 'parser')
        rtph264pay = self.create_element('rtph264pay', 'payloader')
        udpsink = self.create_element('udpsink', 'sink', 
                                      {'host': config.host, 'port': config.port})

        # Add elements to the pipeline
        pipeline.add(videosrc)
        pipeline.add(capsfilter)
        pipeline.add(h264parse)
        pipeline.add(rtph264pay)
        pipeline.add(udpsink)
        self.logger.debug('Elements added to pipeline')

        # Link the elements
        if not videosrc.link(capsfilter):
            self.logger.error('Failed to link videosrc to capsfilter')
            raise Exception('Failed to link videosrc to capsfilter')
        if not capsfilter.link(h264parse):
            self.logger.error('Failed to link capsfilter to h264parse')
            raise Exception('Failed to link capsfilter to h264parse')
        if not h264parse.link(rtph264pay):
            self.logger.error('Failed to link h264parse to rtph264pay')
            raise Exception('Failed to link h264parse to rtph264pay')
        if not rtph264pay.link(udpsink):
            self.logger.error('Failed to link rtph264pay to udpsink')
            raise Exception('Failed to link rtph264pay to udpsink')

        self.logger.debug('Elements linked successfully')
        return pipeline

    def create_element(self, element_type: str, element_name: str, props: dict = {}):
        element = Gst.ElementFactory.make(element_type, element_name)
        if not element:
            self.logger.error(f'Failed to create {element_type} element')
            raise Exception(f'Failed to create {element_type} element')
        self.logger.debug(f'{element_type} created with device: {element_name}')
        for key in props: 
            element.set_property(key, props[key])
            self.logger.debug(f'- {element_name}: Set property {key} to {props[key]}')
        return element

    def set_caps(self, element, caps_string: str):
        caps = Gst.Caps.from_string(caps_string)
        element.set_property('caps', caps)
        self.logger.debug(f'- {element.get_name()}: Set caps to {caps.to_string()}')

    def on_message(self, bus, message):
        res = True
        msg_type = message.type
        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self.logger.error(f'Error: {err}, {debug}')
            self.stop()
            res = False
        elif msg_type == Gst.MessageType.WARNING:
            err, debug = message.parse_warning()
            self.logger.warning(f'Warning: {err}, {debug}')
        elif msg_type == Gst.MessageType.EOS:
            self.logger.info('End-Of-Stream reached')
            self.stop()
            res = False
        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                self.logger.debug(f'Pipeline state changed from {old_state.value_nick} to {new_state.value_nick}')
        return res

    def start(self):
        # Start playing the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        self.logger.info('Pipeline started')

        # Run the pipeline
        try:
            self.loop = self.loop.run()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        # Clean up
        self.pipeline.set_state(Gst.State.NULL)
        self.logger.info('Pipeline stopped')
        self.loop.quit()


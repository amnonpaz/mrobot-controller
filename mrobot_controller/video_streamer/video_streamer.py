import gi
import logging
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from abc import ABC, abstractmethod


class VideoFrameHandler(ABC):
    @abstractmethod
    async def handle_frame(self, frame, size):
        pass


class VideoStreamer:
    def __init__(self,
                 video_frame_handler: VideoFrameHandler,
                 device: str,
                 width: int,
                 height: int,
                 test: bool = False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pipeline = None
        self.elements = {}
        self.bus = None

        # Initialize GStreamer
        Gst.init(None)
        self.logger.debug('GStreamer initialized')

        self.video_frame_handler = video_frame_handler
        self.create_elements(device, width, height, test)
        self.create_pipeline()
        self.add_elements()
        self.link_elements()
        self.create_bus()

        self.loop = GLib.MainLoop()

    def create_pipeline(self):
        self.pipeline = Gst.Pipeline.new('video-stream')
        if not self.pipeline:
            self.logger.error('Failed to create GStreamer pipeline')
            raise Exception('Failed to create GStreamer pipeline')
        self.logger.debug('Pipeline created')

    def create_elements(self,
                        device: str,
                        width: int,
                        height: int,
                        test: bool = False):
        if not test:
            self.create_video_source(device, width, height)
        else:
            self.create_test_source(width, height)

        self.elements['h264parse'] = self.gst_element_create('h264parse', 'parser')
        self.elements['h264decoder'] = self.gst_element_create('avdec_h264', 'decoder')

        self.elements['rgb_convert'] = self.gst_element_create('videoconvert', 'rgbconvert')
        self.elements['rgb_capsfilter'] = self.gst_element_create('capsfilter', 'rgb_capsfilter')
        self.gst_element_set_caps(self.elements['rgb_capsfilter'], f'video/x-raw,format=RGB,width={width},height={height}')

        self.create_sink()

    def create_video_source(self, device: str, width: int, height: int):
        self.logger.debug('Creating V4L source')
        self.elements['source'] = self.gst_element_create('v4l2src', 'source',
                                                          {'device': device})
        self.elements['capsfilter'] = self.gst_element_create('capsfilter', 'source-capsfilter')
        self.gst_element_set_caps(self.elements['capsfilter'], f'video/x-h264,width={width},height={height}')

    def create_test_source(self, width: int, height: int):
        self.logger.debug('Creating test source')
        self.elements['source'] = self.gst_element_create('videotestsrc', 'source')
        self.elements['capsfilter'] = self.gst_element_create('capsfilter', 'source-capsfilter')
        self.gst_element_set_caps(self.elements['capsfilter'], f'video/x-raw,width={width},height={height}')
        self.elements['source-encoder'] = self.gst_element_create('x264enc', 'test-source-encoding')

    def create_sink(self):
        self.elements['sink'] = self.gst_element_create('appsink', 'sink')
        self.elements['sink'].set_property('emit-signals', True)
        self.elements['sink'].connect('new-sample', VideoStreamer.on_new_sample_callback, self)

    def add_elements(self):
        self.logger.debug('Adding elements to pipeline')
        keys_iter = iter(self.elements)
        try:
            while True:
                element_key = next(keys_iter)
                element = self.elements[element_key]
                self.logger.debug(f'- Adding {element.get_name()} to pipeline')
                self.pipeline.add(element)
        except StopIteration:
            pass

    def link_elements(self):
        self.logger.debug('Linking elements')
        keys_iter = iter(self.elements)
        prev = self.elements[next(keys_iter)]
        try:
            while True:
                element_key = next(keys_iter)
                current = self.elements[element_key]
                self.logger.debug(f' - {prev.get_name()} -> {current.get_name()}')
                if not prev.link(current):
                    msg = f'Failed to link {prev.get_name()} to {current.get_name()}'
                    self.logger.error(msg)
                    raise Exception(msg)
                prev = current
        except StopIteration:
            pass

    def create_bus(self):
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.on_message)
        self.logger.debug('Bus connected to pipeline')

    def gst_element_create(self, element_type: str, element_name: str, props: dict = None):
        if props is None:
            props = {}
        element = Gst.ElementFactory.make(element_type, element_name)
        if not element:
            self.logger.error(f'Failed to create {element_type} element')
            raise Exception(f'Failed to create {element_type} element')
        self.logger.debug(f'{element_type} created with device: {element_name}')
        for key in props: 
            element.set_property(key, props[key])
            self.logger.debug(f'- {element_name}: Set property {key} to {props[key]}')
        return element

    def gst_element_set_caps(self, element, caps_string: str):
        caps = Gst.Caps.from_string(caps_string)
        element.set_property('caps', caps)
        self.logger.debug(f'- {element.get_name()}: Set caps to {caps.to_string()}')

    @staticmethod
    def on_new_sample_callback(_, userdata):
        video_streamer_obj: VideoStreamer = userdata
        return video_streamer_obj.handle_sample()

    def handle_sample(self):
        sample = self.elements['sink'].emit('pull-sample')
        if not sample:
            return Gst.FlowReturn.ERROR

        try:
            buffer = sample.get_buffer()
            success, map_info = buffer.map(Gst.MapFlags.READ)
            if success:
                self.logger.debug('Passing new frame')
                raw_data = map_info.data
                self.video_frame_handler.handle_frame(raw_data, len(raw_data))
        except Exception as e:
            self.logger.warning(f'Error while reading video buffer: {e}')
        finally:
            buffer.unmap(map_info)

        return Gst.FlowReturn.OK

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
        elif msg_type == Gst.MessageType.INFO:
            info, debug = message.parse_info()
            self.logger.info(f"Info: {info.message}, Debug Info: {debug}")
        elif msg_type == Gst.MessageType.BUFFERING:
            buffering_percent = message.parse_buffering()
            self.logger.debug(f"Buffering: {buffering_percent}%")
            if buffering_percent < 100:
                self.pipeline.set_state(Gst.State.PAUSED)
            else:
                self.pipeline.set_state(Gst.State.PLAYING)
        elif msg_type == Gst.MessageType.STREAM_START:
            self.logger.info("Stream started")
        elif msg_type == Gst.MessageType.DURATION_CHANGED:
            self.logger.debug("Duration changed")
        elif msg_type == Gst.MessageType.LATENCY:
            self.logger.debug("Latency message received")
            self.pipeline.recalculate_latency()

        return res

    async def start(self):
        # Start playing the pipeline
        self.pause()
        self.logger.info('Pipeline ready')
        self.loop = self.loop.run()

    def play(self):
        self.logger.info('Pipeline state: PLAYING')
        self.pipeline.set_state(Gst.State.PLAYING)

    def pause(self):
        self.logger.info('Pipeline state: PAUSED')
        self.pipeline.set_state(Gst.State.PAUSED)

    def stop(self):
        # Clean up
        self.pipeline.set_state(Gst.State.NULL)
        self.logger.info('Pipeline stopped')
        self.loop.quit()

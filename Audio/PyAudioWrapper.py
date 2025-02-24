import pyaudiowpatch as pyaudio
import numpy as np
import asyncio

# Using Pyaudio based version package
# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py
#####################################
#           PyAudioWPatch           #
#####################################
class PyAudioWrapper():
    def __init__(self, chunk):
        # Initialize PyAudio
        self._chunk = chunk
        self._p = None
        self.default_speakers = None
        self.default_speakers_loopback = None
        self.mono_data = None # The data being read
        self.stream = None
        
    async def setup(self):
        # Close the existing stream if it is open
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        # Terminate the existing PyAudio instance if it exists
        if self._p is not None:
            self._p.terminate()
            self._p = None
        
        # Make pyaudio object 
        self._p = pyaudio.PyAudio()
        # Get default WASAPI speakers
        self.default_speakers = self.get_default_speakers()

        # Getting loopback solution
        if not self.default_speakers["isLoopbackDevice"]:
            for loopback in self._p.get_loopback_device_info_generator():
                """
                Try to find loopback device with same name(and [Loopback suffix]).
                Unfortunately, this is the most adequate way at the moment.
                """
                if self.default_speakers["name"] in loopback["name"]:
                    self.default_speakers_loopback = loopback
                    break
        else:
            self.default_speakers_loopback = self.default_speakers

        # Open audio stream with the selected device
        self.stream = self._p.open(format=pyaudio.paInt16,
                                    channels=self.default_speakers_loopback["maxInputChannels"],
                                    rate=int(self.default_speakers_loopback["defaultSampleRate"]),
                                    frames_per_buffer=self._chunk,
                                    input=True,
                                    input_device_index=self.default_speakers_loopback["index"],
                                    stream_callback=self.read_mono)


    # Callback to get audio data (L channel only)
    def read_mono(self, in_data, frame_count, time_info, status):
        # Convert data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        # Select every alternate value starting from index 0 (left channel)
        self.mono_data = audio_data[::2]
        return (in_data, pyaudio.paContinue)
    
    def get_default_speakers(self):
        # Get default WASAPI info
        wasapi_info = self._p.get_host_api_info_by_type(pyaudio.paWASAPI)
        # Get default WASAPI speakers
        return self._p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

import pyaudiowpatch as pyaudio
import numpy as np

# Using Pyaudio based version package
# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py
#####################################
#           PyAudioWPatch           #
#####################################
class PyAudioWrapper():
    def __init__(self, chunk):
        # Initialize PyAudio
        self._chunk = chunk
        self._p = pyaudio.PyAudio()
        # Get default WASAPI info
        wasapi_info = self._p.get_host_api_info_by_type(pyaudio.paWASAPI)
        # Get default WASAPI speakers
        self.default_speakers = self._p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        self.mono_data = None # The data being read

        # Getting loopback solution
        if not self.default_speakers["isLoopbackDevice"]:
                    for loopback in self._p.get_loopback_device_info_generator():
                        """
                        Try to find loopback device with same name(and [Loopback suffix]).
                        Unfortunately, this is the most adequate way at the moment.
                        """
                        if self.default_speakers["name"] in loopback["name"]:
                            self.default_speakers = loopback
                            break

        # Open audio stream with the selected device
        self.stream = self._p.open(format=pyaudio.paInt16,
                                    channels=self.default_speakers["maxInputChannels"],
                                    rate=int(self.default_speakers["defaultSampleRate"]),
                                    frames_per_buffer=self._chunk,
                                    input=True,
                                    input_device_index=self.default_speakers["index"],
                                    stream_callback=self.read_mono)

    # Also in The FFTProcesssor but will be depreciated...
    def read_mono(self, in_data, frame_count, time_info, status):
        # Convert data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        # Select every alternate value starting from index 0 (left channel)
        self.mono_data = audio_data[::2]
        return (in_data, pyaudio.paContinue)

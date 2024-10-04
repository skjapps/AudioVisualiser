import pyaudiowpatch as pyaudio

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
        default_speakers = self._p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        # Getting loopback solution
        if not default_speakers["isLoopbackDevice"]:
                    for loopback in self._p.get_loopback_device_info_generator():
                        """
                        Try to find loopback device with same name(and [Loopback suffix]).
                        Unfortunately, this is the most adequate way at the moment.
                        """
                        if default_speakers["name"] in loopback["name"]:
                            default_speakers = loopback
                            break

        # Open audio stream with the selected device
        self.stream = self._p.open(format=pyaudio.paInt16,
                                    channels=default_speakers["maxInputChannels"],
                                    rate=int(default_speakers["defaultSampleRate"]),
                                    frames_per_buffer=self._chunk,
                                    input=True,
                                    input_device_index=default_speakers["index"])
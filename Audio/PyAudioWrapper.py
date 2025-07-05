import pyaudio
import numpy as np
import asyncio

#####################################
#           Standard PyAudio        #
#####################################
class PyAudioWrapper():
    def __init__(self, chunk):
        # Initialize PyAudio
        self._chunk = chunk
        self._p = None
        self.default_speakers = None
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
        # Get default input device
        self.default_speakers = self.get_default_speakers()

        # Check if we got a valid device
        if self.default_speakers is None:
            raise RuntimeError("No default input device found")

        # Open audio stream with the selected device
        self.stream = self._p.open(format=pyaudio.paInt16,
                                    channels=int(self.default_speakers["maxInputChannels"]),
                                    rate=int(self.default_speakers["defaultSampleRate"]),
                                    frames_per_buffer=self._chunk,
                                    input=True,
                                    input_device_index=int(self.default_speakers["index"]),
                                    stream_callback=self.read_mono)

    # Callback to get audio data (L channel only)
    def read_mono(self, in_data, frame_count, time_info, status):
        # Convert data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        # Select every alternate value starting from index 0 (left channel)
        # For mono input, use all data
        if self.default_speakers is not None and int(self.default_speakers["maxInputChannels"]) == 1:
            self.mono_data = audio_data
        else:
            self.mono_data = audio_data[::2]
        return (in_data, pyaudio.paContinue)
    
    def get_default_speakers(self):
        # Get default input device info
        if self._p is None:
            return None
        try:
            return self._p.get_device_info_by_index(int(self._p.get_default_input_device_info()["index"]))
        except Exception as e:
            print(f"Error getting default input device: {e}")
            return None

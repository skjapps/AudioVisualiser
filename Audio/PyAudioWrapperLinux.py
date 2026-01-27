import pyaudio
import numpy as np
import asyncio
import subprocess
import re

# Linux audio wrapper using PyAudio with PulseAudio/PipeWire
# PipeWire provides PulseAudio compatibility, so this works on both
#####################################
#       PyAudio Linux Wrapper       #
#####################################
class PyAudioWrapper():
    def __init__(self, chunk):
        # Initialize PyAudio
        self._chunk = chunk
        self._p = None
        self.default_speakers = None
        self.default_speakers_loopback = None
        self.mono_data = None  # The data being read
        self.stream = None
        self._silent_mode = False  # Track if we're in silent mode
        self._error_logged = False  # Prevent repeated error logging
        
    async def setup(self):
        # If already in silent mode, don't re-initialize
        if self._silent_mode:
            return
            
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
        try:
            self._p = pyaudio.PyAudio()
        except Exception as e:
            print(f"WARNING: PyAudio initialization failed: {e}")
            print("Running in SILENT MODE - no audio visualization")
            self._create_dummy_audio()
            return
        
        # Get default output device (monitor/loopback)
        self.default_speakers = self.get_default_speakers()
        
        # Find the monitor (loopback) device for the default sink
        self.default_speakers_loopback = self.find_monitor_device()
        
        if self.default_speakers_loopback is None:
            print("No monitor device found, searching for suitable input device...")
            self.default_speakers_loopback = self.find_suitable_input()
            
        if self.default_speakers_loopback is None:
            print("WARNING: No audio input device available")
            print("Running in SILENT MODE - no audio visualization")
            self._create_dummy_audio()
            return

        # Open audio stream with the selected device
        try:
            print(f"Using input device: {self.default_speakers_loopback['name']}")
            self.stream = self._p.open(
                format=pyaudio.paInt16,
                channels=min(self.default_speakers_loopback["maxInputChannels"], 2),
                rate=int(self.default_speakers_loopback["defaultSampleRate"]),
                frames_per_buffer=self._chunk,
                input=True,
                input_device_index=self.default_speakers_loopback["index"],
                stream_callback=self.read_mono
            )
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            print("Attempting to use default input device...")
            try:
                # Fallback to default input
                default_input = self._p.get_default_input_device_info()
                self.stream = self._p.open(
                    format=pyaudio.paInt16,
                    channels=min(default_input["maxInputChannels"], 2),
                    rate=int(default_input["defaultSampleRate"]),
                    frames_per_buffer=self._chunk,
                    input=True,
                    input_device_index=default_input["index"],
                    stream_callback=self.read_mono
                )
                self.default_speakers_loopback = default_input
            except Exception as e2:
                print(f"Error opening default audio device: {e2}")
                print("Running in SILENT MODE - no audio visualization")
                self._create_dummy_audio()
    
    def _create_dummy_audio(self):
        """Create dummy audio configuration for silent mode"""
        self._silent_mode = True
        self.mono_data = np.zeros(self._chunk // 2, dtype=np.int16)
        self.default_speakers = {
            "name": "Dummy Audio (Silent Mode)",
            "defaultSampleRate": 44100.0,
            "maxInputChannels": 2,
            "maxOutputChannels": 2
        }
        self.default_speakers_loopback = self.default_speakers
        self.stream = None
        if not self._error_logged:
            print("=" * 60)
            print("RUNNING IN SILENT MODE")
            print("No audio devices available - window will show without audio")
            print("=" * 60)
            self._error_logged = True

    # Callback to get audio data (L channel only for mono, or mix both channels)
    def read_mono(self, in_data, frame_count, time_info, status):
        # Convert data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Check if we have stereo data
        if len(audio_data) >= 2:
            # Select every alternate value starting from index 0 (left channel)
            self.mono_data = audio_data[::2]
        else:
            # Already mono
            self.mono_data = audio_data
            
        return (in_data, pyaudio.paContinue)
    
    def get_default_speakers(self):
        """Get default output device info"""
        if self._silent_mode:
            return self.default_speakers  # Return cached value in silent mode
            
        try:
            return self._p.get_default_output_device_info()
        except Exception as e:
            if not self._error_logged:
                print(f"Warning: No default output device available")
                self._error_logged = True
            # Return first available output device
            for i in range(self._p.get_device_count()):
                device_info = self._p.get_device_info_by_index(i)
                if device_info["maxOutputChannels"] > 0:
                    return device_info
            return None
    
    def find_monitor_device(self):
        """
        Find the monitor (loopback) device for capturing system audio.
        In PulseAudio/PipeWire, monitor devices allow recording of output audio.
        """
        # Try to find a device with "monitor" in the name
        for i in range(self._p.get_device_count()):
            device_info = self._p.get_device_info_by_index(i)
            device_name = device_info.get("name", "").lower()
            
            # Look for monitor devices
            if "monitor" in device_name or "loopback" in device_name:
                # Ensure it's an input device
                if device_info["maxInputChannels"] > 0:
                    print(f"Found monitor device: {device_info['name']}")
                    return device_info
        
        # Alternative: use pactl to find the default sink's monitor
        try:
            result = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                default_sink = result.stdout.strip()
                # Monitor source is typically the sink name + ".monitor"
                monitor_name = f"{default_sink}.monitor"
                
                # Find device matching this monitor
                for i in range(self._p.get_device_count()):
                    device_info = self._p.get_device_info_by_index(i)
                    if monitor_name in device_info.get("name", ""):
                        print(f"Found monitor device via pactl: {device_info['name']}")
                        return device_info
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Could not use pactl to find monitor device: {e}")
        
        # If no monitor found, try to use any input device with high sample rate
        print("No monitor device found, searching for suitable input device...")
        return self.find_suitable_input()
    
    def find_suitable_input(self):
        """Find any suitable input device as fallback"""
        best_device = None
        best_rate = 0
        
        if self._p is None:
            return None
        
        for i in range(self._p.get_device_count()):
            device_info = self._p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0:
                rate = device_info["defaultSampleRate"]
                if rate > best_rate:
                    best_rate = rate
                    best_device = device_info
        
        if best_device:
            print(f"Using input device: {best_device['name']}")
        
        return best_device

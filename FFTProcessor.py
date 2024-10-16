import threading
import numpy as np
import time

class FFTProcessor:
    def __init__(self, chunk_size, update_rate, stream):
        self.chunk_size = chunk_size
        self.update_rate = update_rate
        self.stream = stream
        self.data = np.zeros(chunk_size)
        self.fft_result = np.zeros(chunk_size // 2)
        self.previous_fft_result = np.zeros(chunk_size // 2)
        self.last_update = time.time()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_fft)
        self._thread.daemon = True
        self._thread.start()

    def update_data(self, new_data):
        with self._lock:
            self.data = new_data

    def _process_fft(self):
        while not self._stop_event.is_set():
            with self._lock:
                current_time = time.time()
                if current_time - self.last_update >= self.update_rate:
                    self.data = self._read_mono()
                    self.previous_fft_result = self.fft_result
                    self.fft_result = np.fft.rfft(self.data)
                    self.last_update = current_time
    
    def _read_mono(self):
        # Read data from the stream
        data = self.stream.read(self.chunk_size)
        # Convert data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Select every alternate value starting from index 0 (left channel)
        mono_data = audio_data[::2]
        return mono_data

    def get_smoothed_fft_result(self):
        with self._lock:
            current_time = time.time()
            alpha = (current_time - self.last_update) / self.update_rate
            return (1 - alpha) * self.previous_fft_result + alpha * self.fft_result
        
    def stop(self):
        self._stop_event.set()
        self._thread.join()
# # import threading
# # import numpy as np
# # import time
# # from concurrent.futures import ThreadPoolExecutor

# # class FFTProcessor:
# #     def __init__(self, chunk_size, update_rate, stream, num_threads=2):
# #         self.chunk_size = chunk_size
# #         self.update_rate = update_rate
# #         self.stream = stream
# #         self.num_threads = num_threads
# #         self.data = np.zeros(chunk_size)
# #         self.fft_result = np.zeros(chunk_size // 2)
# #         self.previous_fft_result = np.zeros(chunk_size // 2)
# #         self.last_update = time.time()
# #         self._lock = threading.Lock()
# #         self._stop_event = threading.Event()
# #         self._thread = threading.Thread(target=self._process_fft)
# #         self._thread.daemon = True
# #         self._thread.start()
# #         self.executor = ThreadPoolExecutor(max_workers=num_threads)

# #     def update_data(self, new_data):
# #         with self._lock:
# #             self.data = new_data

# #     def _process_fft(self):
# #         while not self._stop_event.is_set():
# #             with self._lock:
# #                 current_time = time.time()
# #                 if current_time - self.last_update >= self.update_rate:
# #                     self.data = self._read_mono()
# #                     self.previous_fft_result = self.fft_result
# #                     self.fft_result = self._multithreaded_fft(self.data)
# #                     self.last_update = current_time

# #     def _read_mono(self):
# #         # Read data from the stream
# #         data = self.stream.read(self.chunk_size)
# #         # Convert data to numpy array
# #         audio_data = np.frombuffer(data, dtype=np.int16)
# #         # Select every alternate value starting from index 0 (left channel)
# #         mono_data = audio_data[::2]
# #         return mono_data

# #     def _multithreaded_fft(self, data):
# #         chunk_size = len(data) // self.num_threads
# #         futures = []

# #         def fft_worker(data_chunk):
# #             return np.fft.rfft(data_chunk)

# #         for i in range(self.num_threads):
# #             start_index = i * chunk_size
# #             end_index = (i + 1) * chunk_size if i != self.num_threads - 1 else len(data)
# #             futures.append(self.executor.submit(fft_worker, data[start_index:end_index]))

# #         results = [future.result() for future in futures]
# #         return np.concatenate(results)

# #     def get_smoothed_fft_result(self):
# #         with self._lock:
# #             current_time = time.time()
# #             alpha = (current_time - self.last_update) / self.update_rate
# #             return (1 - alpha) * self.previous_fft_result + alpha * self.fft_result

# #     def stop(self):
# #         self._stop_event.set()
# #         self._thread.join()
# #         self.executor.shutdown()

# # # Ensure to call fft_processor.stop() when you want to stop the processing

# # # import threading
# # # import numpy as np
# # # import time

# # # class FFTProcessor:
# # #     def __init__(self, chunk_size, update_rate, stream):
# # #         self.chunk_size = chunk_size
# # #         self.update_rate = update_rate
# # #         self.stream = stream
# # #         self.data = np.zeros(chunk_size)
# # #         self.fft_result = np.zeros(chunk_size // 2)
# # #         self.previous_fft_result = np.zeros(chunk_size // 2)
# # #         self.last_update = time.time()
# # #         self._lock = threading.Lock()
# # #         self._stop_event = threading.Event()
# # #         self._thread = threading.Thread(target=self._process_fft)
# # #         self._thread.daemon = True
# # #         self._thread.start()

# # #     def update_data(self, new_data):
# # #         with self._lock:
# # #             self.data = new_data

# # #     def _process_fft(self):
# # #         while not self._stop_event.is_set():
# # #             with self._lock:
# # #                 current_time = time.time()
# # #                 if current_time - self.last_update >= self.update_rate:
# # #                     self.data = self._read_mono()
# # #                     self.previous_fft_result = self.fft_result
# # #                     self.fft_result = np.fft.rfft(self.data)
# # #                     self.last_update = current_time
    
# # #     def _read_mono(self):
# # #         # Read data from the stream
# # #         data = self.stream.read(self.chunk_size)
# # #         # Convert data to numpy array
# # #         audio_data = np.frombuffer(data, dtype=np.int16)
# # #         # Select every alternate value starting from index 0 (left channel)
# # #         mono_data = audio_data[::2]
# # #         return mono_data

# # #     def get_smoothed_fft_result(self):
# # #         with self._lock:
# # #             current_time = time.time()
# # #             alpha = (current_time - self.last_update) / self.update_rate
# # #             return (1 - alpha) * self.previous_fft_result + alpha * self.fft_result
        
# # #     def stop(self):
# # #         self._stop_event.set()
# # #         self._thread.join()

# import threading
# import numpy as np
# import time
# from concurrent.futures import ThreadPoolExecutor

# class FFTProcessor:
#     def __init__(self, chunk_size, update_rate, stream, sample_rate, num_threads=4):
#         self.chunk_size = chunk_size
#         self.update_rate = update_rate
#         self.stream = stream
#         self.sample_rate = sample_rate
#         self.num_threads = num_threads
#         self.data = np.zeros(chunk_size)
#         self.fft_result = np.zeros(chunk_size // 2)
#         self.previous_fft_result = np.zeros(chunk_size // 2)
#         self.last_update = time.time()
#         self._lock = threading.Lock()
#         self._stop_event = threading.Event()
#         self._thread = threading.Thread(target=self._process_fft)
#         self._thread.daemon = True
#         self._thread.start()
#         self.executor = ThreadPoolExecutor(max_workers=num_threads)

#     def update_data(self, new_data):
#         with self._lock:
#             self.data = new_data

#     def _process_fft(self):
#         overlap = self.chunk_size // 2  # 50% overlap
#         while not self._stop_event.is_set():
#             with self._lock:
#                 current_time = time.time()
#                 if current_time - self.last_update >= self.update_rate:
#                     self.data = self._read_mono()
#                     self.previous_fft_result = self.fft_result
#                     fft_result_main = self._multithreaded_fft(self.data)
#                     overlap_data = self.data[overlap:]
#                     fft_result_overlap = self._multithreaded_fft(overlap_data)
                    
#                     # Ensure the shapes match before averaging
#                     if fft_result_main.shape == fft_result_overlap.shape:
#                         self.fft_result = (fft_result_main + fft_result_overlap) / 2
#                     else:
#                         self.fft_result = fft_result_main  # Fallback to main result if shapes don't match
                    
#                     self.last_update = current_time

#     def _read_mono(self):
#         # Read data from the stream
#         data = self.stream.read(self.chunk_size)
#         # Convert data to numpy array
#         audio_data = np.frombuffer(data, dtype=np.int16)
#         # Select every alternate value starting from index 0 (left channel)
#         mono_data = audio_data[::2]
#         return mono_data

#     def _multithreaded_fft(self, data):
#         chunk_size = len(data) // self.num_threads
#         window = np.hanning(len(data))  # Hanning window
#         windowed_data = data * window
#         padded_data = np.pad(windowed_data, (0, chunk_size - len(windowed_data) % chunk_size), 'constant')
#         futures = []

#         def fft_worker(data_chunk):
#             return np.fft.rfft(data_chunk)

#         for i in range(self.num_threads):
#             start_index = i * chunk_size
#             end_index = (i + 1) * chunk_size if i != self.num_threads - 1 else len(padded_data)
#             futures.append(self.executor.submit(fft_worker, padded_data[start_index:end_index]))

#         results = [future.result() for future in futures]
#         return np.concatenate(results)

#     def get_interpolated_fft_result(self):
#         with self._lock:
#             current_time = time.time()
#             alpha = (current_time - self.last_update) / self.update_rate
#             smoothed_fft = (1 - alpha) * self.previous_fft_result + alpha * self.fft_result
#             # Interpolate the FFT result
#             freqs = np.fft.rfftfreq(len(self.data), 1 / self.sample_rate)
#             interpolated_freqs = np.linspace(freqs, freqs[-1], len(freqs) * 10)
#             interpolated_fft = np.interp(interpolated_freqs, freqs, smoothed_fft)
#             return interpolated_fft

#     def stop(self):
#         self._stop_event.set()
#         self._thread.join()
#         self.executor.shutdown()

# # Ensure to call fft_processor.stop() when you want to stop the processing

import threading
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

class FFTProcessor:
    def __init__(self, chunk_size, update_rate, stream, sample_rate, num_threads=4):
        self.chunk_size = chunk_size
        self.update_rate = update_rate
        self.stream = stream
        self.sample_rate = sample_rate
        self.num_threads = num_threads
        self.data = np.zeros(chunk_size)
        self.fft_result = np.zeros(chunk_size // 2)
        self.previous_fft_result = np.zeros(chunk_size // 2)
        self.last_update = time.time()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_fft)
        self._thread.daemon = True
        self._thread.start()
        self.executor = ThreadPoolExecutor(max_workers=num_threads)

    def update_data(self, new_data):
        with self._lock:
            self.data = new_data

    def _process_fft(self):
        overlap = self.chunk_size // 2  # 50% overlap
        while not self._stop_event.is_set():
            with self._lock:
                current_time = time.time()
                if current_time - self.last_update >= self.update_rate:
                    self.data = self._read_mono()
                    self.previous_fft_result = self.fft_result
                    fft_result_main = self._multithreaded_fft(self.data)
                    overlap_data = self.data[overlap:]
                    fft_result_overlap = self._multithreaded_fft(overlap_data)
                    
                    # Ensure the shapes match before averaging
                    if fft_result_main.shape == fft_result_overlap.shape:
                        self.fft_result = (fft_result_main + fft_result_overlap) / 2
                    else:
                        self.fft_result = fft_result_main  # Fallback to main result if shapes don't match
                    
                    self.last_update = current_time

    def _read_mono(self):
        # Read data from the stream
        data = self.stream.read(self.chunk_size)
        # Convert data to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Select every alternate value starting from index 0 (left channel)
        mono_data = audio_data[::2]
        return mono_data

    def _multithreaded_fft(self, data):
        chunk_size = len(data) // self.num_threads
        window = np.hanning(len(data))  # Hanning window
        windowed_data = data * window
        padded_data = np.pad(windowed_data, (0, chunk_size - len(windowed_data) % chunk_size), 'constant')
        futures = []

        def fft_worker(data_chunk):
            return np.fft.rfft(data_chunk)

        for i in range(self.num_threads):
            start_index = i * chunk_size
            end_index = (i + 1) * chunk_size if i != self.num_threads - 1 else len(padded_data)
            if not self._stop_event.is_set():  # Check if the stop event is set before submitting
                futures.append(self.executor.submit(fft_worker, padded_data[start_index:end_index]))

        results = [future.result() for future in futures]
        return np.concatenate(results)

    def get_interpolated_fft_result(self):
        with self._lock:
            current_time = time.time()
            alpha = (current_time - self.last_update) / self.update_rate
            smoothed_fft = (1 - alpha) * self.previous_fft_result + alpha * self.fft_result
            # Interpolate the FFT result
            freqs = np.fft.rfftfreq(len(self.data), 1 / self.sample_rate)
            interpolated_freqs = np.linspace(freqs, freqs[-1], len(freqs) * 10)
            interpolated_fft = np.interp(interpolated_freqs, freqs, smoothed_fft)
            return interpolated_fft

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        self.executor.shutdown(wait=True)

# Ensure to call fft_processor.stop() when you want to stop the processing

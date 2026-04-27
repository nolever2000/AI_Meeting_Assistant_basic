import pyaudiowpatch as pyaudio
import numpy as np


class SystemStream:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.device_index = self.find_loopback_device()

    def find_loopback_device(self):
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)

            if dev.get("isLoopbackDevice"):
                name = dev["name"].lower()

                # 🎯 chọn Realtek loopback
                if "realtek" in name:
                    print(f"[System] {dev['name']} ({i})")
                    return i

        raise RuntimeError("Realtek loopback not found")

    def start(self):
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=2,          # Realtek = stereo
            rate=48000,          # thường là 48k
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.device_index
        )

    def read(self):
        data = np.frombuffer(
            self.stream.read(self.chunk_size, exception_on_overflow=False),
            dtype=np.float32
        )

        # stereo → mono
        data = data.reshape(-1, 2).mean(axis=1)

        return data
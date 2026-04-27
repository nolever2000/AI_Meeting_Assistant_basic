import sounddevice as sd
import numpy as np


class MicStream:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.device = self.find_mic()

        info = sd.query_devices(self.device)
        self.samplerate = int(info['default_samplerate'])
        self.channels = info['max_input_channels']

    def find_mic(self):
        for i, dev in enumerate(sd.query_devices()):
            name = dev['name'].lower()

            if dev['max_input_channels'] > 0 and "microphone" in name:
                print(f"[Mic] {dev['name']} ({i})")
                return i

        raise RuntimeError("Mic not found")

    def start(self):
        self.stream = sd.InputStream(
            device=self.device,
            samplerate=self.samplerate,
            channels=self.channels,
            dtype='float32'
        )
        self.stream.start()

    def read(self):
        data, _ = self.stream.read(self.chunk_size)

        # multi-channel → mono
        return np.mean(data, axis=1)
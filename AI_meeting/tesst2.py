import sounddevice as sd
import numpy as np


def find_mic():
    devices = sd.query_devices()

    for i, dev in enumerate(devices):
        name = dev['name'].lower()

        if dev['max_input_channels'] > 0:
            if any(x in name for x in ["usb", "headset", "airpods", "microphone"]):
                print(f"[Mic] Using: {dev['name']} (id={i})")
                return i

    raise RuntimeError("No mic found")


mic_id = find_mic()

stream = sd.InputStream(
    device=mic_id,
    samplerate=16000,
    channels=1,
    dtype='float32',
    blocksize=1600
)

stream.start()

print("🎤 MIC TEST - Hãy nói...")

while True:
    data, _ = stream.read(1600)
    volume = np.abs(data).mean()

    print(f"Mic Volume: {volume:.5f}")
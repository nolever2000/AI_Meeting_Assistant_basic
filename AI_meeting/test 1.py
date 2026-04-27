import pyaudiowpatch as pyaudio
import numpy as np

p = pyaudio.PyAudio()

# tìm device loopback
device_index = None

for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("isLoopbackDevice"):
        print("Using:", dev["name"])
        device_index = i
        break

stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=48000,
                input=True,
                frames_per_buffer=1024,
                input_device_index=device_index)

print("Listening...")

while True:
    data = np.frombuffer(stream.read(1024), dtype=np.float32)
    print(np.abs(data).mean())
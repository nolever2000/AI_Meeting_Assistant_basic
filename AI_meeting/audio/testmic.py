import pyaudiowpatch as pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if dev.get("isLoopbackDevice"):
        print(i, dev["name"])
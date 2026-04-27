from mic_stream import MicStream
from system_stream import SystemStream
from router import AudioRouter


class DummyVAD:
    def is_speech(self, audio):
        return abs(audio).mean() > 0.01


mic = MicStream()
sys = SystemStream()

mic.start()
sys.start()

router = AudioRouter(mic, sys, DummyVAD())

print("Running...")

while True:
    audio, source = router.read()
    print(source, audio.mean())
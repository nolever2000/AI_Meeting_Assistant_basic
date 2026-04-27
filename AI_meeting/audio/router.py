import time


class AudioRouter:
    def __init__(self, mic, system, vad):
        self.mic = mic
        self.system = system
        self.vad = vad

        self.mic_active = False
        self.last_mic_time = 0
        self.HOLD_TIME = 0.8

    def read(self):
        mic_audio = self.mic.read()
        sys_audio = self.system.read()

        now = time.time()

        if self.vad.is_speech(mic_audio):
            self.mic_active = True
            self.last_mic_time = now

        if self.mic_active and (now - self.last_mic_time < self.HOLD_TIME):
            return mic_audio, "mic"

        self.mic_active = False
        return sys_audio, "system"
import webrtcvad
import numpy as np

class VAD:
    def __init__(self):
        self.vad = webrtcvad.Vad(2)

    def is_speech(self, audio):
        audio_int16 = (audio * 32768).astype('int16')
        return self.vad.is_speech(audio_int16.tobytes(), 16000)
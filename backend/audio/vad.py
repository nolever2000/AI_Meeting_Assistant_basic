import webrtcvad


class SpeechGate:
    def __init__(self, mode: int = 2, sample_rate: int = 16000, frame_ms: int = 20):
        self.vad = webrtcvad.Vad(mode)
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.bytes_per_frame = int(sample_rate * (frame_ms / 1000.0) * 2)

    def has_speech(self, pcm16_chunk: bytes) -> bool:
        if len(pcm16_chunk) < self.bytes_per_frame:
            return False
        speech_votes = 0
        total = 0
        for i in range(0, len(pcm16_chunk) - self.bytes_per_frame + 1, self.bytes_per_frame):
            frame = pcm16_chunk[i : i + self.bytes_per_frame]
            if len(frame) != self.bytes_per_frame:
                continue
            total += 1
            if self.vad.is_speech(frame, self.sample_rate):
                speech_votes += 1
        return total > 0 and (speech_votes / total) >= 0.35

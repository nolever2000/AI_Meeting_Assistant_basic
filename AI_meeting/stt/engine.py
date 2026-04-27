from .api_client import transcribe

class STTEngine:
    def run(self, audio):
        return transcribe(audio)
import queue
import time

class Processor:
    def __init__(self, emit):
        self.emit = emit
        self.queue = queue.Queue()
        self.running = True

    def push_audio(self, audio, source):
        self.queue.put((audio, source))

    def run(self):
        print("Processor started")

        while self.running:
            try:
                audio, source = self.queue.get(timeout=1)

                text = self.transcribe(audio)

                if text:
                    self.emit({
                        "text": text,
                        "source": source,
                        "time": time.strftime("%H:%M:%S")
                    })

            except queue.Empty:
                continue

    def transcribe(self, audio):
        # TODO: thay bằng OpenAI / Whisper
        return "demo text"
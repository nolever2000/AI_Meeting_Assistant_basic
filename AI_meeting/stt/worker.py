from queue import Queue
from threading import Thread

class STTWorker:
    def __init__(self, engine, callback):
        self.queue = Queue()
        self.engine = engine
        self.callback = callback

        Thread(target=self.run, daemon=True).start()

    def push(self, audio, source):
        self.queue.put((audio, source))

    def run(self):
        while True:
            audio, source = self.queue.get()
            text = self.engine.run(audio)

            if text.strip():
                self.callback(text, source)
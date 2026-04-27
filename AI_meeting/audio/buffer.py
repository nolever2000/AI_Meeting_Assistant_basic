import queue


class AudioBuffer:
    def __init__(self, maxsize=50):
        self.q = queue.Queue(maxsize=maxsize)

    def push(self, data):
        if not self.q.full():
            self.q.put(data)

    def pop(self):
        if self.q.empty():
            return None
        return self.q.get()
import time


class MeasureTime:
    def __init__(self, message: str = "Time spent"):
        self.message = message

    def __enter__(self, *_):
        self.start = time.perf_counter()

    def __exit__(self, *_):
        self.end = time.perf_counter()
        interval = self.end - self.start
        print(self.message + f": {interval:.4f} seconds")

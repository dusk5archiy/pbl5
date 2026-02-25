import time
from functools import wraps


class MeasureTime:
    def __init__(self, message: str | None = None):
        self.message = message or "Time spent"

    def __enter__(self, *_):
        self.start = time.perf_counter()

    def __exit__(self, *_):
        self.end = time.perf_counter()
        interval = self.end - self.start
        print(self.message + f": {interval:.4f} seconds")

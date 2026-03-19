import time
from colorama import Fore, init


class MeasureTime:
    def __init__(self, message: str = "Time spent", color=Fore.RESET):
        self.message = message
        self.color = color

    def __enter__(self, *_):
        self.start = time.perf_counter()

    def __exit__(self, *_):
        self.end = time.perf_counter()
        interval = self.end - self.start
        init()
        print(self.color + self.message + f": {interval:.4f} seconds" + Fore.RESET)

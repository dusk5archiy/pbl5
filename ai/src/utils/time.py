import time
from colorama import Fore


class MeasureTime:
    RED = Fore.RED

    def __init__(self, message: str = "Time spent", color=Fore.WHITE):
        self.message = message
        self.color = color

    def __enter__(self, *_):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *_):
        self.end = time.perf_counter()
        interval = self.end - self.start
        print(self.color + self.message + f": {int(interval * 1000)}ms" + Fore.RESET)

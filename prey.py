import random
import time
from multiprocessing import Process

from color import colorString


class Prey(Process):
    def __init__(self, environment, duration, log_queue):
        super().__init__()
        self.environment = environment
        self.duration = duration
        self.log_queue = log_queue

    def flee(self):
        pass

    def run(self):
        # print(f"[Prey {self.pid}] is running.")
        start = time.time()
        while time.time() - start < self.duration:
            if self.log_queue is not None:
                self.log_queue.put(
                    colorString("green", f"[Prey {self.pid} ate 2.0 unit of grass]")
                )
            self.environment.consume_grass()
            time.sleep(random.uniform(2.0, 4.5))

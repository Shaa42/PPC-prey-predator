import random as rd
import time
from multiprocessing import Process

from color import colorString


class Predator(Process):
    def __init__(self, environment, duration, log_queue, barrier):
        super().__init__()
        self.environment = environment
        self.duration = duration
        self.log_queue = log_queue
        self.barrier = barrier
        self.energy = 50.0
        self.alivre = True

    def log(self, color, msg):
        if self.log_queue is not None:
            self.log_queue.put(colorString(color, msg))

    def kill_prey(self, prey):
        succes = self.environment.mark_prey_dead(prey)

        if succes:
            self.log("blue", f"[Predator {self.pid}] killed prey {prey}")

    def kill_probability(self, n):
        # Has 1 chance over n to return true
        if rd.random() < 1 / n:
            return True
        return False

    def hunt(self):
        alive_preys = self.environment.get_alive_preys()
        if alive_preys:
            prey = rd.choice(alive_preys)
            self.kill_prey(prey)
            return True
        return False

    def run(self):
        # Wait for all the preys to load
        if self.barrier:
            self.barrier.wait()

        start = time.time()
        while time.time() - start < self.duration:
            if self.kill_probability(4):
                if not self.hunt():
                    self.log("blue", f"[Predator {self.pid}] killed no prey.")
            time.sleep(rd.uniform(4.0, 6.0))

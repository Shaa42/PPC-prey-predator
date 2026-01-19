import random
import sys
import time
from multiprocessing import Process

from color import colorString

# TODO: Create a manager dict for the prey energy


class Prey(Process):
    def __init__(self, environment, duration, log_queue, barrier):
        super().__init__()
        self.environment = environment
        self.duration = duration
        self.log_queue = log_queue
        self.barrier = barrier
        self.energy = 50.0

    def log(self, color, msg):
        self.log_queue.put(colorString(color, msg))

    def gain_energy(self, n):
        self.energy = min(100.0, self.energy + n)
        # self.environment.update_prey_energy(self.pid, self.energy)

    def lose_energy(self, n):
        self.energy = max(0.0, self.energy - n)
        # self.environment.update_prey_energy(self.pid, self.energy)

    def eat_grass(self):
        self.log("green", f"[Prey {self.pid} ate 2.0 unit of grass]")
        self.environment.consume_grass()
        self.gain_energy(5.0)

    def run(self):
        # Register prey in the environment
        self.environment.register_prey(self.pid, self.energy)
        if self.log_queue is not None:
            self.log("yellow", f"[Prey {self.pid}] Registered in environment")

        # Wait for all the preys to load
        if self.barrier:
            self.barrier.wait()

        start = time.time()
        while time.time() - start < self.duration:
            # See if the prey has been killed
            if self.pid in self.environment.prey_dict:
                # self.log("yellow", f"{self.environment.prey_dict[self.pid]['alive']}")
                if not self.environment.prey_dict[self.pid]:
                    self.log("red", f"[Prey {self.pid} has been killed]")
                    # Remove prey from manager dict and terminate process
                    self.environment.unregister_prey(self.pid)
                    self.log(
                        "yellow", f"[Prey {self.pid}] Unregistered from environment"
                    )
                    sys.exit(0)

            self.eat_grass()

            time.sleep(random.uniform(2.0, 4.5))
            self.lose_energy(2.5)

        # Unregister prey if it finishes naturally
        self.environment.unregister_prey(self.pid)
        self.log("yellow", f"[Prey {self.pid}] Unregistered from environment")

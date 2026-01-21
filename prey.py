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
        self.is_high = 90.0

    def log(self, color, msg):
        self.log_queue.put(colorString(color, msg))

    def gain_energy(self, n):
        self.energy = min(100.0, self.energy + n)
        self.environment.upd_prey_energy(self.pid, self.energy)

    def lose_energy(self, n):
        self.energy = max(0.0, self.energy - n)
        self.environment.upd_prey_energy(self.pid, self.energy)
        if self.energy <= 0:
            self.log("red", f"[Prey {self.pid} starved to death]")
            # Remove prey from manager dict and terminate process
            self.environment.unregister_prey(self.pid)
            self.log(
                "yellow", f"[Prey {self.pid}] Unregistered from environment"
            )
            sys.exit(0)


    def eat_grass(self):
        if self.environment.consume_grass():
            self.log("green", f"[Prey {self.pid} ate 2.0 unit of grass]")
            self.gain_energy(5.0)
            self.environment.upd_prey_energy(self.pid, self.energy)
        else:
            self.log("purple", f"[Prey {self.pid} moved to the next vallety in search for grass]")
            self.lose_energy(2.0)
            self.environment.upd_prey_energy(self.pid, self.energy)


    def run(self):
        self.environment.prey_dict[self.pid] = self.energy
        # Register prey in the environment
        if self.energy <= self.is_high:
            self.environment.register_prey(self.pid, self.energy)
            if self.log_queue is not None:
                self.log("yellow", f"[Prey {self.pid}] Registered in environment")
        else:
            self.log("cyan", f"[Prey {self.pid}] is too strong to be preyed!")
            self.lose_energy(5.0)
            self.environment.upd_prey_energy(self.pid, self.energy)


        # Wait for all the preys to load
        if self.barrier:
            self.barrier.wait()

        start = time.time()
        while time.time() - start < self.duration:
            # See if the prey has been killed
            if self.environment.prey_dict[self.pid] <= 0:
                self.log("red", f"[Prey {self.pid} died]")
                # Remove prey from manager dict and terminate process
                self.environment.unregister_prey(self.pid)
                self.log(
                    "yellow", f"[Prey {self.pid}] Unregistered from environment"
                )
                sys.exit(0)

            self.eat_grass()
            time.sleep(random.uniform(0.5, 1.5))
            self.lose_energy(2.5)
            self.environment.upd_prey_energy(self.pid, self.energy)


        self.environment.unregister_prey(self.pid)

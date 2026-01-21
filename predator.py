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
        self.energy = 60.0
        self.hunger_threshold = 50.0
        self.hunting = False
        self.alive = True

    def log(self, color, msg):
        if self.log_queue is not None:
            self.log_queue.put(colorString(color, msg))

    def kill_probability(self, n):
        # Has 1 chance over n to return true
        return rd.random() < 1 / n

    def hunt(self):
        alive_preys = self.environment.get_alive_preys()
        if alive_preys:
            target_prey = rd.choice(alive_preys)
            if self.kill_probability(4):
                self.environment.mark_prey_dead(target_prey)
                self.log("blue", f"[Predator {self.pid}] killed prey {target_prey}.")
                self.energy += 35.0
                self.environment.upd_pred_energy(self.pid, self.energy)
                if self.energy >= self.hunger_threshold:
                    self.hunting = False
                    self.log("blue", f"[Predator {self.pid}] is full.")
                return True
            else:
                self.log("blue", f"[Predator {self.pid}] failed to catch its prey.")
                self.energy -= 10.0
                self.environment.upd_pred_energy(self.pid, self.energy)
                
        return False

    def run(self):
        self.environment.pred_dict[self.pid] = self.energy
        # Wait for all the preys to load
        if self.barrier:
            self.barrier.wait()
        start = time.time()
        while time.time() - start < self.duration:
            if self.energy <= 0:
                self.log("red", f"[Predator {self.pid} has starved to death. ")
                self.environment.pred_dict[self.pid] = 0
                return
            if self.energy < self.hunger_threshold:
                if not self.hunting:
                    self.hunting = True
                    self.log("blue", f"[Predator {self.pid}] Grrrr...Hungry...")
                self.hunt()
            
            time.sleep(rd.uniform(0.5, 1.0))
            self.energy -= 5.0
            self.environment.upd_pred_energy(self.pid, self.energy)
            print(self.energy)

import os
from multiprocessing import Lock, Manager, Value

from color import colorString


class Environment:
    def __init__(self, duration, initial_grass=100.0):
        self.duration = duration
        self.grass = Value("d", initial_grass)
        manager_prey = Manager()
        manager_pred = Manager()
        self.hunt_lock = Lock()
        self.prey_dict = manager_prey.dict()
        self.pred_dict = manager_pred.dict()

    def consume_grass(self, amount=2.0):
        with self.grass.get_lock():
            if self.grass.value >= amount:
                self.grass.value -= amount
                print(
                    colorString(
                        "red",
                        f"[Environment {os.getpid()}] Grass consumed: {amount}. Remaining grass: {self.grass.value}",
                    )
                )
                return True
            else:
                print(
                    colorString(
                        "red",
                        f"[Environment {os.getpid()}] Not enough grass to consume. Remaining grass: {self.grass.value}",
                    )
                )
                return False

    # Give all the methods to interact with the preys

    def register_prey(self, pid, energy):
        self.prey_dict[pid] = energy

    def unregister_prey(self, pid):
        if pid in self.prey_dict:
            del self.prey_dict[pid]

    def upd_prey_energy(self, pid, energy):
        if pid in self.prey_dict:
            self.prey_dict[pid] = energy

    def upd_pred_energy(self, pid, energy):
        if pid in self.pred_dict:
            self.pred_dict[pid] = energy

    def mark_prey_dead(self, pid):
        with self.hunt_lock:
            self.prey_dict[pid] = -1.0

    def get_alive_preys(self):
        return [pid for pid, energy in self.prey_dict.items() if energy > 0]

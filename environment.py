import os
from multiprocessing import Lock, Manager, Value

from color import colorString


class Environment:
    def __init__(self, duration, initial_grass=100.0):
        self.duration = duration
        self.grass = Value("d", initial_grass)

        manager = Manager()
        self.hunt_lock = Lock()
        self.prey_dict = manager.dict()

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
            else:
                print(
                    colorString(
                        "red",
                        f"[Environment {os.getpid()}] Not enough grass to consume. Remaining grass: {self.grass.value}",
                    )
                )

    # Give all the methods to interact with the preys

    def register_prey(self, pid, energy):
        self.prey_dict[pid] = True

    def unregister_prey(self, pid):
        if pid in self.prey_dict:
            del self.prey_dict[pid]

    def mark_prey_dead(self, pid):
        with self.hunt_lock:
            if pid in self.prey_dict and self.prey_dict[pid]:
                self.prey_dict[pid] = False
                return True
            return False

    # def update_prey_energy(self, pid, energy):
    #     if pid in self.prey_dict:
    #         self.prey_dict[pid][1] = energy

    def get_alive_preys(self):
        return [pid for pid, state in self.prey_dict.items() if state]

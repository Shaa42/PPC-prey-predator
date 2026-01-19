from multiprocessing import Process, Value

from color import colorString


class Environment(Process):
    def __init__(self, duration, initial_grass=100.0):
        super().__init__()
        self.duration = duration
        self.grass = Value("d", initial_grass)

    def consume_grass(self, amount=2.0):
        with self.grass.get_lock():
            if self.grass.value >= amount:
                self.grass.value -= amount
                print(
                    colorString(
                        "red",
                        f"[Environment {self.pid}] Grass consumed: {amount}. Remaining grass: {self.grass.value}",
                    )
                )
            else:
                print(
                    colorString(
                        "red",
                        f"[Environment {self.pid}] Not enough grass to consume. Remaining grass: {self.grass.value}",
                    )
                )

    def run(self):
        pass

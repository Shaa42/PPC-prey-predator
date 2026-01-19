from multiprocessing import Process


class Predator(Process):
    def __init__(self, environment, duration):
        super().__init__()
        self.environment = environment
        self.duration = duration

    def kill_prey(self, preyPID):
        # Kill prey process from its PID
        ...

    def run(self):
        # print(f"[Predator {self.pid}] is running.")
        pass

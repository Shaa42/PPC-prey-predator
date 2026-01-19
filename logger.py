from multiprocessing import Process


class Logger(Process):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def run(self):
        while True:
            message = self.log_queue.get()
            if message == "__STOP__":
                break
            print(message)

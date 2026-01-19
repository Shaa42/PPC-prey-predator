import random as rd 
from multiprocessing import Queue

from environment import Environment
from logger import Logger
from predator import Predator
from prey import Prey

if __name__ == "__main__":
    sim_duration = 5.0

    # Create a new environment
    environment = Environment(duration=sim_duration, initial_grass=500.0)
    environment.start()

    log_queue = Queue()
    logger = Logger(log_queue)
    logger.start()

    # Create a pool of predator
    predators = [Predator(environment, duration=sim_duration) for _ in range(5)]
    for predator in predators:
        predator.start()

    # Create a pool of prey
    preys = [
        Prey(environment, duration=sim_duration, log_queue=log_queue) for _ in range(5)
    ]
    for prey in preys:
        prey.start()

    # Wait for all processes to finish
    for predator in predators:
        predator.join()

    for prey in preys:
        prey.join()

    environment.join()

    log_queue.put("__STOP__")
    logger.join()

from multiprocessing import Queue

from environment import Environment
from logger import Logger
from predator import Predator
from prey import Prey

if __name__ == "__main__":
    sim_duration = 20.0
    n_predateur = 5
    n_proies = 2 * n_predateur

    # Create a new environment
    environment = Environment(duration=sim_duration, initial_grass=500.0)

    log_queue = Queue()
    logger = Logger(log_queue)
    logger.start()

    # Create a pool of prey
    preys = [
        Prey(environment, duration=sim_duration, log_queue=log_queue)
        for _ in range(n_proies)
    ]

    # Create a pool of predator
    predators = [
        Predator(environment, duration=sim_duration, log_queue=log_queue)
        for _ in range(n_predateur)
    ]

    # Start all processes
    for prey in preys:
        prey.start()

    for predator in predators:
        predator.start()

    # Wait for all processes to finish
    for prey in preys:
        prey.join()

    for predator in predators:
        predator.join()

    log_queue.put("__STOP__")
    logger.join()

from multiprocessing import Queue

import constants
from display import Display
from environment import Environment
from predator import Predator
from prey import Prey

if __name__ == "__main__":
    sim_duration = constants.SIMULATION_DURATION
    n_predateur = constants.N_PREDATORS
    n_proies = constants.N_PREYS

    log_queue = Queue()
    reproduction_queue = Queue()
    logger = Display(log_queue)
    logger.start()

    # Create a new environment
    envi = Environment(
        duration=sim_duration + 3,
        log_queue=log_queue,
        initial_grass=constants.INITIAL_GRASS,
    )
    envi.start()

    # Give the environment time to start
    # time.sleep(1.0)

    # Create a pool of prey
    preys = [
        Prey(
            duration=sim_duration,
            log_queue=log_queue,
        )
        for _ in range(n_proies)
    ]

    # Create a pool of predator
    predators = [
        Predator(
            duration=sim_duration,
            log_queue=log_queue,
        )
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

    envi.join()

    log_queue.put("__STOP__")
    logger.join()

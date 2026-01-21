from multiprocessing import Barrier, Queue

from environment import Environment
from logger import Logger
from predator import Predator
from prey import Prey

if __name__ == "__main__":
    sim_duration = 5.0
    n_predators = 3
    n_preys = 5 * n_predators

    # Create a new environment
    environment = Environment(duration=sim_duration, initial_grass=500.0)
    log_queue = Queue()
    logger = Logger(log_queue)
    logger.start()

    barrier = Barrier(n_preys + n_predators)

    # Create a pool of prey
    preys = [
        Prey(environment, duration=sim_duration, log_queue=log_queue, barrier=barrier)
        for _ in range(n_preys)
    ]

    # Create a pool of predator
    predators = [
        Predator(
            environment, duration=sim_duration, log_queue=log_queue, barrier=barrier
        )
        for _ in range(n_predators)
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


    print("\nFINAL SIMULATION STATE")

    print("Grass remaining: ", environment.grass.value)

    survivors = [pid for pid, energy in environment.prey_dict.items() if energy > 0]
    print("Preys surviving: ", len(survivors), "/", n_preys)
    for pid in survivors:
        print("  Prey ", pid, ": ", environment.pred_prey[pid])

    print("\nPredator Status:")
    for pid in predators:
        print("  Predator ", pid, ": ", environment.pred_dict[pid])

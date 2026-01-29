import time
from multiprocessing import Queue

import constants
from color import colorString
from display import Display
from environment import Environment
from predator import Predator
from prey import Prey


def log(color, msg):
    global log_queue
    if log_queue is not None and msg.strip():
        log_queue.put(colorString(color, msg))


if __name__ == "__main__":
    sim_duration = constants.SIMULATION_DURATION
    n_predateurs = constants.N_PREDATORS
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
            reproduction_queue=reproduction_queue,
        )
        for _ in range(n_proies)
    ]

    # Create a pool of predator
    predators = [
        Predator(
            duration=sim_duration,
            log_queue=log_queue,
            reproduction_queue=reproduction_queue,
        )
        for _ in range(n_predateurs)
    ]

    # Start all processes
    for prey in preys:
        prey.start()

    for predator in predators:
        predator.start()

    all_agents = preys + predators
    start_time = time.time()
    while any(p.is_alive() for p in all_agents):
        try:
            new_born_type = reproduction_queue.get(timeout=0.1)
            dt = time.time() - start_time
            remaining_time = max(0, sim_duration - dt)
            if new_born_type == "prey":
                new_agent = Prey(
                    duration=remaining_time,
                    log_queue=log_queue,
                    reproduction_queue=reproduction_queue,
                )
                preys.append(new_agent)
                n_proies += 1
            else:
                new_agent = Predator(
                    duration=remaining_time,
                    log_queue=log_queue,
                    reproduction_queue=reproduction_queue,
                )
                predators.append(new_agent)
                n_predateurs += 1
            new_agent.start()
            all_agents.append(new_agent)
        except Exception:
            continue

    # Wait for all processes to finish
    # for agent in all_agents:
    #     agent.join()

    for prey in preys:
        prey.join()

    for predator in predators:
        predator.join()

    envi.join()

    log("", "")
    log("yellow", "======================================")
    log("yellow", "STATISTIQUES FINALES DE LA SIMULATION")
    # 1. Herbe restante
    log("yellow", f"Herbe restante : {envi.grass.value}")
    # 2. Proies
    surviving_preys = {
        pid: data for pid, data in envi.prey_dict.items() if data.get("alive")
    }
    log("yellow", f"Proies survivantes : {len(surviving_preys)} / {n_proies}")
    for pid, data in surviving_preys.items():
        log("yellow", f"  - Proie {pid} : {data['energy']} énergie")
    # 3. Prédateurs
    surviving_preds = {
        pid: data for pid, data in envi.pred_dict.items() if data.get("alive")
    }
    log("yellow", f"Prédateurs survivants : {len(surviving_preds)} / {n_predateurs}")
    for pid, data in surviving_preds.items():
        log("yellow", f"  - Prédateur {pid} : {data['energy']} énergie")

    log_queue.put("__STOP__")
    logger.join()

import json
import random as rd
import socket
import sys
import time
from multiprocessing import Process

import constants
from color import colorString


class Predator(Process):
    def __init__(self, duration, log_queue):
        """
        Predator constructor
        """
        super().__init__()
        self.duration = duration
        self.log_queue = log_queue
        self.socket = None
        self.energy = constants.PREDATOR_INIT_ENERGY

    def log(self, color, msg):
        if self.log_queue is not None and msg.strip():
            self.log_queue.put(colorString(color, msg))

    def connect_to_envi(self):
        retries = 5
        while retries > 0:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect(("localhost", 8558))
                return True
            except ConnectionRefusedError:
                time.sleep(1.0)
                retries -= 1
        return False

    def form_request(self, request, info):
        return json.dumps(
            {"pid": self.pid, "type": "predator", "request": request, "info": info}
        )

    def send_request(self, request_type, info):
        if self.socket is None:
            self.log(
                "red", f"[Predator {self.pid}] Cannot send request: No connection."
            )
            return

        try:
            message = self.form_request(request_type, info)
            self.socket.sendall(bytes(message, encoding="utf-8"))

            reponse = self.socket.recv(2048)
            if not reponse:
                return None

            return json.loads(reponse.decode())

        except Exception as e:
            self.log("red", f"[Predator {self.pid}] Error sending request: {e}")

    def register(self):
        response = self.send_request("register", self.energy)
        if response is None or response.get("status") != "ok":
            self.log("red", f"[Predator {self.pid}] Registration failed.")

    def unregister(self):
        response = self.send_request("unregister", None)
        if response is None or response.get("status") != "ok":
            self.log("red", f"[Predator {self.pid}] Unregistration failed.")

    # Hunting logic
    def kill_prey(self, prey):
        succes = self.send_request("mark_dead", {"pid": prey, "type": "prey"})
        if succes and succes.get("status") == "ok":
            self.log("blue", f"[Predator {self.pid}] killed prey {prey}")
            self.gain_energy(constants.PREDATOR_PREY_EAT + float(rd.randint(-5, 5)))

    def kill_probability(self, n):
        # Has 1 chance over n to return true
        if rd.random() < 1 / n:
            return True
        return False

    def hunt(self):
        response = self.send_request("get_active_preys", None)
        if response and response.get("active_preys"):
            active_preys = response.get("active_preys")
            prey = rd.choice(active_preys)
            self.kill_prey(prey)
            return True
        return False

    # Energy management
    def lose_energy(self, amount):
        self.energy = max(0.0, self.energy - amount)
        response = self.send_request("update_energy", self.energy)
        if response and response.get("status") == "ok":
            self.log(
                "blue",
                f"[Predator {self.pid}] lost {amount} energy. {self.energy} energy left.",
            )

    def gain_energy(self, amount):
        self.energy = min(100.0, self.energy + amount)
        response = self.send_request("update_energy", self.energy)
        if response and response.get("status") == "ok":
            self.log(
                "blue",
                f"[Predator {self.pid}] gained {amount} energy. {self.energy} energy left.",
            )

    # Main logic
    def run(self):
        # Connect to environment
        if not self.connect_to_envi():
            self.log("red", "Failed to connect to environment")
            sys.exit(1)

        self.register()

        # Wait for processes to load
        time.sleep(0.5)

        start = time.time()
        while time.time() - start < self.duration:
            # Check connection
            status = self.send_request("check_status", None)
            if status is None:
                self.log("red", f"[Predator {self.pid}] Connection lost.")
                sys.exit(0)

            if self.energy <= 0.0:
                self.log("red", f"[Predator {self.pid}] has died.")
                self.unregister()
                sys.exit(0)

            time.sleep(rd.uniform(0.0, 2.0))
            self.log("blue", f"[Predator {self.pid}] is on the hunt.")
            if self.kill_probability(4):
                if not self.hunt():
                    self.log("blue", f"[Predator {self.pid}] killed no prey.")
            self.lose_energy(constants.PREDATOR_ENERGY_LOSS + float(rd.randint(-2, 5)))
            time.sleep(rd.uniform(4.0, 6.0))

        self.log("cyan", f"[Predator {self.pid}] lived peacefully.")

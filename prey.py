import json
import random as rd
import socket
import sys
import time
from multiprocessing import Process

import constants
from color import colorString


class Prey(Process):
    def __init__(self, duration, log_queue, reproduction_queue):
        """
        Prey constructor
        """
        super().__init__()
        self.duration = duration
        self.log_queue = log_queue
        self.reprod_queue = reproduction_queue
        self.socket = None
        self.energy = constants.PREY_INIT_ENERGY

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
            {"pid": self.pid, "type": "prey", "request": request, "info": info}
        )

    def send_request(self, request_type, info):
        if self.socket is None:
            self.log("red", f"[Prey {self.pid}] Cannot send request: No connection.")
            return

        try:
            message = self.form_request(request_type, info)
            self.socket.sendall(bytes(message, encoding="utf-8"))

            reponse = self.socket.recv(2048)
            if not reponse:
                return None

            return json.loads(reponse.decode())

        except Exception as e:
            self.log("red", f"[Prey {self.pid}] Error sending request: {e}")

    def register(self):
        response = self.send_request("register", self.energy)
        if response is None or response.get("status") != "ok":
            self.log("red", f"[Prey {self.pid}] Registration failed.")

    def unregister(self):
        response = self.send_request("unregister", None)
        if response is None or response.get("status") != "ok":
            self.log("red", f"[Prey {self.pid}] Unregistration failed.")

    def eat_grass(self, n, amount):
        # Has 1 chance over n to eat grass
        if rd.random() < 1 / n:
            response = self.send_request("eat_grass", amount + float(rd.randint(-1, 1)))
            if response and response.get("accepted"):
                self.log(
                    "green",
                    f"[Prey {self.pid}] ate {amount} unit of grass. {response.get('grass_left')} unit of grass left.",
                )
                self.gain_energy(amount / 2)

    # Energy management
    def lose_energy(self, amount):
        self.energy = max(0.0, self.energy - amount)
        response = self.send_request("update_energy", self.energy)
        if response and response.get("status") == "ok":
            self.log(
                "green",
                f"[Prey {self.pid}] lost {amount} energy. {self.energy} energy left.",
            )

    def gain_energy(self, amount):
        self.energy = min(100.0, self.energy + amount)
        response = self.send_request("update_energy", self.energy)
        if response and response.get("status") == "ok":
            self.log(
                "green",
                f"[Prey {self.pid}] gained {amount} energy. {self.energy} energy left.",
            )

    def reprod_prey(self):
        if self.energy >= constants.PREY_REPRODUCTION_THRESHOLD:
            self.lose_energy(20 + float(rd.randint(5, 20)))
            response = self.send_request("update_energy", self.energy)
            if response and response.get("status") == "ok":
                self.log(
                    "bright_magenta",
                    f"[Prey {self.pid}] created an offspring. {self.energy} energy left.",
                )
            self.reprod_queue.put("prey")
            return True
        return False

    def run(self):
        # Connect to environment
        if not self.connect_to_envi():
            self.log("red", "Failed to connect to environment")
            sys.exit(1)

        # register
        self.register()

        # Wait for processes to load
        time.sleep(0.5)

        start = time.time()
        while time.time() - start < self.duration:
            # Check if alive
            status = self.send_request("check_status", None)
            if status is None:
                self.log("red", f"[Prey {self.pid}] Connection lost.")
                sys.exit(0)

            if not status.get("alive", True):
                self.log("red", f"[Prey {self.pid}] has been killed.")
                self.unregister()
                sys.exit(0)
            if self.energy <= 0.0:
                self.log("red", f"[Prey {self.pid}] has died.")
                self.unregister()
                sys.exit(0)

            time.sleep(rd.uniform(0.0, 1.0))
            self.log("green", f"[Prey {self.pid}] is grazing.")

            if self.reprod_prey():
                return

            self.eat_grass(1, constants.PREY_GRASS_EAT + float(rd.randint(-2, 2)))
            self.lose_energy(constants.PREY_ENERGY_LOSS + float(rd.randint(-2, 5)))
            time.sleep(rd.uniform(2.0, 3.0))

        self.log("magenta", f"[Prey {self.pid}] lived peacefully.")

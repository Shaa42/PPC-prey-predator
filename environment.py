import json
import socket
import threading
import time
from multiprocessing import Manager, Process

import constants
from color import colorString

"""
Mémoire partagée :
envi_dict's structure :
{
    'grass': Value('d', initial_grass),
    'prey_dict': manager.dict({
        pid1: True,
        pid2: False,
        ...
    'pred_dict': manager.dict({
        pid1: True,
        pid2: False,
        ...
    })
}
"""


class Environment(Process):
    def __init__(self, duration, log_queue, initial_grass=100.0):
        super().__init__()
        self.duration = duration
        self.log_queue = log_queue

        manager = Manager()

        self.grass_lock = manager.Lock()
        self.grass = manager.Value("d", initial_grass)

        self.prey_lock = manager.Lock()
        self.prey_dict = manager.dict()

        self.pred_lock = manager.Lock()
        self.pred_dict = manager.dict()

    def log(self, color, msg):
        if self.log_queue is not None and msg.strip():
            self.log_queue.put(colorString(color, msg))

    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(2048)
                if not data:
                    break

                try:
                    request = data.decode()
                    if not request.strip():
                        continue

                    request = json.loads(request)
                    response = self.handle_request(request)

                    if response:
                        response_str = json.dumps(response)
                        client_socket.sendall(bytes(response_str, encoding="utf-8"))

                except json.JSONDecodeError as e:
                    self.log("red", f"Invalid JSON from {address}: {request} -> {e}")

        except Exception as e:
            self.log("red", f"Error handling client {address}: {e}")
        finally:
            # self.log("yellow", f"Connection closed from {address}")
            client_socket.close()

    def handle_request(self, request):
        req = request["request"]
        type = request["type"]
        pid = request["pid"]
        info = request["info"]

        response = {}

        # Choose the right dict
        if type == "prey":
            target_lock = self.prey_lock
            target_dict = self.prey_dict
        else:
            target_lock = self.pred_lock
            target_dict = self.pred_dict

        match req:
            case "register":
                energy = info
                with target_lock:
                    self.log("yellow", f"Registering {type} {pid}")
                    target_dict[pid] = {"alive": True, "energy": energy}
                response = {"status": "ok"}

            case "unregister":
                with target_lock:
                    if pid in target_dict:
                        self.log("yellow", f"Unregistering {type} {pid}")
                        del target_dict[pid]
                response = {"status": "ok"}

            case "mark_dead":
                # Default to self (suicide/starvation)
                target_pid = pid
                target_type = type

                # If killing someone else
                if info and isinstance(info, dict) and "pid" in info:
                    target_pid = info["pid"]
                    target_type = info.get("type", "prey")

                if target_type == "prey":
                    t_lock = self.prey_lock
                    t_dict = self.prey_dict
                else:
                    t_lock = self.pred_lock
                    t_dict = self.pred_dict

                with t_lock:
                    if target_pid in t_dict:
                        entry = t_dict[target_pid]
                        entry["alive"] = False
                        t_dict[target_pid] = entry
                response = {"status": "ok"}

            case "check_status":
                with target_lock:
                    if pid in target_dict:
                        is_alive = target_dict[pid].get("alive", False)
                        response = {"alive": is_alive}
                    else:
                        response = {"alive": False}

            case "update_energy":
                with target_lock:
                    # self.log("yellow", f"Updating energy for {type} {pid} to {info}")
                    if pid in target_dict:
                        entry = target_dict[pid]
                        entry["energy"] = info
                        target_dict[pid] = entry
                response = {"status": "ok"}

            case "get_alive_preys":
                with self.prey_lock:
                    alive_preys = [
                        p_id
                        for p_id, data in self.prey_dict.items()
                        if data.get("alive") is True
                    ]
                response = {"alive_preys": alive_preys}

            case "get_active_preys":
                with self.prey_lock:
                    active_preys = [
                        p_id
                        for p_id, data in self.prey_dict.items()
                        if data.get("energy", 0) <= constants.ACTIVE_THRESHOLD
                        and data.get("alive") is True
                    ]
                response = {"active_preys": active_preys}

            case "eat_grass":
                amount = info
                with self.grass_lock:
                    if self.grass.value >= amount:
                        self.grass.value -= amount
                        response = {"accepted": True, "grass_left": self.grass.value}
                    else:
                        response = {"accepted": False, "grass_left": self.grass.value}
            case _:
                self.log("red", f"Unknown request type: {request} from {pid}")
                response = {"error": "unknown_request"}

        return response

    def run(self):
        HOSTNAME = "localhost"
        PORT = 8558
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOSTNAME, PORT))
        server_socket.listen(16)
        server_socket.settimeout(1.0)

        try:
            start = time.time()
            while time.time() - start < self.duration:
                try:
                    client_socket, address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True,
                    )

                    client_thread.start()

                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            self.log("yellow", "Shutting envi.")
        finally:
            self.log("yellow", "Environment shutting down.")
            server_socket.close()

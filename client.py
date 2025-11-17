import json
import os
import threading
import time
from socket import *
from playsound import playsound

HOST = 'localhost'
PORT = 12345
HEARTBEAT_INTERVAL = 5

class TaskClient:
    def __init__(self):
        self.client_id = None
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((HOST, PORT))

    def send_request(self, message):
        self.sock.send(json.dumps(message).encode())
        response = self.sock.recv(1024)
        return json.loads(response.decode())

    def register(self):
        response = self.send_request({"action": "register"})
        if response["status"] == "ok":
            self.client_id = response["client_id"]
            print(f"[CLIENT] Registered! My ID is {self.client_id}")

    def submit_task(self, task):
        response = self.send_request({"action": "submit_task", "task": task})
        print(f"[CLIENT] Submitted task: {response}")

    def get_tasks(self):
        response = self.send_request({"action": "get_tasks"})
        print(f"[CLIENT] Current tasks: {response}")

    def schedule_task(self, task_name, delay_seconds):

        def task_thread():
            print(f"[CLIENT {self.client_id}] Scheduled '{task_name}' in {delay_seconds} sec", flush=True)
            time.sleep(delay_seconds)
            print(f"[CLIENT {self.client_id}] Executing '{task_name}' now!", flush=True)

            # Attempt to play sound
            sound_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification.mp3")
            if os.path.exists(sound_file):
                try:
                    playsound(sound_file)
                    print(f"[CLIENT {self.client_id}] Played sound for '{task_name}'", flush=True)
                except Exception as e:
                    print(f"[CLIENT {self.client_id}] ERROR playing sound: {e}", flush=True)
            else:
                print(f"[CLIENT {self.client_id}] Sound file not found: {sound_file}", flush=True)

        t = threading.Thread(target=task_thread, daemon=False)
        t.start()
        return t

    def run_heartbeat(self):
        while True:
            if self.client_id:
                try:
                    self.send_request({"action": "heartbeat"})
                except:
                    break
            time.sleep(HEARTBEAT_INTERVAL)

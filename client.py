import json
import os
import threading
import time
from socket import *
import simpleaudio as sa
from datetime import datetime

HOST = 'localhost'
PORT = 12345
HEARTBEAT_INTERVAL = 5

class TaskClient:
    def __init__(self):
        self.client_id = None
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.lock = threading.Lock()

    def send_request(self, message):
        with self.lock:
            self.sock.send(json.dumps(message).encode())
            response = self.sock.recv(4096)
        try:
            return json.loads(response.decode())
        except:
            return {"status": "error", "error": "invalid_response"}

    def register(self):
        response = self.send_request({"action": "register"})
        if response.get("status") == "ok":
            self.client_id = response.get("client_id")
            print(f"[CLIENT] Registered! My ID is {self.client_id}")

    def submit_task(self, task, scheduled_time=None):
        message = {
            "action": "submit_task",
            "task": task,
            "scheduled_time": scheduled_time
        }
        response = self.send_request(message)
        print(f"[CLIENT] Submitted task: {response}")
        return response

    def get_tasks(self):
        response = self.send_request({"action": "get_tasks"})
        print(f"[CLIENT] Current tasks: {response}")
        return response
    
    def play_sound(self):
        # added wav sound option
        sound_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification.wav")

        if not os.path.exists(sound_file):
            print(f"[CLIENT {self.client_id}] Sound file not found: {sound_file}")
            return

        try:
            wave = sa.WaveObject.from_wave_file(sound_file)
            play_obj = wave.play()
            #commented out so multiple tasks can play audio at nearly 
            # the same time without  other threads
            # play_obj.wait_done()
            print(f"[CLIENT {self.client_id}] Played sound successfully")
        except Exception as e:
            print(f"[CLIENT {self.client_id}] Error playing sound: {e}")

    def schedule_task(self, task_name, scheduled_time):
        """
        scheduled_time: absolute epoch seconds (float)
        """
        def task_thread():
            now = time.time()
            delay = scheduled_time - now

            if delay > 0:
                print(f"[CLIENT {self.client_id}] Scheduled '{task_name}' at {datetime.fromtimestamp(scheduled_time)} "
                      f"(in {delay:.1f}s)")
                time.sleep(delay)
            else:
                print(f"[CLIENT {self.client_id}] Time already passed—running now")

            print(f"[CLIENT {self.client_id}] Executing '{task_name}' now!", flush=True)

            self.play_sound()

        t = threading.Thread(target=task_thread, daemon=False)
        t.start()
        return t

    def run_heartbeat(self):
        while True:
            if self.client_id:
                try:
                    self.send_request({"action": "heartbeat"})
                except Exception as e:
                    print(f"[CLIENT {self.client_id}] Heartbeat error, stopping heartbeats: {e}")
                    break
            time.sleep(HEARTBEAT_INTERVAL)

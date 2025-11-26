import json
import os
import threading
import time
from socket import *
from urllib import response
import simpleaudio as sa
from datetime import datetime

HOST = 'localhost'
PORT = 12345
HEARTBEAT_INTERVAL = 1  # seconds between heartbeats
POLL_INTERVAL = 2   # seconds for how often server is polled for due tasks

class TaskClient:
    def __init__(self):
        self.client_id = None
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.lock = threading.Lock()
        self.running = True
        self.slept = False  #for crash testing purposes

    def send_request(self, message):
        """
        Send a request safely. Only HEARTBEAT messages may be skipped to simulate a crash.
        """
        if not self.running:
            return {"status": "error", "error": "client_crashed"}
        
        if self.client_id == 1 and message.get("action") == "heartbeat" and not self.slept:
            self.simulate_crash()  # actually invoke the crash
            raise ConnectionResetError("Simulated heartbeat crash")
        
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
    
    def fetch_due(self):
        """
        Poll the server for tasks that are due for this client.
        Server will remove and return tasks that should be executed now, or had no scheduled_time.
        """
        response = self.send_request({"action": "fetch_due"})
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
            # re-enabled, otherwise sound wouldnt fully play
            play_obj.wait_done()
            print(f"[CLIENT {self.client_id}] Played sound successfully")
        except Exception as e:
            print(f"[CLIENT {self.client_id}] Error playing sound: {e}")
            self.running = False

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
        while self.running:
            if self.client_id:
                try:
                    self.send_request({"action": "heartbeat"})
                    print(f"[CLIENT {self.client_id}] Sent heartbeat")
                except Exception as e:
                    print(f"[CLIENT {self.client_id}] Heartbeat error, stopping heartbeats: {e}")
                    break
            time.sleep(HEARTBEAT_INTERVAL)

    def simulate_crash(self):
        """
        Immediately stops all client activity and closes socket.
        Tasks should then be reassigned by the scheduler.
        """
        print(f"\n***** CLIENT {self.client_id} CRASHED *****\n")
        self.running = False
        try:
            self.sock.shutdown(SHUT_RDWR)
        except:
            pass
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    c = TaskClient()
    c.register()

    hb = threading.Thread(target=c.run_heartbeat, daemon=True)
    hb.start()

    while True:
        time.sleep(1)
        

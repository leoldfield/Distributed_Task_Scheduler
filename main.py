import threading
import time
from server import run_server
from client import TaskClient
from datetime import datetime
import os

POLL_INTERVAL = 2   # seconds for how often server is polled for due tasks

def client_task_poller(client):
    """Continuously fetch due tasks from the server and execute them."""
    while client.running:
        try:
            response = client.fetch_due()
            for task in response.get("tasks", []):
                print(f"[CLIENT {client.client_id}] Executing task '{task['name']}' now!")
                client.play_sound()
        except Exception as e:
            print(f"[CLIENT {client.client_id}] Polling error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":

    # Start server
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    print("[MAIN] Server is up and running")

    # Create clients
    clients = []
    for i in range(3):
        c = TaskClient()
        c.register()
        threading.Thread(target=c.run_heartbeat, daemon=True).start()
        clients.append(c)

    print(f"[MAIN] {len(clients)} clients registered")

    # Submit and schedule tasks
    tasks = [
        {"name": "Task A"},
        {"name": "Task B"},
        {"name": "Task C"}
    ]


    task_threads = []

    for i, task in enumerate(tasks):
        client = clients[i % len(clients)]
        if not client.running:
            print(f"[MAIN] Skipping task '{task['name']}' because client {client.client_id} crashed")
            continue

        scheduled_time = time.time() + (3 + i)
        response = client.submit_task(task, scheduled_time=scheduled_time)
        if response.get("status") != "ok":
            print(f"[MAIN] Task '{task['name']}' submission failed for client {client.client_id}: {response}")
            continue

        print(f"[MAIN] Submitted task '{task['name']}' to client {client.client_id} scheduled at {time.ctime(scheduled_time)}")
        t = client.schedule_task(task["name"], scheduled_time)
        task_threads.append(t)
        print(f"[MAIN] Scheduled thread for {task['name']}")

    # Wait for task threads
    for t in task_threads:
        t.join()

    print("[MAIN] All tasks should have triggered sounds")

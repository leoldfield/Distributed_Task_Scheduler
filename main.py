import threading
import time
from server import run_server
from client import TaskClient
import os

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

    # define thread
    task_threads = []

    for i, task in enumerate(tasks):
        client = clients[i % len(clients)]
        #schedule 3_i seconds from now
        scheduled_time = time.time() + (3 + i)
        client.submit_task(task, scheduled_time=scheduled_time)
        print(f"[MAIN] About to schedule task {task['name']} at {scheduled_time} ({time.ctime(scheduled_time)})")
        t = client.schedule_task(task["name"], scheduled_time)
        task_threads.append(t)
        print(f"[MAIN] Scheduled thread for {task['name']}")

    # Wait for threads
    for t in task_threads:
        t.join()

    print("[MAIN] All tasks should have triggered sounds")

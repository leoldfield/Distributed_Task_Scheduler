import json
import threading
from socket import *
from datetime import datetime
import time

HOST = 'localhost'
PORT = 12345

clients = {}
tasks = {}
next_client_id = 1
next_task_id = 1
lock = threading.Lock()

HEARTBEAT_TIMEOUT = 2  # seconds after client is considered dead
SCHEDULER_INTERVAL = 1  # seconds in how often housekeeping runs

def now_ts():
    return time.time()

def handle_client(conn, addr):
    global next_client_id, next_task_id
    client_id = None
    try:
        data = conn.recv(4096)
        if not data:
            return
        message = json.loads(data.decode())
        if message.get("action") == "register":
            with lock:
                client_id = next_client_id
                next_client_id += 1
                clients[client_id] = {"conn": conn, "addr": addr, "last_heartbeat": now_ts()}
            conn.send(json.dumps({"status": "ok", "client_id": client_id}).encode())
            print(f"[SERVER] Client {client_id} registered from {addr}")
        else:
            conn.send(json.dumps({"status": "error", "error": "not_registered"}).encode())
            return

        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                message = json.loads(data.decode())
            except Exception as e:
                conn.send(json.dumps({"status": "error", "error": "invalid_json"}).encode())
                continue 

            action = message.get("action")

            #keeps track of when each task is scheduled
            if action == "submit_task":
                task = message.get("task", {})
                scheduled_time = message.get("scheduled_time")  # epoch seconds (float) or None
                with lock:
                    task_id = next_task_id
                    next_task_id += 1
                    task["client_id"] = client_id
                    task["scheduled_time"] = scheduled_time
                    task["submitted_at"] = now_ts()
                    tasks[task_id] = task
                conn.send(json.dumps({"status": "ok", "task_id": task_id}).encode())
                print(f"[SERVER] Task submitted: {task}, assigned to client {client_id}")

            elif action == "get_tasks":
                with lock:
                    client_tasks = {tid: t for tid, t in tasks.items() if t.get("client_id") == client_id}
                conn.send(json.dumps({"status": "ok", "tasks": client_tasks}).encode())

            elif action == "heartbeat":
                # Update last_heartbeat timestamp
                with lock:
                    if client_id in clients:
                        clients[client_id]["last_heartbeat"] = now_ts()
                print(f"[SERVER] Heartbeat received from client {client_id}")
                conn.send(json.dumps({"status": "ok"}).encode())

            else:
                conn.send(json.dumps({"status": "error", "error": f"unknown_action {action}"}).encode())

    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        if client_id:
            with lock:
                clients.pop(client_id, None)
        try:
            conn.close()
        except:
            pass
        print(f"[SERVER] Connection with {addr} closed")

def scheduler_housekeeping():
    """
    Detect overdue tasks and remove dead clients.
    Reassign tasks from dead clients to active clients.
    """
    while True:
        time.sleep(SCHEDULER_INTERVAL)
        now = now_ts()

        # Detect overdue tasks
        overdue = []
        with lock:
            # --- Detect overdue tasks ---
            overdue = [(tid, t) for tid, t in tasks.items()
                       if t.get("scheduled_time") is not None and t["scheduled_time"] <= now]
            if overdue:
                print(f"[SCHEDULER] Overdue tasks waiting to be fetched: {[tid for tid, _ in overdue]}")

            # --- Detect dead clients ---
            dead_clients = [cid for cid, meta in clients.items()
                            if now - meta.get("last_heartbeat", 0) > HEARTBEAT_TIMEOUT]
            
            if dead_clients:
                print(f"[SCHEDULER] Dead clients detected: {dead_clients}")
            
            # --- Reassign tasks from dead clients ---
            for tid, t in tasks.items():
                cid = t.get("client_id")
                if cid in dead_clients:
                    live_clients = [c for c in clients.keys() if c not in dead_clients]
                    if live_clients:
                        new_cid = live_clients[0]
                        t["client_id"] = new_cid
                        print(f"[SCHEDULER] Reassigned task {tid} from dead client {cid} to {new_cid}")
                    else:
                        print(f"[SCHEDULER] No active clients to reassign task {tid}")

            # --- Remove dead clients after reassignment ---
            for cid in dead_clients:
                meta = clients.pop(cid, None)
                if meta:
                    try:
                        meta["conn"].close()
                    except:
                        pass
                print(f"[SCHEDULER] Removed dead client {cid}")

        with lock:
            print(f"[SCHEDULER] Active clients: {list(clients.keys())}, Total tasks: {len(tasks)}")

def run_server():
    print(f"[SERVER] Listening on {HOST}:{PORT}...")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)

    # Start housekeeping thread
    threading.Thread(target=scheduler_housekeeping, daemon=True).start()
    
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()

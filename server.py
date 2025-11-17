import json
import threading
from socket import *

HOST = 'localhost'
PORT = 12345

clients = {}
tasks = {}
next_client_id = 1
next_task_id = 1
lock = threading.Lock()

def handle_client(conn, addr):
    global next_client_id, next_task_id
    client_id = None
    try:
        data = conn.recv(1024)
        if not data:
            return
        message = json.loads(data.decode())
        if message.get("action") == "register":
            with lock:
                client_id = next_client_id
                next_client_id += 1
                clients[client_id] = conn
            conn.send(json.dumps({"status": "ok", "client_id": client_id}).encode())
            print(f"[SERVER] Client {client_id} registered from {addr}")

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = json.loads(data.decode())
            if message.get("action") == "submit_task":
                task = message.get("task")
                with lock:
                    task_id = next_task_id
                    next_task_id += 1
                    task["client_id"] = client_id
                    tasks[task_id] = task
                conn.send(json.dumps({"status": "ok", "task_id": task_id}).encode())
                print(f"[SERVER] Task submitted: {task}, assigned to client {client_id}")
            elif message.get("action") == "get_tasks":
                client_tasks = {tid: t for tid, t in tasks.items() if t["client_id"] == client_id}
                conn.send(json.dumps({"status": "ok", "tasks": client_tasks}).encode())
    except Exception as e:
        print(f"[SERVER] Error: {e}")
    finally:
        if client_id:
            with lock:
                clients.pop(client_id, None)
        conn.close()
        print(f"[SERVER] Connection with {addr} closed")

def run_server():
    print(f"[SERVER] Listening on {HOST}:{PORT}...")
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()

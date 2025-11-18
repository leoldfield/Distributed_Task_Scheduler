# Distributed Task Scheduler

## Team Members
- Lindsay Oldfield
- Olivia Sabb
- Angel Paul Antipolo
- Ethan Miller
- Tugba Agdas

## Overview
This project implements a **lightweight distributed task scheduler** that coordinates reminders across multiple client devices using a simple client–server architecture. The primary goal is to demonstrate core distributed systems concepts—**communication, synchronization, fault tolerance, and coordination**—through an implementation that is easy to understand, extend, and evaluate.  

Clients can join or leave dynamically, tasks are reliably delivered using acknowledgments and retries, and local audio reminders are triggered at scheduled times. The system is implemented in **Python** using **sockets** for communication, **JSON** for data serialization, and **threading** for concurrency.

### Interdisciplinary Note
Beyond computer science, this project touches:
- **Operations Research**: Task scheduling strategies  
- **UI/UX Design**: Client-side reminder interface  
- **Acoustics**: Audio reminder notifications  

---

## Features / Methods
- **Client-Server Communication**: TCP sockets with JSON serialization.  
- **Task Scheduling**: Local scheduling on clients with audio reminders using the `playsound` library.  
- **Concurrency**: Server handles multiple clients using threads.  
- **Reliability**: Heartbeat mechanism, at-least-once delivery, and task persistence (JSON/SQLite).  
- **Extensibility**: Supports advanced scheduling policies, cloud deployment, and integration with calendar apps.  

---

## Project Stages

| Stage | Focus | Milestones | Deliverables |
|-------|-------|------------|-------------|
| 1 | Core Communication & Task Handling | - Client-server communication using Python sockets<br>- Server-side in-memory task storage<br>- Client registration & round-robin task assignment | Basic server and client code with task assignment functionality |
| 2 | Local Scheduling & Audio Reminders | - Local task scheduling on client<br>- Audio reminders using `playsound` | Client-side code with scheduled task execution and audio notifications |
| 3 | Concurrency & Heartbeat Monitoring | - Multi-threaded server for concurrent clients<br>- Heartbeat mechanism for client liveness | Multi-threaded server with heartbeat detection |
| 4 | Reliability & Persistence | - At-least-once delivery with acknowledgments<br>- Task persistence (JSON/SQLite) | Reliable task delivery system with persistent storage |
| 5 | Evaluation & Refinement | - Test under network delays and client failures<br>- Identify and resolve issues | Testing report and refined distributed task scheduler |

---

## Task Assignments
- **Lindsay Oldfield**: Project management, testing & evaluation, documentation  
- **Olivia Sabb**: Client-side development, local scheduling, audio reminders  
- **Angel Paul Antipolo**: Server-side development, core communication, advanced scheduling  
- **Ethan Miller**: Reliability, concurrency, heartbeat monitoring, persistence  
- **Tugba Agdas**: DevOps, cloud deployment, future integrations (calendar apps, TLS, broker-backed queues)  

---

## Future Directions
- Transition to **asyncio** or distributed task stores for higher scalability  
- Advanced scheduling policies considering client load  
- Real-world integrations with **Google Calendar, Outlook, or mobile platforms**  
- Cloud deployment on **AWS, Azure, or GCP**  
- Security enhancements with **TLS** and **broker-backed queues** (RabbitMQ, Kafka)  

---

## Setup & Usage
1. Install dependencies:
```bash
pip install playsound==1.2.2
(If on linux, pip install libasound2-dev libjack-jackd2-dev if on linux)
pip install simpleaudio==1.0.4
```

2. Testing
```bash
To test out the task creation and audio, run python3 main.py




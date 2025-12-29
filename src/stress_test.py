import asyncio
import websockets
import json
import random
import time
import argparse
from typing import List

# Configuration
BAD_WORDS = ["spam", "buy crypto", "free money", "badword"]
GOOD_SENTENCES = [
    "Hello everyone!",
    "How is the weather?",
    "This chat is fast.",
    "I love Python.",
    "Real-time systems are cool.",
    "Redis is a great message broker.",
    "Is anyone there?",
    "Just checkin in.",
    "Good morning!",
    "Have a nice day."
]

class StressMetrics:
    def __init__(self):
        self.sent = 0
        self.received = 0
        self.banned = 0
        self.errors = 0
        self.start_time = time.time()
        self.lock = asyncio.Lock()

    async def record_sent(self):
        async with self.lock:
            self.sent += 1

    async def record_received(self):
        async with self.lock:
            self.received += 1

    async def record_ban(self):
        async with self.lock:
            self.banned += 1

    async def record_error(self):
        async with self.lock:
            self.errors += 1

    def report(self):
        duration = time.time() - self.start_time
        print(f"\n--- Stress Test Report ({duration:.2f}s) ---")
        print(f"Total Sent: {self.sent}")
        print(f"Total Received: {self.received}")
        print(f"Total Banned: {self.banned}")
        print(f"Total Errors: {self.errors}")
        print(f"Throughput: {(self.sent + self.received) / duration:.2f} msg/s")
        print("---------------------------------------")

metrics = StressMetrics()

async def chat_user(user_id: str, is_toxic: bool, duration: int, uri: str):
    """Simulates a single user."""
    try:
        async with websockets.connect(f"{uri}/{user_id}") as websocket:
            end_time = time.time() + duration
            
            # Receive loop task
            async def receive_loop():
                try:
                    while True:
                        msg = await websocket.recv()
                        data = json.loads(msg)
                        if data.get("type") == "system" and data.get("status") == "BLOCKED":
                            await metrics.record_ban()
                            return
                        await metrics.record_received()
                except:
                    pass

            recv_task = asyncio.create_task(receive_loop())

            # Send loop
            while time.time() < end_time:
                # Decide content
                is_bad = False
                if is_toxic:
                    # Toxic users send bad words 50% of the time
                    if random.random() < 0.5:
                        text = f"{random.choice(BAD_WORDS)} {random.randint(1, 100)}"
                        is_bad = True
                    else:
                        text = random.choice(GOOD_SENTENCES)
                else:
                    text = random.choice(GOOD_SENTENCES)

                try:
                    await websocket.send(json.dumps({"text": text}))
                    await metrics.record_sent()
                except websockets.exceptions.ConnectionClosed:
                    break # Likely banned/disconnected

                # Variable delay for realism
                await asyncio.sleep(random.uniform(0.1, 0.5))

            recv_task.cancel()

    except Exception:
        # Connection failed or dropped (banned users drop)
        await metrics.record_error()

async def main(users: int, duration: int, toxic_ratio: float):
    uri = "ws://localhost:8000/ws"
    print(f"🚀 Starting Stress Test: {users} users, {duration}s duration, {toxic_ratio*100}% toxic")
    
    tasks = []
    for i in range(users):
        user_id = f"stress_user_{i}"
        is_toxic = random.random() < toxic_ratio
        tasks.append(chat_user(user_id, is_toxic, duration, uri))
    
    await asyncio.gather(*tasks)
    metrics.report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Stress Test")
    parser.add_argument("--users", type=int, default=50, help="Number of concurrent users")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds")
    parser.add_argument("--toxic", type=float, default=0.2, help="Ratio of toxic users (0.0 to 1.0)")
    
    args = parser.parse_args()
    asyncio.run(main(args.users, args.duration, args.toxic))

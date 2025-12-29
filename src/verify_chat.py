import asyncio
import websockets
import json
import sys

async def verify():
    uri = "ws://localhost:8000/ws/test_user_verifier"
    
    print("Connecting to WebSocket...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            history_msg = await websocket.recv()
            print(f"Received: {history_msg[:100]}...")  
            
            print("Sending CLEAN message...")
            await websocket.send(json.dumps({"text": "Hello World, this is a clean message."}))
            
            found = False
            for _ in range(3):
                response = await websocket.recv()
                data = json.loads(response)
                if data.get("type") == "chat" and "Hello World" in data.get("text", ""):
                    print("Received valid message back!")
                    found = True
                    break
            
            if not found:
                print("Did not receive own message back.")
                sys.exit(1)

            print("Sending BAD messages to trigger ban...")
            bad_word = "spam" 
            for i in range(10):
                await websocket.send(json.dumps({"text": f"{bad_word} {i}"}))
                await asyncio.sleep(0.1)
                
            try:
                while True:
                    msg = await websocket.recv()
                    data = json.loads(msg)
                    print(f"Received: {data}")
                    if data.get("type") == "system" and data.get("status") == "BLOCKED":
                        print("Received BLOCKED warning.")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"Connection Closed: Code {e.code} Reason: {e.reason}")
                if e.code == 4003:
                    print("SUCCESS: User was banned.")
                else:
                    print(f"FAILURE: Unexpected close code {e.code}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())

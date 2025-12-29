import asyncio
import json
import logging
from typing import List
from datetime import datetime, timezone

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import get_redis_client, get_db
from .config import Config
from .engine import ModerationEngine
from .messaging import RedisManager
from .models import BlockedUser
from .utils.ratelimit import SlidingWindowLimiter
from .utils.cuckoo import CuckooFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI(title="Chat Moderator Realtime")

moderation_engine = None
redis_client = None
redis_manager = None
rate_limiter = None
cuckoo_filter = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    global moderation_engine, redis_client, redis_manager, rate_limiter, cuckoo_filter
    
    moderation_engine = ModerationEngine()
    
    redis_client = await get_redis_client()
    
    redis_manager = RedisManager(redis_client)
    rate_limiter = SlidingWindowLimiter(redis_client)
    cuckoo_filter = CuckooFilter(redis_client)
    
    asyncio.create_task(redis_listener())
    
    print("System Online: WebSockets + Redis Pub/Sub + ML + Cuckoo Filter")

async def redis_listener():
    pubsub = await redis_manager.subscribe()
    async for message in pubsub.listen():
        if message["type"] == "message":
            await manager.broadcast(message["data"])

import os
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: AsyncSession = Depends(get_db)):
    if await cuckoo_filter.contains(user_id):
        logger.info(f"Connection Rejected (Cuckoo): {user_id}")
        await websocket.close(code=4003, reason="You are banned.")
        return

    ban_reason = await redis_client.get(f"banned:{user_id}")
    if ban_reason:
        await websocket.close(code=4003, reason=f"Banned: {ban_reason}")
        return

    await manager.connect(websocket)
    
    try:
        history = await redis_manager.get_recent_messages()
        await websocket.send_text(json.dumps({"type": "history", "data": history}))

        while True:
            data = await websocket.receive_text()
            
            try:
                payload = json.loads(data)
                text = payload.get("text", "")
            except:
                text = data
            
            if not text.strip():
                continue

            mod_result = moderation_engine.moderate(text)
            
            if mod_result["status"] == "FLAGGED":
                logger.warning(f"Flagged: {user_id} - {text}")
                
                await websocket.send_text(json.dumps({
                    "type": "system", 
                    "status": "BLOCKED", 
                    "reason": mod_result["reason"]
                }))
                
                is_rate_limited = await rate_limiter.record_violation(user_id)
                if is_rate_limited:
                    logger.warning(f"BANNING USER: {user_id}")
                    reason = "Excessive Toxic Behavior"
                    
                    await redis_client.setex(f"banned:{user_id}", Config.BAN_DURATION, reason)
                    
                    await cuckoo_filter.add(user_id)
                    
                    new_ban = BlockedUser(
                        user_id=user_id,
                        reason=reason,
                        banned_until=None
                    )
                    db.add(new_ban)
                    await db.commit()
                    
                    await websocket.close(code=4003, reason="Banned for toxicity.")
                    break
            else:
                msg_obj = {
                    "type": "chat",
                    "user_id": user_id,
                    "text": text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await redis_manager.publish(msg_obj)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS Error: {e}")
        manager.disconnect(websocket)

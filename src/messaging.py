import json
import logging
from redis.asyncio import Redis
from typing import List, Dict

logger = logging.getLogger("uvicorn")

class RedisManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.channel = "chat_global"  
        self.history_key = "chat_history"
        self.history_limit = 50

    async def publish(self, message: dict):
        try:
            await self._add_to_history(message)
            
            await self.redis.publish(self.channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Redis Publish Error: {e}")

    async def subscribe(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel)
        return pubsub

    async def _add_to_history(self, message: dict):
        try:
            val = json.dumps(message)
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.lpush(self.history_key, val)
                pipe.ltrim(self.history_key, 0, self.history_limit - 1)
                await pipe.execute()
        except Exception as e:
            logger.error(f"Redis History Error: {e}")

    async def get_recent_messages(self) -> List[Dict]:
        try:
            raw_msgs = await self.redis.lrange(self.history_key, 0, -1)
            return [json.loads(m) for m in reversed(raw_msgs)]
        except Exception as e:
            logger.error(f"Get History Error: {e}")
            return []

import time
import uuid
import logging
from redis.asyncio import Redis
from ..config import Config

logger = logging.getLogger("uvicorn")

class SlidingWindowLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.window_seconds = Config.RATE_LIMIT_WINDOW
        self.max_offenses = Config.RATE_LIMIT_MAX_OFFENSES

    async def record_violation(self, user_id: str) -> bool:
        key = f"violation_window:{user_id}"
        now = time.time()
        cutoff = now - self.window_seconds

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(key, 0, cutoff)
                
                pipe.zadd(key, {str(uuid.uuid4()): now})
                
                pipe.expire(key, self.window_seconds + 60)
                
                pipe.zcard(key)
                
                results = await pipe.execute()
                
            total_offenses = results[3]
            
            logger.info(f"User {user_id} violations: {total_offenses}/{self.max_offenses}")
            
            return total_offenses >= self.max_offenses

        except Exception as e:
            logger.error(f"Rate limit error: {e}")
            return False

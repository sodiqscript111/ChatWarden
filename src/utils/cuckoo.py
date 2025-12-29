import logging
from redis.asyncio import Redis
from redis.exceptions import ResponseError

logger = logging.getLogger("uvicorn")

class CuckooFilter:

    def __init__(self, redis_client: Redis, key_name: str = "blocked_users_cuckoo"):
        self.redis = redis_client
        self.key = key_name
        self._has_redis_stack = None  

    async def _check_stack_availability(self):

        if self._has_redis_stack is not None:
            return self._has_redis_stack
        
        try:

            await self.redis.execute_command("CF.EXISTS", self.key, "dummy")
            self._has_redis_stack = True
            logger.info("RedisBloom (Cuckoo Filter) detected.")
        except ResponseError as e:
            if "unknown command" in str(e).lower():
                self._has_redis_stack = False
                logger.warning("RedisBloom not detected. Falling back to standard Redis Set.")
            else:
                raise e
        return self._has_redis_stack

    async def add(self, item: str):
        if await self._check_stack_availability():
            try:
                await self.redis.execute_command("CF.ADD", self.key, item)
            except ResponseError:
                pass
        else:
            await self.redis.sadd(self.key, item)

    async def contains(self, item: str) -> bool:
        if await self._check_stack_availability():
            return bool(await self.redis.execute_command("CF.EXISTS", self.key, item))
        else:
            return await self.redis.sismember(self.key, item)

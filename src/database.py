import logging
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import Config

logger = logging.getLogger("uvicorn")

Base = declarative_base()

db_engine = create_async_engine(Config.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=db_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

_redis_client = None

async def get_redis_client():
    global _redis_client
    if _redis_client:
        return _redis_client

    redis_url = Config.REDIS_URL.replace("localhost", "127.0.0.1")
    logger.info(f"Connecting to Redis at {redis_url}...")

    try:
        client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=10
        )
        await client.ping()
        logger.info("Redis Connection Successful")
        _redis_client = client
        return client
    except Exception as e:
        logger.error(f"Redis Connection Failed: {e}")
        raise e

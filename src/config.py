import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    AI_THRESHOLD = float(os.getenv("AI_THRESHOLD", "0.8"))
    BAN_DURATION = int(os.getenv("BAN_DURATION", "600"))
    
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "300"))
    RATE_LIMIT_MAX_OFFENSES = int(os.getenv("RATE_LIMIT_MAX_OFFENSES", "5"))
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/testing")

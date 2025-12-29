from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class BlockedUser(Base):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    reason = Column(String, nullable=True)
    banned_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __repr__(self):
        return f"<BlockedUser(user_id={self.user_id}, reason={self.reason})>"

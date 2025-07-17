from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.database import Base

class LLMCache(Base):
    """
    SQLAlchemy model for caching LLM responses.
    """
    __tablename__ = "llm_cache"
    __table_args__ = {'schema': 'db_ai'} # <--- Specify the schema here

    id = Column(Integer, primary_key=True, index=True)
    prompt_hash = Column(String, unique=True, index=True, nullable=False,
                         comment="Hash of the prompt and parameters for cache key")
    prompt_text = Column(Text, nullable=False)
    llm_provider = Column(String, nullable=False)
    generated_text = Column(Text, nullable=False)
    cached_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True,
                        comment="Optional expiration time for the cache entry")

    def __repr__(self):
        return f"<LLMCache(id={self.id}, prompt_hash='{self.prompt_hash}')>"


class UserData(Base):
    """
    Example model for general user-related data.
    """
    __tablename__ = "user_data"
    __table_args__ = {'schema': 'db_ai'} # <--- Specify the schema here

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<UserData(id={self.id}, name='{self.name}', email='{self.email}')>"
from pydantic import BaseModel
from datetime import datetime

class LLMCacheCreate(BaseModel):
    """Pydantic model for creating a new LLM cache entry."""
    prompt_hash: str
    prompt_text: str
    llm_provider: str
    generated_text: str
    expires_at: datetime | None = None

class LLMCacheRead(BaseModel):
    """Pydantic model for reading an LLM cache entry."""
    id: int
    prompt_hash: str
    prompt_text: str
    llm_provider: str
    generated_text: str
    cached_at: datetime
    expires_at: datetime | None = None

    class Config:
        from_attributes = True # Was orm_mode = True in Pydantic v1

class UserDataCreate(BaseModel):
    """Pydantic model for creating new user data."""
    name: str
    email: str
    is_active: bool = True

class UserDataRead(BaseModel):
    """Pydantic model for reading user data."""
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
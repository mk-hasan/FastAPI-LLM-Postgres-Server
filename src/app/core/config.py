from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    OPENAI_API_KEY: str
    COHERE_API_KEY: str
    HUGGINGFACE_API_KEY: str
    DEFAULT_LLM_PROVIDER: str = "gemini" # Default LLM to use
    GOOGLE_API_KEY: str
    # PostgreSQL Database Connection Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str
    POSTGRES_DATABASE: str

    @property
    def DATABASE_URL(self) -> str:
        """Constructs the database connection URL."""
        return (f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

@lru_cache()
def get_settings():
    """
    Dependency to get cached settings.
    """
    return Settings()
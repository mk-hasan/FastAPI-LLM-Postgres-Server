from fastapi import Depends
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Type
from sqlalchemy.orm import Session
import logging

from app.llm_providers.base import BaseLLMProvider
from app.llm_providers.openai_provider import OpenAIProvider
from app.llm_providers.gemini_provider import GeminiProvider

from app.models.llm_models import LLMResponse, ParsedJobInfo
from app.models.db_models import LLMCacheCreate, LLMCacheRead
from app.db.models import LLMCache as DBLlmcache

from app.core.exceptions import InvalidLLMProviderError, LLMProviderError
from app.core.config import Settings, get_settings
from app.db.database import get_db
from app.utils.web_scraper import fetch_html_content, extract_text_from_html
from app.utils.prompt_manager import get_prompt_manager, PromptManager

logger = logging.getLogger(__name__)

class LLMService:
    # --- CHANGE THIS LINE ---
    def __init__(self, settings: Settings, db: Session, prompt_manager: PromptManager): # <--- Added prompt_manager here
        self.settings = settings
        self.db = db
        self.prompt_manager = prompt_manager # <--- Store it as an instance variable
        # Pass prompt_manager to providers that need it
        self.providers: Dict[str, BaseLLMProvider] = {
            "openai": OpenAIProvider(api_key=settings.OPENAI_API_KEY), # OpenAIProvider doesn't use prompt_manager directly, no need to pass it unless it's designed to.
            "gemini": GeminiProvider(api_key=settings.GOOGLE_API_KEY, prompt_manager=prompt_manager),
            # "cohere": CohereProvider(api_key=settings.COHERE_API_KEY, prompt_manager=prompt_manager),
        }

    def _generate_cache_key(self, prompt: str, llm_provider_name: str, max_tokens: int, temperature: float) -> str:
        """Generates a unique hash for caching based on prompt and parameters."""
        key_string = f"{prompt}-{llm_provider_name}-{max_tokens}-{temperature}"
        return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

    async def generate_response(
        self,
        prompt: str,
        llm_provider_name: str,
        max_tokens: int,
        temperature: float,
        use_cache: bool = True,
        cache_ttl_minutes: int = 60 # Time-to-live for cache
    ) -> LLMResponse:
        # Use the default provider from settings if not explicitly provided in the request
        if not llm_provider_name:
            llm_provider_name = self.settings.DEFAULT_LLM_PROVIDER

        cache_key = self._generate_cache_key(prompt, llm_provider_name, max_tokens, temperature)

        if use_cache:
            # Try to fetch from cache
            cached_result = self.db.query(DBLlmcache).filter(DBLlmcache.prompt_hash == cache_key).first()

            if cached_result and (cached_result.expires_at is None or cached_result.expires_at > datetime.now()):
                return LLMResponse(
                    generated_text=cached_result.generated_text,
                    provider_used=cached_result.llm_provider,
                    tokens_generated=None # Cache doesn't store tokens generated directly
                )
            elif cached_result and cached_result.expires_at <= datetime.now():
                # Cache expired, remove it (optional)
                self.db.delete(cached_result)
                self.db.commit()

        provider = self.providers.get(llm_provider_name.lower())
        if not provider:
            raise InvalidLLMProviderError(llm_provider_name)

        try:
            llm_response = await provider.generate_text(prompt, max_tokens, temperature)

            # Cache the new result
            if use_cache:
                expires_at = datetime.now() + timedelta(minutes=cache_ttl_minutes)
                cache_entry = DBLlmcache(
                    prompt_hash=cache_key,
                    prompt_text=prompt,
                    llm_provider=llm_provider_name,
                    generated_text=llm_response.generated_text,
                    expires_at=expires_at
                )
                self.db.add(cache_entry)
                self.db.commit()
                self.db.refresh(cache_entry)

            return llm_response
        except Exception as e:
            raise LLMProviderError(f"Error during LLM interaction or caching: {e}")

    async def parse_job_url(self, job_url: str, llm_provider_name: str) -> ParsedJobInfo:
        """
        Fetches job description from URL and uses LLM to parse it.
        """
        if not llm_provider_name:
            llm_provider_name = self.settings.DEFAULT_LLM_PROVIDER

        provider = self.providers.get(llm_provider_name.lower())
        if not provider:
            raise InvalidLLMProviderError(llm_provider_name)

        if not hasattr(provider, 'parse_job_description'):
            raise LLMProviderError(f"LLM provider '{llm_provider_name}' does not support job parsing.")

        logger.info(f"Fetching content from: {job_url}")
        try:
            html_content = await fetch_html_content(str(job_url))
            job_description_text = extract_text_from_html(html_content)

            if not job_description_text.strip():
                raise ValueError("Could not extract meaningful text from the job URL.")

            logger.info(f"Parsing job description with {llm_provider_name}")
            parsed_info = await provider.parse_job_description(job_description_text)
            return parsed_info

        except ValueError as e: # Catch errors from web_scraper or text extraction
            raise LLMProviderError(f"Failed to process job URL content: {e}")
        except Exception as e:
            raise LLMProviderError(f"An unexpected error occurred during job URL parsing: {e}")

# Dependency for LLMService (updated to include prompt_manager)
def get_llm_service(
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
    prompt_manager: PromptManager = Depends(get_prompt_manager) # <--- NEW DEPENDENCY
):
    return LLMService(settings, db, prompt_manager) # <--- This call now matches the __init__ signature
from openai import AsyncOpenAI
from app.llm_providers.base import BaseLLMProvider
from app.models.llm_models import LLMResponse
from app.core.exceptions import LLMProviderError
from app.core.config import Settings

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.provider_name = "openai"

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or "gpt-4o", etc.
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            generated_text = response.choices[0].message.content.strip()
            tokens_generated = response.usage.completion_tokens if response.usage else None
            return LLMResponse(
                generated_text=generated_text,
                provider_used=self.provider_name,
                tokens_generated=tokens_generated
            )
        except Exception as e:
            raise LLMProviderError(f"OpenAI API error: {e}")
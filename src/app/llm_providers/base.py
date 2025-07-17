from abc import ABC, abstractmethod
from app.models.llm_models import LLMResponse

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM providers.
    Defines the interface that all LLM integrations must adhere to.
    """

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        """
        Generates text using the specific LLM.

        Args:
            prompt: The input prompt for text generation.
            max_tokens: The maximum number of tokens to generate.
            temperature: The sampling temperature.

        Returns:
            An LLMResponse object containing the generated text and metadata.
        """
        pass
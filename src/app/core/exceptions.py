from fastapi import HTTPException, status

class LLMProviderError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM Provider Error: {detail}")

class InvalidLLMProviderError(HTTPException):
    def __init__(self, provider_name: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid LLM provider: {provider_name}")

class PromptValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Prompt Validation Error: {detail}")
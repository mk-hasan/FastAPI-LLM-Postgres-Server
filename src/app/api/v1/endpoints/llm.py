from fastapi import APIRouter, Depends, status, Body, HTTPException
from app.models.llm_models import PromptRequest, LLMResponse, JobParseRequest, ParsedJobInfo # <--- Import new models
from app.services.llm_service import LLMService, get_llm_service
from app.core.exceptions import PromptValidationError, LLMProviderError, InvalidLLMProviderError

router = APIRouter()

@router.post(
    "/generate",
    response_model=LLMResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate text using an LLM",
    description="Sends a prompt to a specified LLM provider and returns the generated text. "
                "Results are cached in the database.",
    response_description="The generated text and details of the provider used."
)
async def generate_text_endpoint(
    request: PromptRequest = Body(..., alias="request"), # Ensure alias matches body key
    llm_service: LLMService = Depends(get_llm_service),
    use_cache: bool = Body(True, description="Whether to use caching for this request."),
    cache_ttl_minutes: int = Body(60, gt=0, description="Time-to-live for cache in minutes if used.")
) -> LLMResponse:
    """
    Generates text based on the provided prompt and LLM provider.
    """
    if not request.prompt.strip():
        raise PromptValidationError("Prompt cannot be empty.")

    try:
        response = await llm_service.generate_response(
            prompt=request.prompt,
            llm_provider_name=request.llm_provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            use_cache=use_cache,
            cache_ttl_minutes=cache_ttl_minutes
        )
        return response
    except (InvalidLLMProviderError, LLMProviderError) as e:
        raise e
    except Exception as e:
        raise LLMProviderError(f"An unexpected error occurred during LLM interaction or caching: {e}")


@router.post(
    "/parse-job",
    response_model=ParsedJobInfo,
    status_code=status.HTTP_200_OK,
    summary="Parse job description from URL",
    description="Fetches content from a job URL and uses an LLM (Gemini) to extract structured information like title, skills, etc."
)
async def parse_job_url_endpoint(
    request: JobParseRequest, # This time, the entire body maps to JobParseRequest
    llm_service: LLMService = Depends(get_llm_service)
) -> ParsedJobInfo:
    """
    Parses job information from a given URL.

    - **job_url**: The URL of the job posting.
    - **llm_provider**: The LLM provider to use for parsing (defaults to Gemini).
    """
    try:
        parsed_info = await llm_service.parse_job_url(
            job_url=request.job_url,
            llm_provider_name=request.llm_provider
        )
        return parsed_info
    except (LLMProviderError, InvalidLLMProviderError, ValueError) as e:
        # Catch specific errors and re-raise as HTTP exceptions if needed,
        # or let the global handler catch LLMProviderError.
        # For ValueError from web_scraper, converting to 422 or 400 might be appropriate.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")
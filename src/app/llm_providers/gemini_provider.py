import google.generativeai as genai
from app.llm_providers.base import BaseLLMProvider
from app.models.llm_models import LLMResponse, ParsedJobInfo
from app.core.exceptions import LLMProviderError
import json
from app.utils.prompt_manager import get_prompt_manager, PromptManager # <--- NEW IMPORTS
from fastapi import Depends

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, prompt_manager: PromptManager = Depends(get_prompt_manager)): # <--- Pass PromptManager
        if not api_key:
            raise ValueError("Gemini API Key is required for GeminiProvider.")
        genai.configure(api_key=api_key)
        self.provider_name = "gemini"
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.prompt_manager = prompt_manager # Store prompt manager

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> LLMResponse:
        try:
            # Use a template for generic text generation
            templated_prompt = self.prompt_manager.render_prompt(
                "generic_text_generation.jinja2", # Use the template file name
                user_prompt=prompt # Pass variables to the template
            )

            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 1,
                "top_k": 1,
            }

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]

            response = await self.model.generate_content_async(
                templated_prompt, # <--- Use the templated prompt
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                generated_text = ""
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text'):
                        generated_text += part.text
                return LLMResponse(
                    generated_text=generated_text.strip(),
                    provider_used=self.provider_name,
                    tokens_generated=None
                )
            else:
                raise LLMProviderError(f"Gemini API did not return generated text. Prompt feedback: {response.prompt_feedback}")

        except genai.types.BlockedPromptException as e:
            raise LLMProviderError(f"Gemini API blocked prompt due to safety settings: {e}")
        except Exception as e:
            raise LLMProviderError(f"Gemini API error during text generation: {e}")

    async def parse_job_description(self, job_description_text: str) -> ParsedJobInfo:
        """
        Uses Gemini to parse a job description text and extract structured information.
        """
        # Render the job parsing prompt template
        parsing_prompt = self.prompt_manager.render_prompt(
            "job_parser.jinja2", # Use the template file name
            job_description_text=job_description_text # Pass variables to the template
        )

        try:
            generation_config = {
                "max_output_tokens": 1000,
                "temperature": 0.2,
                "top_p": 1,
                "top_k": 1,
            }

            response = await self.model.generate_content_async(
                parsing_prompt, # <--- Use the templated prompt
                generation_config=generation_config
            )

            if not (response.candidates and response.candidates[0].content and response.candidates[0].content.parts):
                 raise LLMProviderError("Gemini API did not return valid content for job parsing.")

            raw_gemini_output = ""
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    raw_gemini_output += part.text

            try:
                cleaned_output = raw_gemini_output.strip()
                if cleaned_output.startswith("```json") and cleaned_output.endswith("```"):
                    cleaned_output = cleaned_output[7:-3].strip()
                elif cleaned_output.startswith("```") and cleaned_output.endswith("```"):
                    cleaned_output = cleaned_output[3:-3].strip()

                parsed_data = json.loads(cleaned_output)
            except json.JSONDecodeError as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to decode JSON from Gemini for job parsing. Raw output: {raw_gemini_output[:500]}... Error: {e}")
                raise LLMProviderError(f"Gemini returned invalid JSON: {e}. Raw: {raw_gemini_output}")

            parsed_job_info = ParsedJobInfo(
                parsed_by_provider=self.provider_name,
                raw_llm_output=raw_gemini_output, # Store raw output for debugging
                **parsed_data # <--- This will now expect 'technical_skills' and 'soft_skills'
            )
            return parsed_job_info

        except genai.types.BlockedPromptException as e:
            raise LLMProviderError(f"Gemini API blocked job parsing prompt due to safety settings: {e}")
        except Exception as e:
            raise LLMProviderError(f"Gemini API error during job parsing: {e}")
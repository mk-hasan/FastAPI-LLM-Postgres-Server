from jinja2 import Environment, FileSystemLoader
import os
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    # ...
    def __init__(self, templates_dir: str = "prompts"):
        current_dir = os.path.dirname(os.path.abspath(__file__)) # app/utils
        # Go up three levels to reach the actual project root where 'prompts' folder sits
        project_root = os.path.join(current_dir, '..', '..') # <--- CHANGED
        self.templates_path = os.path.join(project_root, templates_dir)

        if not os.path.exists(self.templates_path):
            logger.error(f"Prompt templates directory not found: {self.templates_path}")
            raise FileNotFoundError(f"Prompt templates directory not found at {self.templates_path}")

        self.env = Environment(loader=FileSystemLoader(self.templates_path), trim_blocks=True, lstrip_blocks=True)
        logger.info(f"PromptManager initialized. Loading templates from: {self.templates_path}")

    def get_prompt_template(self, template_name: str):
        """
        Loads a Jinja2 template by name (e.g., 'job_parser.jinja2').
        """
        try:
            return self.env.get_template(template_name)
        except Exception as e:
            logger.error(f"Error loading prompt template '{template_name}': {e}")
            raise ValueError(f"Prompt template '{template_name}' not found or invalid: {e}")

    def render_prompt(self, template_name: str, **kwargs) -> str:
        """
        Renders a specific prompt template with provided variables.
        """
        template = self.get_prompt_template(template_name)
        return template.render(**kwargs)

# Singleton instance for easy access
_prompt_manager = PromptManager()

def get_prompt_manager() -> PromptManager:
    """FastAPI dependency to get the PromptManager instance."""
    return _prompt_manager
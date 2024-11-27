import logging

from src.config.models.llm import LLMConfig
from src.llm_handler.openai_handler import OpenAIHandler
from src.llm_handler.ollama_handler import OllamaHandler
from src.llm_handler.anthropic_handler import AnthropicHandler

logger = logging.getLogger('hey-database')

class LLMFactory:
    """Factory per la creazione dei componenti LLM"""
    
    @staticmethod
    def create_handler(config: LLMConfig):
        """Crea l'handler LLM appropriato"""
        try:
            if config.type == 'openai':
                if not config.api_key:
                    raise ValueError("OpenAI API key is required")
                return OpenAIHandler(
                    api_key=config.api_key,
                    chat_model=config.model or "gpt-4o"
                )
            elif config.type == 'anthropic':
                if not config.api_key:
                    raise ValueError("Anthropic API key is required")
                return AnthropicHandler(
                    api_key=config.api_key,
                    chat_model=config.model or "claude-3-sonnet"
                )
            elif config.type == 'ollama':
                return OllamaHandler(
                    base_url=config.base_url or "http://localhost:11434",
                    model=config.model or "llama3.1"
                )
            else:
                raise ValueError(f"LLM type {config.type} not supported")
                
        except Exception as e:
            logger.exception(f"Error creating LLM handler: {e}")
            raise
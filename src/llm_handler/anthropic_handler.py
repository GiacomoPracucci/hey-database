from anthropic import Anthropic
from typing import Union, Generator
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from src.llm_handler.base_llm_handler import BaseLLMHandler

class AnthropicHandler(BaseLLMHandler):
    """Classe per gestire le operazioni con le API di Anthropic/Claude"""

    def __init__(self,
                 api_key: str,
                 chat_model: str = "claude-3-5-sonnet-latest"
                 ) -> None:
        """Initialize Anthropic client and configure models
        
        Args:
            api_key: Anthropic API key
            chat_model: Model name for chat completions (default to Claude 3 Sonnet)
        """
        self.client = Anthropic(api_key=api_key)
        self.chat_model = chat_model
        
    def _serialize_response(self, text: str) -> str:
        """Serializes the response text to ensure consistent formatting
        Args:
            text: Response text to serialize
        Returns:
            Serialized text
        """
        return text.strip()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_completion(self,
                      prompt: str,
                      system_prompt: str = "Sei un assistente utile ed accurato.",
                      temperature: float = 0.2,
                      max_tokens: int = 1000
                      ) -> Union[str, None]:
        """Get completion from Anthropic API
        
        Args:
            prompt: User prompt
            system_prompt: System context for the conversation
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response or None if error occurs
        """
        try:
            response = self.client.messages.create(
                model=self.chat_model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return self._serialize_response(response.content[0].text)
            
        except Exception as e:
            print(f"Errore nella generazione della risposta: {str(e)}")
            return None
        
        
    def get_chat_stream(self,
                       prompt: str,
                       system_prompt: str = "Sei un assistente utile ed accurato.",
                       temperature: float = 0.2
                       ) -> Generator[str, None, None]:
        """Get streaming response from Anthropic API
        
        Args:
            prompt: User prompt
            system_prompt: System context for the conversation
            temperature: Generation temperature
            
        Yields:
            Response chunks as they are generated
        """
        try:
            stream = self.client.messages.create(
                model=self.chat_model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                system=system_prompt,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.content:
                    yield self._serialize_response(chunk.content[0].text)
                    
        except Exception as e:
            print(f"Errore nello streaming della risposta: {str(e)}")
            yield None
from abc import ABC, abstractmethod
from typing import Union, Generator

class BaseLLMHandler(ABC):
    """Base class for LLM handlers that provide unified interface for different LLM providers"""
    
    @abstractmethod
    def get_completion(self,
                      prompt: str,
                      system_prompt: str = "Sei un assistente utile ed accurato.",
                      temperature: float = 0.2,
                      max_tokens: int = 1000
                      ) -> Union[str, None]:
        """Get completion from LLM
        
        Args:
            prompt: User prompt
            system_prompt: System context for the conversation
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response or None if error occurs
        """
        pass
    
    @abstractmethod
    def get_chat_stream(self,
                       prompt: str,
                       system_prompt: str = "Sei un assistente SQL utile ed accurato.",
                       temperature: float = 0.2
                       ) -> Generator[str, None, None]:
        """Get streaming response from LLM
        
        Args:
            prompt: User prompt
            system_prompt: System context
            temperature: Generation temperature
            
        Yields:
            Response chunks as they are generated
        """
        pass
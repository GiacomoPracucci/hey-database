from openai import OpenAI
from typing import Union, List,  Any
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from src.llm_handler.base_llm_handler import LLMHandler

class OpenAIHandler(LLMHandler):
    """Classe per gestire le operazion con le API di OpenAI"""
    
    def __init__(self,
                 api_key: str,
                 chat_model: str = "gpt-4o"
                 ) -> None:
        """Initialize OpenAI client and configure models
        
        Args:
            api_key: OpenAI API key
            chat_model: Model name for chat completions
        """
        
        self.client = OpenAI(api_key=api_key)
        self.chat_model = chat_model

    def _serialize_response(self, obj: Any) -> Any:
        """Serialize objects to JSON-compatible format
        Args:
            obj: Object to serialize
        Returns:
            Serialized object
        """

        if hasattr(obj, 'keys'):  # Se è un dict-like object
            return {key: self._serialize_response(value) for key, value in dict(obj).items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_response(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

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
        """Get completion from OpenAI API"""
            
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return self._serialize_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Errore nella generazione della risposta: {str(e)}")
            return None
        
    def get_chat_stream(self,
                        prompt: str,
                        system_prompt: str = "Sei un assistente utile ed accurato.",
                        temperature: float = 0.2):
        """Get streaming response from OpenAI API"""
        try:
            stream = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield self._serialize_response(chunk.choices[0].delta.content)
                    
        except Exception as e:
            print(f"Errore nello streaming della risposta: {str(e)}")
            yield None
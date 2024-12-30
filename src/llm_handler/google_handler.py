from typing import Generator, Union

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.llm_handler.llm_handler import LLMHandler


class GoogleHandler(LLMHandler):
    """Classe per gestire le operazioni con le API di Google/Gemini"""

    def __init__(
        self,
        api_key: str,
        chat_model: str = "gemini-1.5-flash",
    ) -> None:
        """Initialize Gemini client and configure models

        Args:
            api_key: Gemini API key
            chat_model: Model name for chat completions (default to Gemini 1.5 Flash)
        """

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(chat_model)
        self.chat_model = chat_model

    def _generate_system_prompt(self, system_prompt: str) -> list[dict]:
        """Workaround for Google absence of a system prompt parameter as suggested here https://www.googlecloudcommunity.com/gc/AI-ML/Gemini-Pro-Context-Option/m-p/684704/highlight/true#M4159
        Args:
            system_prompt: System prompt
        Returns:
            Messages history used as system prompt
        """
        return [
            {"role": "user", "parts": [{"text": system_prompt}]},
            {"role": "model", "parts": [{"text": "Understood."}]},
        ]

    def _serialize_response(self, text: str) -> str:
        """Serializes the response text to ensure consistent formatting
        Args:
            text: Response text to serialize
        Returns:
            Serialized text
        """
        return text.strip()

    @retry(
        stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_completion(
        self,
        prompt: str,
        system_prompt: str = "Sei un assistente utile ed accurato.",
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> Union[str, None]:
        """Get completion from Gemini API

        Args:
            prompt: User prompt
            system_prompt: System context for the conversation
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Generated response or None if error occurs
        """
        try:
            chat = self.client.start_chat(
                history=self._generate_system_prompt(system_prompt)
            )
            response = chat.send_message(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                ),
            )
            return self._serialize_response(response.text)

        except Exception as e:
            print(f"Errore nella generazione della risposta: {str(e)}")
            return None

    def get_chat_stream(
        self,
        prompt: str,
        system_prompt: str = "Sei un assistente utile ed accurato.",
        temperature: float = 0.2,
    ) -> Generator[str, None, None]:
        """Get streaming response from Gemini API

        Args:
            prompt: User prompt
            system_prompt: System context for the conversation
            temperature: Generation temperature

        Yields:
            Response chunks as they are generated
        """
        try:
            stream = self.client.start_chat(
                history=self._generate_system_prompt(system_prompt)
                + [{"role": "user", "content": prompt}],
                system=system_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                ),
                stream=True,
            )

            for chunk in stream:
                if chunk.content:
                    yield self._serialize_response(chunk.text)

        except Exception as e:
            print(f"Errore nello streaming della risposta: {str(e)}")
            yield None

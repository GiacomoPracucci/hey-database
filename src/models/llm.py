from dataclasses import dataclass
from typing import Optional
from src.config.languages import SupportedLanguage

@dataclass
class LLMConfig:
    type: str # tipo di modello (huggingface, openai, ollama ...)
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None # parametro opzionale per modelli locali (localhost su cui girano)
    language: SupportedLanguage = SupportedLanguage.get_default()
    
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmbeddingConfig:
    type: str  # huggingface o openai
    model_name: str  
    api_key: Optional[str] = None  # non richiesto per huggingface (local models)
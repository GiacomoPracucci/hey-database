from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    type: str # tipo di database (postgres, snowflake, ecc.)
    host: str
    port: str
    database: str
    user: str
    password: str
    schema: str
    warehouse: Optional[str] = None # parametro opzionale di snowflake
    account: Optional[str] = None # parametro opzionale di snowflake
    role: Optional[str] = None # parametro opzionale di snowflake

@dataclass
class LLMConfig:
    type: str # tipo di modello (huggingface, openai, ollama ...)
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None # parametro opzionale per modelli locali (localhost su cui girano)
    
@dataclass
class PromptConfig:
    include_sample_data: bool = True
    max_sample_rows: int = 3 

@dataclass
class AppConfig:
    database: DatabaseConfig
    llm: LLMConfig
    prompt: PromptConfig
    debug: bool = False
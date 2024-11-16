from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from src.config.languages import SupportedLanguage

# ---------- DB ----------
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

# ---------- LLM ----------
@dataclass
class LLMConfig:
    type: str # tipo di modello (huggingface, openai, ollama ...)
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None # parametro opzionale per modelli locali (localhost su cui girano)
    language: SupportedLanguage = SupportedLanguage.get_default()
    
# --------- EMBEDDING ----------
@dataclass
class EmbeddingConfig:
    type: str  # huggingface o openai
    model_name: str  
    api_key: Optional[str] = None  # non richiesto per huggingface (local models)

# ---------- PROMPT ----------
@dataclass
class PromptConfig:
    include_sample_data: bool = True
    max_sample_rows: int = 3 

# ---------- VECTOR STORE --------- 
@dataclass
class QueryStorePayload:
    """Rappresenta il payload standard per ogni record nel vector store"""
    question: str
    sql_query: str
    explanation: str
    positive_votes: int

@dataclass
class VectorStoreConfig:
    """Configurazione standard per il vector store"""
    enabled: bool
    type: str # qdrant, ecc
    collection_name: str
    path: Optional[str] # path per lo storage locale
    url: Optional[str] # url per server remoto
    embedding: EmbeddingConfig
    api_key: Optional[str] = None
    batch_size: int = 100
    
@dataclass
class SearchResult:
    """Rappresenta un risultato della ricerca in un vectorstore"""
    question: str
    sql_query: str
    explanation: str
    score: float
    positive_votes: int
    
# ---------- CONFIGURAZIONE FINALE APP ----------    
@dataclass
class AppConfig:
    database: DatabaseConfig
    llm: LLMConfig
    prompt: PromptConfig
    vector_store: Optional[VectorStoreConfig] = None
    debug: bool = False
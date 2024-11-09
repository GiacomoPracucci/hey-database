# Configuration System Documentation

## Overview 

The configuration system is designed to provide a flexible and maintainable way to configure different components of the application:

- Database connections
- LLM services
- Embedding models
- Vector stores
- Context retrievers
- General application settings

## Configuration Components

1. Configuration Files Structure
    ```
    src/
    ├── config/
    │   ├── models.py         # Configuration data classes
    │   ├── config_loader.py  # YAML configuration loader
    │   └── factory.py        # Service factory for components
    ├── config.yaml           # Main configuration file
    └── .env                  # Environment variables
    ```

2. Key Components and Their Roles

    `config.yaml`  

    This is the main configuration file where you specify all application settings:  
    ```yaml
    database:
        type: postgres  # or mysql, snowflake
        host: localhost
        port: 5432
        database: postgres
        user: postgres
        password: ${POSTGRES_PWD}
        schema: video_games
        # Optional Snowflake settings:
        # warehouse: compute_wh
        # account: xy12345.eu-central-1
        # role: analyst

    llm:
        type: ollama    # or openai
        base_url: http://localhost:11434
        model: llama3.1
        # For OpenAI:
        # api_key: ${OPENAI_API_KEY}
        # model: gpt-4

    vector_store:
        enabled: true
        type: qdrant
        collection_name: ${db_schema}_store
        path: ./data/${db_schema}_store
        batch_size: 100
        embedding:
            type: huggingface    # or openai
            model_name: sentence-transformers/multi-qa-MiniLM-L6-cos-v1
            # api_key: ${OPENAI_API_KEY}  # required for OpenAI embeddings

    prompt:
        include_sample_data: true
        max_sample_rows: 3

    debug: true
    ```

    `models.py`  
    
    Defines the structure of configuration using dataclasses:  
    ```python
    @dataclass
    class DatabaseConfig:
        type: str
        host: str
        port: str
        database: str
        user: str
        password: str
        schema: str
        warehouse: Optional[str] = None
        account: Optional[str] = None
        role: Optional[str] = None

    @dataclass
    class LLMConfig:
        type: str
        api_key: Optional[str] = None
        model: Optional[str] = None
        base_url: Optional[str] = None

    @dataclass
    class EmbeddingConfig:
        type: str
        model_name: str
        api_key: Optional[str] = None

    @dataclass
    class VectorStoreConfig:
        enabled: bool
        type: str
        collection_name: str
        path: Optional[str]
        url: Optional[str]
        api_key: Optional[str] = None
        batch_size: int = 100
        embedding: EmbeddingConfig

    @dataclass
    class PromptConfig:
        include_sample_data: bool = True
        max_sample_rows: int = 3

    @dataclass
    class AppConfig:
        database: DatabaseConfig
        llm: LLMConfig
        prompt: PromptConfig
        vector_store: Optional[VectorStoreConfig] = None
        debug: bool = False
    ```    
    
    `factory.py` 

    Creates service instances based on configuration:   
    ```python
    class ServiceFactory:
        @staticmethod
        def create_db_connector(config: DatabaseConfig)
            
        @staticmethod
        def create_llm_handler(config: LLMConfig)
            
        @staticmethod
        def create_metadata_retriever(config: DatabaseConfig, db)
            
        @staticmethod
        def create_embedding_model(config: EmbeddingConfig)
            
        @staticmethod
        def create_vector_store(config: VectorStoreConfig)
    ```

## Configuration Features

- **Environment Variables**:  

    - Support for environment variables in configuration using ${VAR_NAME} syntax
    - Automatic loading of .env file
    - Schema-based variable substitution (e.g., ${db_schema})


- **Vector Store Configuration**:  

    - Enable/disable vector store functionality
    - Support for local or remote Qdrant instances
    - Configurable batch size for operations
    - Embedding model selection and configuration
    - Safe handling of embedding model changes


- **Embedding Models**: 

    - Support for multiple embedding providers
    - HuggingFace Sentence Transformers
    - OpenAI Embeddings
    - Automatic dimension handling
    - Version-safe collection naming


- **Prompt Configuration**:  

    - Control over sample data inclusion
    - Configurable number of sample rows
    - Customizable prompt templates
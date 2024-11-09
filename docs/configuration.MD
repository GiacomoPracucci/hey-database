# Configuration System Documentation

## Overview 

The configuration system is designed to provide a flexible and maintainable way to configure different components of the application:

- Database connections
- LLM services
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

    llm:
        type: ollama    # or openai
        base_url: http://localhost:11434
        model: llama2
        # For OpenAI:
        # api_key: ${OPENAI_API_KEY}
        # model: gpt-4

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

    @dataclass
    class LLMConfig:
        type: str
        api_key: Optional[str] = None
        model: Optional[str] = None
        base_url: Optional[str] = None

    @dataclass
    class AppConfig:
        database: DatabaseConfig
        llm: LLMConfig
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
    ```
